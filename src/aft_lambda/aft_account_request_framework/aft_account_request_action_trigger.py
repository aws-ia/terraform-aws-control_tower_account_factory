# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
import logging
from typing import TYPE_CHECKING, Any, Dict

from aft_common import notifications
from aft_common.account_request_framework import (
    control_tower_param_changed,
    provisioned_product_exists,
)
from aft_common.account_request_record_handler import AccountRequestRecordHandler
from aft_common.auth import AuthClient
from aft_common.logger import configure_aft_logger
from aft_common.shared_account import shared_account_request

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object


configure_aft_logger()
logger = logging.getLogger("aft")


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> None:
    auth = AuthClient()
    try:
        record_handler = AccountRequestRecordHandler(auth=auth, event=event)
        logger.info(record_handler.record)
        record_handler.process_request()

    except Exception as error:
        notifications.send_lambda_failure_sns_message(
            session=auth.aft_management_session,
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
