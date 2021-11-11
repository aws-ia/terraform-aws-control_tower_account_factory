import json
import os

import boto3
import jsonschema
import aft_common.aft_utils as utils
from boto3.dynamodb.conditions import Key


logger = utils.get_logger()


def tag_account(payload, account_info, ct_management_session, logger, rollback):
    logger.info("Start Function - tag_account")
    logger.info(payload)

    tags = payload["account_request"]["account_tags"]
    tag_list = [{"Key": k, "Value": v} for k, v in tags.items()]
    response = utils.tag_org_resource(
        ct_management_session, account_info["id"], tag_list, rollback
    )
    return response


def lambda_handler(event, context):
    logger.info("AFT Account Provisioning Framework Handler Start")

    rollback = None
    try:
        if event["rollback"]:
            rollback = True
    except KeyError:
        pass
    try:
        if event["offline"]:
            return True
    except KeyError:
        pass

    payload = event["payload"]
    action = event["action"]

    session = boto3.session.Session()
    ct_management_session = utils.get_ct_management_session(session)

    if action == "tag_account":
        account_info = payload["account_info"]["account"]
        account_tags = tag_account(payload, account_info, ct_management_session, logger, rollback)
        return account_tags
    else:
        raise BaseException(
            "Incorrect Command Passed to Lambda Function. Input: {action}. Expected: 'tag_account'"
        )


if __name__ == "__main__":
    event = {}
    example_file = os.path.join(os.path.dirname(__file__), "schema/example_event.json")
    with open(example_file) as json_data:
        event = json.load(json_data)
    lambda_handler(event, None)
