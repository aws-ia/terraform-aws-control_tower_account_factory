# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
from typing import TYPE_CHECKING, Any, Dict

import boto3
from aft_common import aft_utils as utils
from aft_common import notifications

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
    from mypy_boto3_dynamodb.type_defs import PutItemOutputTableTypeDef
else:
    PutItemOutputTableTypeDef = object
    LambdaContext = object

logger = utils.get_logger()


def lambda_handler(
    event: Dict[str, Any], context: LambdaContext
) -> PutItemOutputTableTypeDef:
    session = boto3.session.Session()
    try:
        response = utils.put_ddb_item(
            session,
            utils.get_ssm_parameter_value(session, utils.SSM_PARAM_AFT_EVENTS_TABLE),
            event,
        )
        return response

    except Exception as error:
        notifications.send_lambda_failure_sns_message(
            session=session,
            message=str(error),
            context=context,
            subject="AFT Event Logging failed",
        )
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(error),
        }
        logger.exception(message)
        raise
