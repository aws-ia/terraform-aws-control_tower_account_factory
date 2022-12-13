# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
import sys
from typing import TYPE_CHECKING, Any, Dict

from aft_common import aft_utils as utils
from aft_common import notifications
from aft_common.account_request_framework import (
    build_account_customization_payload,
    get_account_request_record,
)
from aft_common.auth import AuthClient
from aft_common.customizations import (
    get_excluded_accounts,
    get_included_accounts,
    get_target_accounts,
    validate_identify_targets_request,
)
from aft_common.organizations import OrganizationsAgent

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object

logger = utils.get_logger()


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    auth = AuthClient()

    try:
        aft_management_session = auth.get_aft_management_session()
        ct_mgmt_session = auth.get_ct_management_session()

        # Reuse orgs agent to benefit from memoization, avoid throttling
        orgs_agent = OrganizationsAgent(ct_mgmt_session)

        payload = event
        if not validate_identify_targets_request(payload):
            sys.exit(1)
        else:
            included_accounts = get_included_accounts(
                aft_management_session, ct_mgmt_session, orgs_agent, payload["include"]
            )
            if "exclude" in payload.keys():
                excluded_accounts = get_excluded_accounts(
                    aft_management_session,
                    ct_mgmt_session,
                    orgs_agent,
                    payload["exclude"],
                )
                target_accounts = get_target_accounts(
                    included_accounts, excluded_accounts
                )
            else:
                target_accounts = included_accounts

            target_account_info = []
            for account_id in target_accounts:

                account_email = orgs_agent.get_account_email_from_id(account_id)
                account_request = get_account_request_record(
                    aft_management_session=aft_management_session,
                    table_id=account_email,
                )

                target_account_info.append(
                    build_account_customization_payload(
                        ct_management_session=ct_mgmt_session,
                        account_id=account_id,
                        account_request=account_request,
                        control_tower_event={},
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
