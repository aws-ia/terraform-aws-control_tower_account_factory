# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
from typing import TYPE_CHECKING, Any, Dict

from aft_common import aft_utils as utils
from aft_common import notifications
from aft_common.account_provisioning_framework import tag_account
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
        logger.info("AFT Account Provisioning Framework Handler Start")

        rollback = False
        try:
            if event["rollback"]:
                rollback = True
        except KeyError:
            pass

        payload = event["payload"]
        action = event["action"]
        ct_management_session = auth.get_ct_management_session()

        if action == "tag_account":
            account_info = payload["account_info"]["account"]
            tag_account(payload, account_info, ct_management_session, rollback)
        else:
            raise Exception(
                f"Incorrect Command Passed to Lambda Function. Input action: {action}. Expected: 'tag_account'"
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
