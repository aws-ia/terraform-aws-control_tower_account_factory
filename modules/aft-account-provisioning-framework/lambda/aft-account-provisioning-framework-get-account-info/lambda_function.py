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


def get_account_info(payload, session, ct_management_session, logger):
    """
    get_account is keyed from account_id, but account requests are keyed from email
    look for the account id in the control_tower_event, and then the metadata table
    last case look up account id using get_account_by_email() -- the most expensive approach.
    """
    logger.info("Function Start - get_account_info")

    email = payload["account_request"]["id"]
    logger.info("Account Email: " + email)

    account_id = None

    if "account" in payload["control_tower_event"]:
        account_id = payload['control_tower_event']['detail']['serviceEventDetails']['createManagedAccountStatus']['account']['accountId']
        if account_id:
            logger.info(f"Account Id [{account_id}] found in control_tower_event")

    if account_id is None:
        logger.info(f"Querying metadata table emailIndex for [{email}]")
        dynamodb = session.resource("dynamodb")
        metadata_table_name = utils.get_ssm_parameter_value(
            session, utils.SSM_PARAM_AFT_DDB_META_TABLE)
        metadata_table = dynamodb.Table(metadata_table_name)
        result = metadata_table.query(
            IndexName="emailIndex",
            KeyConditionExpression=Key('email').eq(email)
        )
        if result['Items']:
            account_id = result['Items'][0]['id']
            logger.info(f"Account id from metadata table: [{account_id}]")

    if account_id is None:
        logger.info("Account id not found. Running get_account_by_email [EXPENSIVE]")
        account = utils.get_account_by_email(ct_management_session, email)
    else:
        account = {"Id": account_id}
        account = utils.get_account(ct_management_session, account)

    return account


def lambda_handler(event, context):
    logger.info("AFT Account Pprovisioning Framework Get Account Info Handler Start")

    try:
        if event["offline"]:
            return True
    except KeyError:
        pass

    payload = event['payload']
    action = event['action']

    session = boto3.session.Session()
    ct_management_session = utils.get_ct_management_session(session)
    if action == "get_account_info":
        account_info = get_account_info(
            payload, session, ct_management_session, logger)
        return account_info
    else:
        raise BaseException("Incorrect Command Passed to Lambda Function. Input: {action}. Expected: 'get_account_info'")


if __name__ == "__main__":
    event = {}
    example_file = os.path.join(os.path.dirname(__file__), "schema/example_event.json")
    with open(example_file) as json_data:
        event = json.load(json_data)
    lambda_handler(event, None)
