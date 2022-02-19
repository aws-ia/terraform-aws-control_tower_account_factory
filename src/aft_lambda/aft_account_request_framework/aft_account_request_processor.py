# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
import json
from typing import Any, Dict, Union

from aft_common import aft_utils as utils
from aft_common.account_request_framework import (
    create_new_account,
    modify_ct_request_is_valid,
    new_ct_request_is_valid,
    update_existing_account,
)
from boto3.session import Session

logger = utils.get_logger()


def lambda_handler(event: Dict[str, Any], context: Union[Dict[str, Any], None]) -> None:

    try:
        logger.info("Lambda_handler Event")
        logger.info(event)

        session = Session()
        ct_management_session = utils.get_ct_management_session(session)

        if utils.product_provisioning_in_progress(
            ct_management_session,
            utils.get_ct_product_id(session, ct_management_session),
        ):
            logger.info("Exiting due to provisioning in progress")
            return None
        else:
            sqs_message = utils.receive_sqs_message(
                session,
                utils.get_ssm_parameter_value(
                    session, utils.SSM_PARAM_ACCOUNT_REQUEST_QUEUE
                ),
            )
            if sqs_message is not None:
                sqs_body = json.loads(sqs_message["Body"])
                ct_request_is_valid = True
                if sqs_body["operation"] == "ADD":
                    ct_request_is_valid = new_ct_request_is_valid(
                        ct_management_session, sqs_body
                    )
                    if ct_request_is_valid:
                        response = create_new_account(
                            session, ct_management_session, sqs_body
                        )
                elif sqs_body["operation"] == "UPDATE":
                    ct_request_is_valid = modify_ct_request_is_valid(sqs_body)
                    if ct_request_is_valid:
                        update_existing_account(
                            session, ct_management_session, sqs_body
                        )
                else:
                    logger.info("Unknown operation received in message")

                utils.delete_sqs_message(session, sqs_message)
                if not ct_request_is_valid:
                    logger.exception("CT Request is not valid")
                    assert ct_request_is_valid

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise
