# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
from typing import TYPE_CHECKING, Any, Dict

from aft_common import notifications
from aft_common.account_provisioning_framework import persist_metadata
from aft_common.logger import customization_request_logger
from boto3.session import Session

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
    from mypy_boto3_dynamodb.type_defs import PutItemOutputTableTypeDef
else:
    PutItemOutputTableTypeDef = object
    LambdaContext = object


def lambda_handler(
    event: Dict[str, Any], context: LambdaContext
) -> PutItemOutputTableTypeDef:
    action = event["action"]
    event_payload = event["payload"]
    request_id = event_payload["customization_request_id"]
    account_info = event_payload["account_info"]["account"]
    target_account_id = event_payload["account_info"]["account"]["id"]
    logger = customization_request_logger(
        aws_account_id=target_account_id, customization_request_id=request_id
    )

    aft_management_session = Session()
    try:
        rollback = None

        try:
            if event["rollback"]:
                rollback = True
        except KeyError:
            pass

        if action == "persist_metadata":
            logger.info(f"Managing AFT metadata table entry for target account")
            update_metadata = persist_metadata(
                event_payload, account_info, aft_management_session
            )
            return update_metadata
        else:
            raise Exception(
                f"Incorrect Command Passed to Lambda Function. Input action: {action}. Expected: 'persist_metadata'"
            )

    except Exception as error:
        notifications.send_lambda_failure_sns_message(
            session=aft_management_session,
            message=str(error),
            context=context,
            subject="AFT account provisioning failed",
        )
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(error),
        }
        logger.exception(message)
        raise
