# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
from typing import TYPE_CHECKING, Any, Dict

from aft_common import aft_utils as utils
from aft_common import notifications
from aft_common.account_provisioning_framework import get_account_info
from aft_common.types import AftAccountInfo
from boto3.session import Session

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object

logger = utils.get_logger()


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> AftAccountInfo:
    session = Session()
    try:
        logger.info("AFT Account Provisioning Framework Get Account Info Handler Start")

        payload = event["payload"]
        action = event["action"]

        ct_management_session = utils.get_ct_management_session(session)
        if action == "get_account_info":
            return get_account_info(payload, session, ct_management_session)
        else:
            raise Exception(
                f"Incorrect Command Passed to Lambda Function. Input action: {action}. Expected: 'get_account_info'"
            )

    except Exception as error:
        notifications.send_lambda_failure_sns_message(
            session=session,
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
