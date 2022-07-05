# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
import sys
from typing import TYPE_CHECKING, Any, Dict

from aft_common import aft_utils as utils
from aft_common import notifications
from aft_common.account_provisioning_framework import ProvisionRoles
from aft_common.auth import AuthClient
from aft_common.customizations import (
    build_customization_invoke_event_for_target_account,
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
    aft_management_session = Session()
    auth = AuthClient()
    try:
        payload = event
        if not validate_request(payload):
            sys.exit(1)
        else:
            ct_mgmt_session = auth.get_ct_management_session(
                role_name=ProvisionRoles.SERVICE_ROLE_NAME
            )
            included_accounts = get_included_accounts(
                aft_management_session, ct_mgmt_session, payload["include"]
            )
            if "exclude" in payload.keys():
                excluded_accounts = get_excluded_accounts(
                    aft_management_session, ct_mgmt_session, payload["exclude"]
                )
                target_accounts = get_target_accounts(
                    included_accounts, excluded_accounts
                )
            else:
                target_accounts = included_accounts

            target_account_info = []
            account_metadata_table = utils.get_ssm_parameter_value(
                aft_management_session, utils.SSM_PARAM_AFT_DDB_META_TABLE
            )
            account_request_table = utils.get_ssm_parameter_value(
                aft_management_session, utils.SSM_PARAM_AFT_DDB_REQ_TABLE
            )
            for account_id in target_accounts:
                target_account_info.append(
                    build_customization_invoke_event_for_target_account(
                        account_id=account_id,
                        account_metadata_table=account_metadata_table,
                        account_request_table=account_request_table,
                        aft_management_session=aft_management_session,
                    )
                )

            return {
                "number_pending_accounts": len(target_accounts),
                "pending_accounts": target_accounts,
                "target_accounts_info": target_account_info,
            }

    except Exception as error:
        notifications.send_lambda_failure_sns_message(
            session=aft_management_session,
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
