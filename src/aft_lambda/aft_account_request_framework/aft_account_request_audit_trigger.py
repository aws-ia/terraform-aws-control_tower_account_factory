# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
import sys
from typing import Any, Dict, Union

import aft_common.aft_utils as utils
from aft_common.account_request_framework import put_audit_record
from boto3.session import Session

logger = utils.get_logger()


def lambda_handler(event: Dict[str, Any], context: Union[Dict[str, Any], None]) -> None:

    try:
        logger.info("Lambda_handler Event")
        logger.info(event)
        session = Session()

        # validate event
        if "Records" in event:
            response = None
            event_record = event["Records"][0]
            if "eventSource" in event_record:
                if event_record["eventSource"] == "aws:dynamodb":
                    logger.info("DynamoDB Event Record Received")
                    table_name = utils.get_ssm_parameter_value(
                        session, utils.SSM_PARAM_AFT_DDB_AUDIT_TABLE
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
                            session, table_name, image_to_record, event_name
                        )
                    else:
                        logger.info(f"Event Name: {event_name} is unsupported.")
                else:
                    logger.info("Non DynamoDB Event Received")
                    sys.exit(1)
        else:
            logger.info("Unexpected Event Received")

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise
