import inspect
import json
import os
from typing import Any, Dict, Union

import aft_common.aft_utils as utils
import boto3
from boto3.session import Session

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

    try:
        return_value: str
        role = exec_iam_client.get_role(RoleName=role_name.split("/")[-1])
        logger.info("Role Exists. Exiting")
        return_value = role["Role"]["Arn"]
        return return_value
    except exec_iam_client.exceptions.NoSuchEntityException:
        logger.info("Role not found in account.")
        role = create_role_in_account(session, ct_execution_session, role_name)
        return_value = role
        return return_value


def create_role_in_account(
    session: Session, ct_execution_session: Session, role_name: str
) -> str:
    logger.info("Function Start - create_role_in_account")
    trust_policy_template = os.path.join(
        os.path.dirname(__file__), "iam/trust-policies/aftmanagement.tpl"
    )
    aft_management_account = utils.get_ssm_parameter_value(
        session, utils.SSM_PARAM_ACCOUNT_AFT_MANAGEMENT_ACCOUNT_ID
    )
    with open(trust_policy_template) as trust_policy_file:
        template = trust_policy_file.read()
        template = template.replace("{AftManagementAccount}", aft_management_account)
        assume_role_policy_document = json.loads(template)

    exec_client = ct_execution_session.client("iam")
    logger.info("Creating Role")
    response = exec_client.create_role(
        RoleName=role_name.split("/")[-1],
        AssumeRolePolicyDocument=json.dumps(assume_role_policy_document),
        Description="AFT Execution Role",
        MaxSessionDuration=3600,
        Tags=[
            {"Key": "managed_by", "Value": "AFT"},
        ],
    )
    role = response["Role"]["Arn"]
    logger.info(response)
    logger.info("Attaching Role Policy")
    response = exec_client.attach_role_policy(
        RoleName=role_name.split("/")[-1],
        PolicyArn="arn:aws:iam::aws:policy/AdministratorAccess",
    )
    logger.info(response)
    logger.info("Returning role")
    logger.info(role)
    return_value: str = role
    return return_value


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
