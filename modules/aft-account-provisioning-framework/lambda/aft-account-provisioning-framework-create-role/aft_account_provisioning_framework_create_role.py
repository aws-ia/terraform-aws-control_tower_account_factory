import inspect
import json
import os
from typing import TYPE_CHECKING, Any, Dict, Union

import aft_common.aft_utils as utils
import boto3
from boto3.session import Session

if TYPE_CHECKING:
    from mypy_boto3_iam import IAMClient, IAMServiceResource
    from mypy_boto3_iam.type_defs import CreateRoleResponseTypeDef
else:
    IAMClient = object
    CreateRoleResponseTypeDef = object
    IAMServiceResource = object


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


def persist_metadata(
    payload: Dict[str, Any], account_info: Dict[str, Any], session: Session
) -> Dict[str, Any]:
    logger.info("Function Start - persist_metadata")

    account_tags = payload["account_request"]["account_tags"]

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
        "parent_ou": account_info["parent_id"],
        "vcs_information": {},
        "terraform_workspace": {},
    }

    logger.info("Writing item to " + metadata_table_name)
    logger.info(item)

    response = utils.put_ddb_item(session, metadata_table_name, item)

    logger.info(response)
    return response


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
        os.path.dirname(__file__), "iam/trust-policies/aftmanagement.tpl"
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


def lambda_handler(event: Dict[str, Any], context: Union[Dict[str, Any], None]) -> str:
    try:
        logger.info("AFT Account Provisioning Framework Create Role Handler Start")

        payload = event["payload"]
        action = event["action"]

        session = boto3.session.Session()
        ct_management_session = utils.get_ct_management_session(session)

        if action == "create_role":
            account_info = payload["account_info"]["account"]
            aft_role = create_aft_execution_role(
                account_info, session, ct_management_session
            )
            return_value: str = aft_role
            return return_value
        else:
            raise Exception(
                "Incorrect Command Passed to Lambda Function. Input: {action}. Expected: 'create_role'"
            )

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


if __name__ == "__main__":
    import json
    import sys
    from optparse import OptionParser

    logger.info("Local Execution")
    parser = OptionParser()
    parser.add_option(
        "-f", "--event-file", dest="event_file", help="Event file to be processed"
    )
    (options, args) = parser.parse_args(sys.argv)
    if options.event_file is not None:
        with open(options.event_file) as json_data:
            event = json.load(json_data)
            lambda_handler(event, None)
    else:
        lambda_handler({}, None)
