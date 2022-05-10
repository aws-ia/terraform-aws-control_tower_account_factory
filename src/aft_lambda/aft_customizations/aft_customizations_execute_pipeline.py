# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
from typing import TYPE_CHECKING, Any, Dict

from aft_common import aft_utils as utils
from aft_common import notifications
from aft_common.customizations import execute_pipeline
from boto3.session import Session

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object

logger = utils.get_logger()


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    session = Session()
    try:
        maximum_concurrent_pipelines = int(
            utils.get_ssm_parameter_value(
                session, utils.SSM_PARAM_AFT_MAXIMUM_CONCURRENT_CUSTOMIZATIONS
            )
        )

        running_pipelines = int(event["running_executions"]["running_pipelines"])
        pipelines_to_run = maximum_concurrent_pipelines - running_pipelines
        accounts = event["targets"]["pending_accounts"]
        logger.info("Accounts submitted for execution: " + str(len(accounts)))
        for p in accounts[:pipelines_to_run]:
            execute_pipeline(session, str(p))
            accounts.remove(p)
        logger.info("Accounts remaining to be executed - ")
        logger.info(accounts)
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
