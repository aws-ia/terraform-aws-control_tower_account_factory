# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
import logging
from typing import TYPE_CHECKING, Any, Dict

import aft_common.ssm
from aft_common import constants as utils
from aft_common import notifications
from aft_common.aft_utils import sanitize_input_for_logging
from aft_common.codepipeline import execute_pipeline
from aft_common.logger import configure_aft_logger, customization_request_logger
from boto3.session import Session

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object

configure_aft_logger()
logger = logging.getLogger("aft")


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    session = Session()
    try:
        maximum_concurrent_pipelines = int(
            aft_common.ssm.get_ssm_parameter_value(
                session, utils.SSM_PARAM_AFT_MAXIMUM_CONCURRENT_CUSTOMIZATIONS
            )
        )

        running_pipelines = int(event["running_executions"]["running_pipelines"])
        pipelines_to_run = maximum_concurrent_pipelines - running_pipelines
        accounts = event["targets"]["pending_accounts"]
        logger.info("Accounts submitted for execution: " + str(len(accounts)))
        for account_id in accounts[:pipelines_to_run]:
            execute_pipeline(session, str(account_id))
            accounts.remove(account_id)
        logger.info("Accounts remaining to be executed - ")
        sanitized_accounts = sanitize_input_for_logging(accounts)
        logger.info(sanitized_accounts)
        return {"number_pending_accounts": len(accounts), "pending_accounts": accounts}

    except Exception as error:
        notifications.send_lambda_failure_sns_message(
            session=session,
            message=str(error),
            context=context,
            subject="Failed to trigger one or more AFT account customization pipelines",
        )
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(error),
        }
        logger.exception(message)
        raise
