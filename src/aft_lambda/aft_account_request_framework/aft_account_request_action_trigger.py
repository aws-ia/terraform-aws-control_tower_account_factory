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

        # Account record was deleted from `aft-request` repo
        if record_handler.record["eventName"] == "REMOVE":
            record_handler.handle_remove()
            logger.info("Delete account request received")

        # We only support customization actions against shared accounts
        elif not control_tower_param_changed(
            record=record_handler.record
        ) and shared_account_request(event_record=record_handler.record):
            logger.info("Customization request received")
            record_handler.handle_customization_request()

        # In this situation, a new entry has been added to the account request table
        # but no provisioned product exists, that means no account should exist for this
        # and we must process this as a new account request
        elif record_handler.is_create_action and not provisioned_product_exists(
            record=record_handler.record
        ):
            logger.info("New account request received")
            record_handler.handle_account_request(new_account=True)

        # In this situation, a new entry has been added to the account request table
        # and a provisioned product exists, and No Control Tower parameters changed
        elif (
            record_handler.is_create_action
            and provisioned_product_exists(record=record_handler.record)
            and not record_handler.control_tower_parameters_updated
        ):
            logger.info("Customization request received for existing CT account")
            record_handler.handle_customization_request()

        # If we're processing a request that updates an existing entry in the
        # account request table, we need to handle control tower parameter changes
        # by routing the request to service catalog
        elif (
            record_handler.is_update_action
            and record_handler.control_tower_parameters_updated
        ):
            logger.info("Control Tower parameter update request received")
            record_handler.handle_account_request(new_account=False)

        # In this situation we have an entry in the account request table, but no control
        # tower parameters are being updated, we can optimize this flow but routing the
        # request to the customization stepfunction directly
        elif (
            record_handler.is_update_action
            and not record_handler.control_tower_parameters_updated
        ):
            logger.info("Customization request received")
            record_handler.handle_customization_request()

        else:
            raise Exception("Unsupported account request")

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
