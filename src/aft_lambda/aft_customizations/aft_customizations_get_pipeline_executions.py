# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
from typing import TYPE_CHECKING, Any, Dict

from aft_common import aft_utils as utils
from aft_common import notifications
from aft_common.customizations import get_running_pipeline_count, list_pipelines
from boto3.session import Session

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object

logger = utils.get_logger()


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, int]:
    session = Session()
    try:
        pipelines = list_pipelines(session)
        running_pipelines = get_running_pipeline_count(session, pipelines)

        return {"running_pipelines": running_pipelines}

    except Exception as error:
        notifications.send_lambda_failure_sns_message(
            session=session,
            message=str(error),
            context=context,
            subject="Failed to list all AFT account customization pipelines",
        )
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(error),
        }
        logger.exception(message)
        raise
