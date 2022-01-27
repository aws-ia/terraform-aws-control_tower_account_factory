import inspect
import json
from typing import Any, Dict, Union

import aft_common.aft_utils as utils
import boto3
from aft_common.account import Account
from boto3.session import Session

logger = utils.get_logger()


def new_account_request(record: Dict[str, Any]) -> bool:
    ct_management_session = utils.get_ct_management_session(aft_mgmt_session=Session())
    account_name = utils.unmarshal_ddb_item(record["dynamodb"]["NewImage"])[
        "control_tower_parameters"
    ]["AccountName"]
    provisioned_product = Account(
        ct_management_session=ct_management_session, account_name=account_name
    ).provisioned_product
    return provisioned_product is None


def delete_account_request(record: Dict[str, Any]) -> bool:
    if record["eventName"] == "REMOVE":
        return True
    return False


def control_tower_param_changed(record: Dict[str, Any]) -> bool:
    if record["eventName"] == "MODIFY":
        old_image = utils.unmarshal_ddb_item(record["dynamodb"]["OldImage"])[
            "control_tower_parameters"
        ]
        new_image = utils.unmarshal_ddb_item(record["dynamodb"]["NewImage"])[
            "control_tower_parameters"
        ]

        if old_image != new_image:
            return True
    return False


def build_sqs_message(record: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Building SQS Message - ")
    message = {}
    operation = record["eventName"]

    new_image = utils.unmarshal_ddb_item(record["dynamodb"]["NewImage"])
    message["operation"] = operation
    message["control_tower_parameters"] = new_image["control_tower_parameters"]

    if operation == "MODIFY":
        old_image = utils.unmarshal_ddb_item(record["dynamodb"]["OldImage"])
        message["old_control_tower_parameters"] = old_image["control_tower_parameters"]

    logger.info(message)
    return message


def build_aft_account_provisioning_framework_event(
    record: Dict[str, Any]
) -> Dict[str, Any]:
    account_request = utils.unmarshal_ddb_item(record["dynamodb"]["NewImage"])
    aft_account_provisioning_framework_event = {
        "account_request": account_request,
        "control_tower_event": {},
    }
    logger.info(aft_account_provisioning_framework_event)
    return aft_account_provisioning_framework_event


def lambda_handler(event: Dict[str, Any], context: Union[Dict[str, Any], None]) -> None:

    try:
        logger.info("Lambda_handler Event")
        logger.info(event)
        session = boto3.session.Session()

        # validate event
        if "Records" not in event:
            return None
        event_record = event["Records"][0]
        if "eventSource" not in event_record:
            return None
        if event_record["eventSource"] != "aws:dynamodb":
            return None

        logger.info("DynamoDB Event Record Received")
        if delete_account_request(event_record):
            # Terraform handles removing the request record from DynamoDB
            # AWS does not support automated deletion of accounts
            logger.info("Delete account request received")
            return None

        new_account = new_account_request(event_record)
        if new_account:
            logger.info("New account request received")
            sqs_queue = utils.get_ssm_parameter_value(
                session, utils.SSM_PARAM_ACCOUNT_REQUEST_QUEUE
            )
            sqs_queue = utils.build_sqs_url(session, sqs_queue)
            message = build_sqs_message(event_record)
            utils.send_sqs_message(session, sqs_queue, message)
        else:
            logger.info("Modify account request received")
            if control_tower_param_changed(event_record):
                logger.info("Control Tower Parameter Update Request Received")
                sqs_queue = utils.get_ssm_parameter_value(
                    session, utils.SSM_PARAM_ACCOUNT_REQUEST_QUEUE
                )
                sqs_queue = utils.build_sqs_url(session, sqs_queue)
                message = build_sqs_message(event_record)
                utils.send_sqs_message(session, sqs_queue, message)
            else:
                logger.info("NON-Control Tower Parameter Update Request Received")
                payload = build_aft_account_provisioning_framework_event(event_record)
                lambda_name = utils.get_ssm_parameter_value(
                    session,
                    utils.SSM_PARAM_AFT_ACCOUNT_PROVISIONING_FRAMEWORK_LAMBDA,
                )
                utils.invoke_lambda(session, lambda_name, json.dumps(payload).encode())

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
