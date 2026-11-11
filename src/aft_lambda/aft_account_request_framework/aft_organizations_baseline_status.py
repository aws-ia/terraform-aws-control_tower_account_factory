# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Read the Control Tower enrollment of a created-and-moved account.

The state machine calls this in a Wait loop after MoveAccount. It moves on to
governance validation when ``is_complete`` (the baseline is enrolled) and
``controls_settled`` (the OU's controls are on the account), or when
``controls_wait_expired``, and fails on ``is_failed``. The previous poll's
result, ``event["baseline"]``, carries the time the baseline was first seen
complete and whether a poll has seen it complete, and ``event["poll_window"]``
the execution's start time and TimeoutSeconds, which bound the control wait.
The ARNs come from ``event["move"]``, resolved once by MoveAccount. Shared by
the CreateAccount and UpdateAccount branches.
"""

import inspect
import logging
from typing import TYPE_CHECKING, Any, Dict

from aft_common.account_provisioning_framework import ProvisionRoles
from aft_common.auth import AuthClient
from aft_common.control_tower import ControlTowerFacade
from aft_common.logger import configure_aft_logger
from aft_common.organizations_provisioning import get_baseline_status

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object

configure_aft_logger()
logger = logging.getLogger("aft")

# What the MoveAccount step returns and this poll reads.
MOVE_KEYS = (
    "account_id",
    "destination_ou_id",
    "account_arn",
    "ou_arn",
    "ou_enabled_baseline_arns",
)


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    auth = AuthClient()
    try:
        move = event.get("move", {})
        missing = [key for key in MOVE_KEYS if not move.get(key)]
        if missing:
            raise ValueError(f"event['move'] is missing {missing}")
        ct_management_session = auth.get_ct_management_session(
            role_name=ProvisionRoles.SERVICE_ROLE_NAME
        )
        ct_facade = ControlTowerFacade(ct_management_session=ct_management_session)
        return get_baseline_status(
            ct_facade=ct_facade,
            account_id=move["account_id"],
            destination_ou_id=move["destination_ou_id"],
            targets=move,
            previous=event.get("baseline"),
            poll_window=event.get("poll_window"),
        )
    except Exception as error:
        logger.exception(
            {
                "FILE": __file__.split("/")[-1],
                "METHOD": inspect.stack()[0][3],
                "EXCEPTION": str(error),
            }
        )
        raise
