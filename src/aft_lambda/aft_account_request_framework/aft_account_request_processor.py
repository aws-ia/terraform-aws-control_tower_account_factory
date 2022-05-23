# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
import json
from typing import TYPE_CHECKING, Any, Dict

from aft_common import aft_utils as utils
from aft_common import notifications
from aft_common.account_request_framework import (
    create_new_account,
    modify_ct_request_is_valid,
    new_ct_request_is_valid,
    update_existing_account,
)
from aft_common.auth import AuthClient
from boto3.session import Session

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object

logger = utils.get_logger()


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> None:
    session = Session()
    auth = AuthClient()
    try:
        ct_management_session = auth.get_ct_management_session()
        product_id = utils.get_ct_product_id(
            session=session, ct_management_session=ct_management_session
        )
        if utils.product_provisioning_in_progress(
            ct_management_session=ct_management_session,
            product_id=product_id,
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
                            session=session,
                            ct_management_session=ct_management_session,
                            request=sqs_body,
                        )

                elif sqs_body["operation"] == "UPDATE":
                    ct_request_is_valid = modify_ct_request_is_valid(sqs_body)
                    if ct_request_is_valid:
                        update_existing_account(
                            session=session,
                            ct_management_session=ct_management_session,
                            request=sqs_body,
                        )
                else:
                    logger.info("Unknown operation received in message")

                utils.delete_sqs_message(session, sqs_message)
                if not ct_request_is_valid:
                    logger.exception("CT Request is not valid")
                    assert ct_request_is_valid

    except Exception as error:
        notifications.send_lambda_failure_sns_message(
            session=session,
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
