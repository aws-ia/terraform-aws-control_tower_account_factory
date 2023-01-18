# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
import json
from typing import TYPE_CHECKING, Any, Dict

from aft_common.account_provisioning_framework import ProvisionRoles
from aft_common.account_request_framework import (
    build_account_customization_payload,
    get_account_request_record,
)
from aft_common.aft_utils import (
    SSM_PARAM_AFT_SFN_NAME,
    get_logger,
    get_ssm_parameter_value,
    invoke_step_function,
    is_aft_supported_controltower_event,
)
from aft_common.auth import AuthClient
from aft_common.notifications import send_lambda_failure_sns_message
from aft_common.organizations import OrganizationsAgent
from boto3.session import Session

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object

logger = get_logger()


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> None:
    auth = AuthClient()

    try:
        aft_management_session = auth.get_aft_management_session()
        ct_management_session = auth.get_ct_management_session(
            role_name=ProvisionRoles.SERVICE_ROLE_NAME
        )
        orgs_agent = OrganizationsAgent(ct_management_session)

        control_tower_event = (
            {}
        )  # Unused by AFT, kept for backwards compability for use by aft-account-provisioning-customizations
        if is_aft_supported_controltower_event(event):
            control_tower_event = event

            logger.info("Control Tower Event Detected")

            # Get account ID from CT event
            # Different CT events have different data structures - map them for easier access
            event_name_to_event_detail_key_map = {
                "CreateManagedAccount": "createManagedAccountStatus",
                "UpdateManagedAccount": "updateManagedAccountStatus",
            }
            event_name = event["detail"]["eventName"]
            account_id = event["detail"]["serviceEventDetails"][
                event_name_to_event_detail_key_map[event_name]
            ]["account"]["accountId"]

            # CT events do not contain email, which is PK of DDB table
            account_email = orgs_agent.get_account_email_from_id(account_id=account_id)
            account_request = get_account_request_record(
                aft_management_session, account_email
            )

        elif "account_request" in event:
            logger.info("Account Customizations Event Detected")

            # Customization-only event does not contain ID
            # Contains OU, and if OU-move was requested, would be completed
            # by this step, so can optimize with OU-only search
            account_request = event["account_request"]
            account_ou = account_request["control_tower_parameters"][
                "ManagedOrganizationalUnit"
            ]
            account_id = orgs_agent.get_account_id_from_email(
                email=event["account_request"][
                    "id"
                ],  # `id` field of ddb table is the account email
                ou_name=account_ou,
            )

        else:
            raise RuntimeError("Invoked with unrecognized event type")

        account_customization_payload = build_account_customization_payload(
            ct_management_session=ct_management_session,
            account_id=account_id,
            account_request=account_request,
            control_tower_event=control_tower_event,
        )

        response = invoke_step_function(
            aft_management_session,
            get_ssm_parameter_value(aft_management_session, SSM_PARAM_AFT_SFN_NAME),
            json.dumps(account_customization_payload),
        )
        logger.info(response)

    except Exception as error:
        send_lambda_failure_sns_message(
            session=aft_management_session,
            message=str(error),
            context=context,
            subject="AFT account request failed",
        )
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(error),
        }
        logger.exception(message)
        raise
