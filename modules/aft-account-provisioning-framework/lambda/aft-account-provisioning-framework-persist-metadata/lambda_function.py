import json
import os

import boto3
import jsonschema
import aft_common.aft_utils as utils
from boto3.dynamodb.conditions import Key


logger = utils.get_logger()


def persist_metadata(payload, account_info, session, logger):
    logger.info("Function Start - persist_metadata")

    account_tags = payload["account_request"]["account_tags"]
    account_customizations_name = payload["account_request"]["account_customizations_name"]
    account_custom_fields = json.loads(payload["account_request"]["custom_fields"])
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
        "account_custom_fields": account_custom_fields,
        "parent_ou": account_info["parent_id"],
        "vcs_information": {},
        "terraform_workspace": {},
    }

    logger.info("Writing item to " + metadata_table_name)
    logger.info(item)

    response = utils.put_ddb_item(session, metadata_table_name, item)

    logger.info(response)
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

    if "offline" in event.keys():
        if event["offline"]:
            session = None
            ct_management_session = None
    else:
        session = boto3.session.Session()
        ct_management_session = utils.get_ct_management_session(session)

    if action == "persist_metadata":
        account_info = payload["account_info"]["account"]
        update_metadata = persist_metadata(payload, account_info, session, logger)
        return update_metadata
    else:
        raise BaseException(
            "Incorrect Command Passed to Lambda Function. Input: {action}. Expected: 'persist_metadata'"
        )


if __name__ == "__main__":
    event = {}
    example_file = os.path.join(os.path.dirname(__file__), "schema/example_event.json")
    with open(example_file) as json_data:
        event = json.load(json_data)
    lambda_handler(event, None)
