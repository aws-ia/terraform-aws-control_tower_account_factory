import json
import os

import boto3
import jsonschema
import aft_common.aft_utils as utils
from boto3.dynamodb.conditions import Key


logger = utils.get_logger()


def get_ct_execution_session(aft_management_session, ct_management_session, account_id):
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


def persist_metadata(payload, account_info, session, logger):
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
        payload, account_info, session, ct_management_session, logger
):
    logger.info("Function Start - create_aft_execution_role")
    role_name = utils.get_ssm_parameter_value(session, utils.SSM_PARAM_AFT_EXEC_ROLE)
    ct_execution_session = get_ct_execution_session(
        session, ct_management_session, account_info["id"]
    )
    exec_iam_client = ct_execution_session.client("iam")

    try:
        role = exec_iam_client.get_role(RoleName=role_name.split("/")[-1])
        if role:
            logger.info("Role Exists. Exiting")
            return role["Role"]["Arn"]
    except exec_iam_client.exceptions.NoSuchEntityException:
        logger.info("Role not found in account.")
        role = create_role_in_account(session, ct_execution_session, role_name)
        return role


def create_role_in_account(session, ct_execution_session, role_name):
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
    return role


def lambda_handler(event, context):
    logger.info("AFT Account Provisioning Framework Create Role Handler Start")
    try:
        if event["offline"]:
            return True
    except KeyError:
        pass


    payload = event["payload"]
    action = event["action"]

    session = boto3.session.Session()
    ct_management_session = utils.get_ct_management_session(session)

    if action == "create_role":
        account_info = payload["account_info"]["account"]
        aft_role = create_aft_execution_role(
            payload, account_info, session, ct_management_session, logger
        )
        return aft_role
    else:
        raise BaseException(
            "Incorrect Command Passed to Lambda Function. Input: {action}. Expected: 'create_role'"
        )


if __name__ == "__main__":
    event = {}
    example_file = os.path.join(os.path.dirname(__file__), "schema/example_event.json")
    with open(example_file) as json_data:
        event = json.load(json_data)
    lambda_handler(event, None)
