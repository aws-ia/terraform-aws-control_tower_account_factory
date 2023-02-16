# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import json
import logging
import time
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Dict, List, Sequence

import aft_common.aft_utils as utils
from aft_common import ddb
from aft_common.auth import AuthClient
from aft_common.organizations import OrganizationsAgent
from boto3.session import Session
from botocore.exceptions import ClientError

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.type_defs import PutItemOutputTableTypeDef
    from mypy_boto3_iam import IAMClient, IAMServiceResource
    from mypy_boto3_organizations.type_defs import TagTypeDef
else:
    PutItemOutputTableTypeDef = object
    IAMClient = object
    CreateRoleResponseTypeDef = object
    IAMServiceResource = object
    TagTypeDef = object


logger = logging.getLogger("aft")


AFT_EXEC_ROLE = "AWSAFTExecution"

SSM_PARAMETER_PATH = "/aft/account-request/custom-fields/"


class ProvisionRoles:

    SERVICE_ROLE_NAME = "AWSAFTService"
    EXECUTION_ROLE_NAME = "AWSAFTExecution"

    def __init__(self, auth: AuthClient, account_id: str) -> None:
        self.auth = auth
        self.target_account_id = account_id

        temp_session = self.auth.get_ct_management_session()
        self.partition = utils.get_aws_partition(temp_session)

        self.ADMINISTRATOR_ACCESS_MANAGED_POLICY_ARN = (
            f"arn:{self.partition}:iam::aws:policy/AdministratorAccess"
        )

    def generate_aft_trust_policy(self) -> str:
        return json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": [
                                # TODO: Do we still need role/AWSAFTAdmin
                                f"arn:{self.partition}:iam::{self.auth.aft_management_account_id}:role/AWSAFTAdmin",
                                f"arn:{self.partition}:sts::{self.auth.aft_management_account_id}:assumed-role/AWSAFTAdmin/AWSAFT-Session",
                            ]
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
        self._put_role(
            target_account_session=target_account_session,
            role_name=role_name,
            trust_policy=trust_policy,
        )
        self._put_policy_on_role(
            target_account_session=target_account_session,
            role_name=role_name,
            policy_arn=policy_arn,
        )

    def _put_role(
        self,
        target_account_session: Session,
        role_name: str,
        trust_policy: str,
        max_attempts: int = 20,
        delay: int = 5,
    ) -> None:
        client: IAMClient = target_account_session.client("iam")
        if self.role_exists(
            role_name=role_name, target_account_session=target_account_session
        ):
            client.update_assume_role_policy(
                RoleName=role_name, PolicyDocument=trust_policy
            )
        else:
            client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=trust_policy,
                Description="Role for use with Account Factory for Terraform",
                MaxSessionDuration=3600,
                Tags=[{"Key": "managed_by", "Value": "AFT"}],
            )
            waiter = client.get_waiter("role_exists")
            waiter.wait(
                RoleName=role_name,
                WaiterConfig={"Delay": delay, "MaxAttempts": max_attempts},
            )

    @staticmethod
    def role_exists(role_name: str, target_account_session: Session) -> bool:
        client: IAMClient = target_account_session.client("iam")
        try:
            client.get_role(RoleName=role_name)
            return True

        except ClientError as error:
            if error.response["Error"]["Code"] == "NoSuchEntity":
                return False
            raise

    def _put_policy_on_role(
        self,
        target_account_session: Session,
        role_name: str,
        policy_arn: str,
        delay: int = 5,
        timeout_in_mins: int = 1,
    ) -> None:
        if not self.role_policy_is_attached(
            role_name=role_name,
            policy_arn=policy_arn,
            target_account_session=target_account_session,
        ):
            resource: IAMServiceResource = target_account_session.resource("iam")
            role = resource.Role(role_name)
            role.attach_policy(PolicyArn=policy_arn)
            timeout = datetime.utcnow() + timedelta(minutes=timeout_in_mins)
            while datetime.utcnow() < timeout:
                time.sleep(delay)
                if self.role_policy_is_attached(
                    role_name=role_name,
                    policy_arn=policy_arn,
                    target_account_session=target_account_session,
                ):
                    return None
        return None

    @staticmethod
    def role_policy_is_attached(
        role_name: str, policy_arn: str, target_account_session: Session
    ) -> bool:
        logger.info("Determining if {policy_arn} is attached to {role_name}")
        resource: IAMServiceResource = target_account_session.resource("iam")
        role = resource.Role(role_name)
        policy_iterator = role.attached_policies.all()
        policy_arns = [policy.arn for policy in policy_iterator]
        attached = policy_arn in policy_arns
        logger.info(
            f"{policy_arn} is {'attached' if attached else 'detached'} to {role_name}"
        )
        return attached

    def _ensure_role_can_be_assumed(
        self, role_name: str, timeout_in_mins: int = 1, delay: int = 5
    ) -> None:
        timeout = datetime.utcnow() + timedelta(minutes=timeout_in_mins)
        while datetime.utcnow() < timeout:
            if self._can_assume_role(role_name=role_name):
                return None
            time.sleep(delay)
        raise TimeoutError(
            f"Could not assume role {role_name} within {timeout_in_mins} minutes"
        )

    def _can_assume_role(self, role_name: str) -> bool:
        try:
            self.auth.get_target_account_session(
                account_id=self.target_account_id, role_name=role_name
            )
            return True
        except ClientError:
            return False

    def deploy_aws_aft_roles(self) -> None:
        trust_policy = self.generate_aft_trust_policy()

        aft_role_names = [
            ProvisionRoles.SERVICE_ROLE_NAME,
            ProvisionRoles.EXECUTION_ROLE_NAME,
        ]

        logger.info(f"Deploying roles {', '.join(aft_role_names)}")
        for role_name in aft_role_names:
            self._deploy_role_in_target_account(
                role_name=role_name,
                trust_policy=trust_policy,
                policy_arn=self.ADMINISTRATOR_ACCESS_MANAGED_POLICY_ARN,
            )
            logger.info(f"Deployed {role_name} role")

        for role_name in aft_role_names:
            self._ensure_role_can_be_assumed(role_name=role_name)
            logger.info(f"Can assume {role_name} role")


# From persist-metadata Lambda
def persist_metadata(
    payload: Dict[str, Any], account_info: Dict[str, str], session: Session
) -> PutItemOutputTableTypeDef:

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

    response = ddb.put_ddb_item(session, metadata_table_name, item)

    logger.info(response)
    return response


def get_ssm_parameters_names_by_path(session: Session, path: str) -> List[str]:

    client = session.client("ssm")
    paginator = client.get_paginator("get_parameters_by_path")
    pages = paginator.paginate(Path=path, Recursive=True)

    parameter_names = []
    for page in pages:
        parameter_names.extend([param["Name"] for param in page["Parameters"]])

    return parameter_names


def delete_ssm_parameters(session: Session, parameters: Sequence[str]) -> None:
    batches = utils.yield_batches_from_list(
        parameters, batch_size=10
    )  # Max batch size for API
    for batched_names in batches:
        client = session.client("ssm")
        response = client.delete_parameters(Names=batched_names)


def put_ssm_parameters(session: Session, parameters: Dict[str, str]) -> None:

    client = session.client("ssm")

    for key, value in parameters.items():
        response = client.put_parameter(
            Name=SSM_PARAMETER_PATH + key, Value=value, Type="String", Overwrite=True
        )


def tag_account(
    payload: Dict[str, Any],
    account_info: Dict[str, str],
    ct_management_session: Session,
    rollback: bool,
) -> None:
    logger.info(payload)

    tags = payload["account_request"]["account_tags"]
    tag_list: List[TagTypeDef] = [{"Key": k, "Value": v} for k, v in tags.items()]

    orgs_agent = OrganizationsAgent(ct_management_session)
    orgs_agent.tag_org_resource(account_info["id"], tag_list, rollback)
