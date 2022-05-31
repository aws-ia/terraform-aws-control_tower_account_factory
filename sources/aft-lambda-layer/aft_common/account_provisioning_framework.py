# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import json
import os
import time
from typing import TYPE_CHECKING, Any, Dict, List, Sequence

import aft_common.aft_utils as utils
import jsonschema
from aft_common.auth import AuthClient
from aft_common.types import AftAccountInfo
from boto3.session import Session

if TYPE_CHECKING:
    from mypy_boto3_iam import IAMClient
    from mypy_boto3_organizations.type_defs import TagTypeDef
else:
    IAMClient = object
    CreateRoleResponseTypeDef = object
    IAMServiceResource = object
    TagTypeDef = object


logger = utils.get_logger()


AFT_EXEC_ROLE = "AWSAFTExecution"

SSM_PARAMETER_PATH = "/aft/account-request/custom-fields/"


class ProvisionRoles:
    ADMINISTRATOR_ACCESS_MANAGED_POLICY_ARN = (
        "arn:aws:iam::aws:policy/AdministratorAccess"
    )
    SERVICE_ROLE_NAME = "AWSAFTService"

    def __init__(self, auth: AuthClient, account_id: str) -> None:
        self.auth = auth
        self.target_account_id = account_id

    def generate_aft_trust_policy(self) -> str:
        return json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": f"arn:aws:iam::{self.auth.aft_management_account_id}:assumed-role/AWSAFTAdmin/AWSAFT-Session"
                        },
                        "Action": "sts:AssumeRole",
                    }
                ],
            }
        )

    def _deploy_role_in_target_account(
        self, role_name: str, trust_policy: str, policy_arn: str
    ) -> None:
        """
        Since we're creating the AFT roles in the account, we must assume
        AWSControlTowerExecution as the target role. Since this role only
        trusts federation from the CT Management account, we pass a hub session
        that has already been federated into the CT Management account
        """
        ct_mgmt_session = self.auth.get_ct_management_session(
            role_name=ProvisionRoles.SERVICE_ROLE_NAME
        )
        ct_mgmt_acc_id = ct_mgmt_session.client("sts").get_caller_identity()["Account"]
        if self.target_account_id == ct_mgmt_acc_id:
            target_account_session = ct_mgmt_session
        else:
            target_account_session = self.auth.get_target_account_session(
                account_id=self.target_account_id,
                hub_session=ct_mgmt_session,
                role_name=AuthClient.CONTROL_TOWER_EXECUTION_ROLE_NAME,
            )
        client: IAMClient = target_account_session.client("iam")
        try:
            client.get_role(RoleName=role_name)
            client.update_assume_role_policy(
                RoleName=role_name, PolicyDocument=trust_policy
            )

        except client.exceptions.NoSuchEntityException:
            logger.info(f"Creating {role_name} in {self.target_account_id}")
            client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=trust_policy,
                Description="Role for use with Account Factory for Terraform",
                MaxSessionDuration=3600,
                Tags=[{"Key": "managed_by", "Value": "AFT"}],
            )
            eventual_consistency_sleep = 60
            logger.info(
                f"Sleeping for {eventual_consistency_sleep}s to ensure Role exists"
            )
            time.sleep(eventual_consistency_sleep)

        client.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)

    def deploy_aws_aft_execution_role(self) -> None:
        aft_execution_role_name = utils.get_ssm_parameter_value(
            session=self.auth.get_aft_management_session(),
            param=AuthClient.SSM_PARAM_AFT_EXEC_ROLE_NAME,
        )
        # Account for paths
        aft_execution_role_name = aft_execution_role_name.split("/")[-1]
        trust_policy = self.generate_aft_trust_policy()
        self._deploy_role_in_target_account(
            role_name=aft_execution_role_name,
            trust_policy=trust_policy,
            policy_arn=ProvisionRoles.ADMINISTRATOR_ACCESS_MANAGED_POLICY_ARN,
        )

    def deploy_aws_aft_service_role(self) -> None:
        trust_policy = self.generate_aft_trust_policy()
        self._deploy_role_in_target_account(
            role_name=ProvisionRoles.SERVICE_ROLE_NAME,
            trust_policy=trust_policy,
            policy_arn=ProvisionRoles.ADMINISTRATOR_ACCESS_MANAGED_POLICY_ARN,
        )


def get_account_info(
    payload: Dict[str, Any], ct_management_session: Session
) -> AftAccountInfo:
    logger.info("Function Start - get_account_info")

    account_id = None

    # Handle a Control Tower Event
    if "account" in payload["control_tower_event"]:
        if (
            payload["control_tower_event"]["detail"]["eventName"]
            == "CreateManagedAccount"
        ):
            account_id = payload["control_tower_event"]["detail"][
                "serviceEventDetails"
            ]["createManagedAccountStatus"]["account"]["accountId"]
        elif (
            payload["control_tower_event"]["detail"]["eventName"]
            == "UpdateManagedAccount"
        ):
            account_id = payload["control_tower_event"]["detail"][
                "serviceEventDetails"
            ]["updateManagedAccountStatus"]["account"]["accountId"]
        if account_id:
            logger.info(f"Account Id [{account_id}] found in control_tower_event")
            return utils.get_account_info(ct_management_session, account_id)

    elif "id" in payload["account_request"]:
        email = payload["account_request"]["id"]
        logger.info("Account Email: " + email)
        account_id = utils.get_account_id_from_email(ct_management_session, email)
        return utils.get_account_info(ct_management_session, account_id)

    raise Exception("Account was not found")


# From persist-metadata Lambda
def persist_metadata(
    payload: Dict[str, Any], account_info: Dict[str, str], session: Session
) -> Dict[str, Any]:

    logger.info("Function Start - persist_metadata")

    account_tags = payload["account_request"]["account_tags"]
    account_customizations_name = payload["account_request"][
        "account_customizations_name"
    ]
    metadata_table_name = utils.get_ssm_parameter_value(
        session, utils.SSM_PARAM_AFT_DDB_META_TABLE
    )

    item = {
        "id": account_info["id"],
        "email": account_info["email"],
        "account_name": account_info["name"],
        "account_creation_time": account_info["joined_date"],
        "account_status": account_info["status"],
        "account_level_tags": account_tags,
        "account_customizations_name": account_customizations_name,
        "parent_ou": account_info["parent_id"],
        "vcs_information": {},
        "terraform_workspace": {},
    }

    logger.info("Writing item to " + metadata_table_name)
    logger.info(item)

    response = utils.put_ddb_item(session, metadata_table_name, item)

    logger.info(response)
    return response


def get_ssm_parameters_names_by_path(session: Session, path: str) -> List[str]:

    client = session.client("ssm")
    response = client.get_parameters_by_path(Path=path, Recursive=True)
    logger.debug(response)

    parameter_names = []
    for p in response["Parameters"]:
        parameter_names.append(p["Name"])

    return parameter_names


def delete_ssm_parameters(session: Session, parameters: Sequence[str]) -> None:

    if len(parameters) > 0:
        client = session.client("ssm")
        response = client.delete_parameters(Names=parameters)
        logger.info(response)


def create_ssm_parameters(session: Session, parameters: Dict[str, str]) -> None:

    client = session.client("ssm")

    for key, value in parameters.items():
        response = client.put_parameter(
            Name=SSM_PARAMETER_PATH + key, Value=value, Type="String", Overwrite=True
        )
        logger.info(response)


def tag_account(
    payload: Dict[str, Any],
    account_info: Dict[str, str],
    ct_management_session: Session,
    rollback: bool,
) -> None:
    logger.info("Start Function - tag_account")
    logger.info(payload)

    tags = payload["account_request"]["account_tags"]
    tag_list: List[TagTypeDef] = [{"Key": k, "Value": v} for k, v in tags.items()]
    utils.tag_org_resource(
        ct_management_session, account_info["id"], tag_list, rollback
    )


def validate_request(payload: Dict[str, Any]) -> bool:
    logger.info("Function Start - validate_request")
    schema_path = os.path.join(
        os.path.dirname(__file__), "schemas/valid_account_request_schema.json"
    )
    with open(schema_path) as schema_file:
        schema_object = json.load(schema_file)
    logger.info("Schema Loaded:" + json.dumps(schema_object))
    validated = jsonschema.validate(payload, schema_object)
    if validated is None:
        logger.info("Request Validated")
        return True
    else:
        raise Exception("Failure validating request.\n{validated}")
