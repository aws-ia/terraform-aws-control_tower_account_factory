import inspect
import json
from typing import Any, Dict, Union

import aft_common.aft_utils as utils
from aft_common.account_request_framework import (
    build_aft_account_provisioning_framework_event,
    build_sqs_message,
    control_tower_param_changed,
    delete_account_request,
    new_account_request,
)
from boto3.session import Session

logger = utils.get_logger()


def lambda_handler(event: Dict[str, Any], context: Union[Dict[str, Any], None]) -> None:

    try:
        logger.info("Lambda_handler Event")
        logger.info(event)
        session = Session()

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
