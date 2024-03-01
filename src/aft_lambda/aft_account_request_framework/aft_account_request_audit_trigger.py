# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
import logging
import sys
from typing import TYPE_CHECKING, Any, Dict

from aft_common import constants as utils
from aft_common import notifications, ssm
from aft_common.account_request_framework import put_audit_record
from aft_common.logger import configure_aft_logger
from boto3.session import Session

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object

configure_aft_logger()
logger = logging.getLogger("aft")


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> None:
    aft_management_session = Session()
    try:
        # validate event
        if "Records" in event:
            response = None
            event_record = event["Records"][0]
            if "eventSource" in event_record:
                if event_record["eventSource"] == "aws:dynamodb":
                    logger.info("DynamoDB Event Record Received")
                    table_name = ssm.get_ssm_parameter_value(
                        aft_management_session, utils.SSM_PARAM_AFT_DDB_AUDIT_TABLE
                    )
                    event_name = event_record["eventName"]

                    supported_events = {"INSERT", "MODIFY", "REMOVE"}

                    image_key_name = (
                        "OldImage" if event_name == "REMOVE" else "NewImage"
                    )
                    image_to_record = event_record["dynamodb"][image_key_name]

                    if event_name in supported_events:
                        logger.info("Event Name: " + event_name)
                        response = put_audit_record(
                            aft_management_session,
                            table_name,
                            image_to_record,
                            event_name,
                        )
                    else:
                        logger.info(f"Event Name: {event_name} is unsupported.")
                else:
                    raise Exception("Non DynamoDB Event Received")
        else:
            logger.info("Unexpected Event Received")

    except Exception as error:
        notifications.send_lambda_failure_sns_message(
            session=aft_management_session,
            message=str(error),
            context=context,
            subject="AFT account request failed",
        )
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(error),
        }
        logger.exception(message)
        raise
