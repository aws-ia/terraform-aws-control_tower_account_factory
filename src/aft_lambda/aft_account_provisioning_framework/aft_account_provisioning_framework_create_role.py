# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
from typing import TYPE_CHECKING, Any, Dict

from aft_common import aft_utils as utils
from aft_common import notifications
from aft_common.account_provisioning_framework import ProvisionRoles
from aft_common.auth import AuthClient

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object

logger = utils.get_logger()


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> None:
    auth = AuthClient()
    try:
        logger.info("AFT Account Provisioning Framework Create Role Handler Start")

        payload = event["payload"]
        action = event["action"]

        if action != "create_role":
            raise Exception(
                f"Incorrect Command Passed to Lambda Function. Input: {action}. Expected: 'create_role'"
            )

        account_id = payload["account_info"]["account"]["id"]
        provisioning = ProvisionRoles(auth=auth, account_id=account_id)
        provisioning.deploy_aws_aft_execution_role()
        provisioning.deploy_aws_aft_service_role()

    except Exception as error:
        notifications.send_lambda_failure_sns_message(
            session=auth.get_aft_management_session(),
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
