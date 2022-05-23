# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
import json
from typing import TYPE_CHECKING, Any, Dict

from aft_common import aft_utils as utils
from aft_common import notifications
from aft_common.account_request_framework import (
    build_invoke_event,
    is_customizations_event,
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
        response = None
        if utils.is_controltower_event(
            event
        ) and utils.is_aft_supported_controltower_event(event):
            logger.info("Control Tower Event Detected")
            invoke_event = build_invoke_event(
                session, ct_management_session, event, "ControlTower"
            )
            response = utils.invoke_step_function(
                session,
                utils.get_ssm_parameter_value(session, utils.SSM_PARAM_AFT_SFN_NAME),
                json.dumps(invoke_event),
            )
        elif is_customizations_event(event):
            logger.info("Account Customizations Event Detected")
            invoke_event = build_invoke_event(
                session, ct_management_session, event, "Customizations"
            )
            response = utils.invoke_step_function(
                session,
                utils.get_ssm_parameter_value(session, utils.SSM_PARAM_AFT_SFN_NAME),
                json.dumps(invoke_event),
            )
        logger.info(response)

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
