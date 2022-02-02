import inspect
import json
from typing import Any, Dict, Union

import aft_common.aft_utils as utils
from aft_common.account_request_framework import (
    build_invoke_event,
    is_customizations_event,
)
from boto3.session import Session

logger = utils.get_logger()


def lambda_handler(event: Dict[str, Any], context: Union[Dict[str, Any], None]) -> None:
    try:
        logger.info("Lambda_handler Event")
        logger.info(event)
        session = Session()
        ct_management_session = utils.get_ct_management_session(session)
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

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise
