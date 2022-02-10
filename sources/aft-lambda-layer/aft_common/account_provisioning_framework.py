# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
import json
import os
from typing import TYPE_CHECKING, Any, Dict, List, Sequence

import aft_common.aft_utils as utils
import jsonschema
from aft_common.types import AftAccountInfo
from boto3.session import Session

if TYPE_CHECKING:
    from mypy_boto3_iam import IAMClient, IAMServiceResource
    from mypy_boto3_iam.type_defs import CreateRoleResponseTypeDef
    from mypy_boto3_organizations.type_defs import TagTypeDef
else:
    IAMClient = object
    CreateRoleResponseTypeDef = object
    IAMServiceResource = object
    TagTypeDef = object


logger = utils.get_logger()


def get_ct_execution_session(
    aft_management_session: Session, ct_management_session: Session, account_id: str
) -> Session:
    session_name = utils.get_ssm_parameter_value(
        aft_management_session, utils.SSM_PARAM_AFT_SESSION_NAME
    )
    admin_credentials = utils.get_assume_role_credentials(
        ct_management_session,
        utils.build_role_arn(
            ct_management_session, "AWSControlTowerExecution", account_id
        ),
        session_name,
    )

    return utils.get_boto_session(admin_credentials)


def create_aft_execution_role(
    account_info: Dict[str, Any], session: Session, ct_management_session: Session
) -> str:
    logger.info("Function Start - create_aft_execution_role")
    role_name = utils.get_ssm_parameter_value(session, utils.SSM_PARAM_AFT_EXEC_ROLE)
    ct_execution_session = get_ct_execution_session(
        session, ct_management_session, account_info["id"]
    )
    exec_iam_client = ct_execution_session.client("iam")

    role_name = role_name.split("/")[-1]

    try:
        role = exec_iam_client.get_role(RoleName=role_name)
        logger.info("Role Exists. Updating...")
        update_aft_role_trust_policy(session, ct_execution_session, role_name)
        set_role_policy(
            ct_execution_session=ct_execution_session,
            role_name=role_name,
            policy_arn="arn:aws:iam::aws:policy/AdministratorAccess",
        )
        return role["Role"]["Arn"]
    except exec_iam_client.exceptions.NoSuchEntityException:
        logger.info("Role not found in account. Creating...")
        return create_role_in_account(session, ct_execution_session, role_name)


def update_aft_role_trust_policy(
    session: Session, ct_execution_session: Session, role_name: str
) -> None:
    assume_role_policy_document = get_aft_trust_policy_document(session)
    iam_resource: IAMServiceResource = ct_execution_session.resource("iam")
    role = iam_resource.Role(name=role_name)
    role.AssumeRolePolicy().update(PolicyDocument=assume_role_policy_document)


def get_aft_trust_policy_document(session: Session) -> str:
    trust_policy_template = os.path.join(
        os.path.dirname(__file__), "templates/aftmanagement.tpl"
    )
    aft_management_account = utils.get_ssm_parameter_value(
        session, utils.SSM_PARAM_ACCOUNT_AFT_MANAGEMENT_ACCOUNT_ID
    )
    with open(trust_policy_template) as trust_policy_file:
        template = trust_policy_file.read()
        template = template.replace("{AftManagementAccount}", aft_management_account)
        return template


def create_role_in_account(
    session: Session, ct_execution_session: Session, role_name: str
) -> str:
    logger.info("Function Start - create_role_in_account")
    assume_role_policy_document = get_aft_trust_policy_document(session=session)
    exec_client: IAMClient = ct_execution_session.client("iam")
    logger.info("Creating Role")
    response: CreateRoleResponseTypeDef = exec_client.create_role(
        RoleName=role_name.split("/")[-1],
        AssumeRolePolicyDocument=assume_role_policy_document,
        Description="AFT Execution Role",
        MaxSessionDuration=3600,
        Tags=[
            {"Key": "managed_by", "Value": "AFT"},
        ],
    )
    role_arn = response["Role"]["Arn"]
    logger.info(response)
    set_role_policy(
        ct_execution_session=ct_execution_session,
        role_name=role_name,
        policy_arn="arn:aws:iam::aws:policy/AdministratorAccess",
    )
    return role_arn


def set_role_policy(
    ct_execution_session: Session, role_name: str, policy_arn: str
) -> None:
    iam_resource: IAMServiceResource = ct_execution_session.resource("iam")
    role = iam_resource.Role(name=role_name)
    for policy in role.attached_policies.all():
        role.detach_policy(PolicyArn=policy.arn)
    logger.info("Attaching Role Policy")
    role.attach_policy(
        PolicyArn=policy_arn,
    )
    return None


def get_account_info(
    payload: Dict[str, Any], session: Session, ct_management_session: Session
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


AFT_EXEC_ROLE = "AWSAFTExecution"

SSM_PARAMETER_PATH = "/aft/account-request/custom-fields/"


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
