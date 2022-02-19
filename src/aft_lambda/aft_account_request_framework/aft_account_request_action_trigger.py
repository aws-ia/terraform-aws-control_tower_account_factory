# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
import json
from typing import Any, Dict, Union

import aft_common.aft_utils as utils
from aft_common.account_request_framework import (
    build_aft_account_provisioning_framework_event,
    control_tower_param_changed,
    delete_account_request,
    insert_msg_into_acc_req_queue,
    provisioned_product_exists,
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

        new_account = not provisioned_product_exists(event_record)
        control_tower_updates = control_tower_param_changed(event_record)

        if new_account:
            logger.info("New account request received")
            insert_msg_into_acc_req_queue(
                event_record=event_record, new_account=True, session=session
            )
        elif not new_account and control_tower_updates:
            logger.info("Modify account request received")
            logger.info("Control Tower Parameter Update Request Received")
            insert_msg_into_acc_req_queue(
                event_record=event_record, new_account=False, session=session
            )
        elif not new_account and not control_tower_updates:
            logger.info("NON-Control Tower Parameter Update Request Received")
            payload = build_aft_account_provisioning_framework_event(event_record)
            lambda_name = utils.get_ssm_parameter_value(
                session,
                utils.SSM_PARAM_AFT_ACCOUNT_PROVISIONING_FRAMEWORK_LAMBDA,
            )
            utils.invoke_lambda(session, lambda_name, json.dumps(payload).encode())
        else:
            raise Exception("Unsupported account request")

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise
