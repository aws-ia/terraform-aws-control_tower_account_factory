# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
import sys
from typing import TYPE_CHECKING, Any, Dict

from aft_common import aft_utils as utils
from aft_common import notifications
from aft_common.auth import AuthClient
from aft_common.customizations import (
    get_excluded_accounts,
    get_included_accounts,
    get_target_accounts,
    validate_request,
)
from boto3.session import Session

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object

logger = utils.get_logger()


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    session = Session()
    auth = AuthClient()
    try:
        payload = event
        if not validate_request(payload):
            sys.exit(1)
        else:
            ct_mgmt_session = auth.get_ct_management_session()
            included_accounts = get_included_accounts(
                session, ct_mgmt_session, payload["include"]
            )
            if "exclude" in payload.keys():
                excluded_accounts = get_excluded_accounts(
                    session, ct_mgmt_session, payload["exclude"]
                )
                target_accounts = get_target_accounts(
                    included_accounts, excluded_accounts
                )
            else:
                target_accounts = included_accounts

            return {
                "number_pending_accounts": len(target_accounts),
                "pending_accounts": target_accounts,
            }

    except Exception as error:
        notifications.send_lambda_failure_sns_message(
            session=session,
            message=str(error),
            context=context,
            subject="Failed to identify targets for AFT account customizations",
        )
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(error),
        }
        logger.exception(message)
        raise
