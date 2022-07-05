# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
from typing import TYPE_CHECKING, Any, Dict

from aft_common import aft_utils as utils
from aft_common import notifications
from aft_common.account_provisioning_framework import persist_metadata
from boto3.session import Session

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
    aft_management_session = Session()
    try:
        logger.info("AFT Account Provisioning Framework Handler Start")

        rollback = None

        try:
            if event["rollback"]:
                rollback = True
        except KeyError:
            pass

        payload = event["payload"]
        action = event["action"]

        if action == "persist_metadata":
            account_info = payload["account_info"]["account"]
            update_metadata = persist_metadata(
                payload, account_info, aft_management_session
            )
            return update_metadata
        else:
            raise Exception(
                f"Incorrect Command Passed to Lambda Function. Input action: {action}. Expected: 'persist_metadata'"
            )

    except Exception as error:
        notifications.send_lambda_failure_sns_message(
            session=aft_management_session,
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
