# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Compare a provisioned account's baselines and controls with its OU's.

Shared step of the CreateAccount and UpdateAccount branches, after the
baseline poll. ``/aft/config/feature/governance-validation-enabled`` turns the
check off; with ``/aft/config/governance-validation-mode`` set to "fail", a gap
fails the execution, with "warn" it is logged and published to the AFT
notifications topic. The ARNs come from ``event["move"]``, resolved once by
MoveAccount.
"""

import inspect
import logging
from typing import TYPE_CHECKING, Any, Dict, List, Mapping

from aft_common.account_provisioning_framework import ProvisionRoles
from aft_common.aft_utils import sanitize_input_for_logging
from aft_common.auth import AuthClient
from aft_common.constants import (
    SSM_PARAM_GOVERNANCE_VALIDATION_ENABLED,
    SSM_PARAM_GOVERNANCE_VALIDATION_MODE,
    SSM_PARAM_SNS_TOPIC_ARN,
)
from aft_common.control_tower import ControlTowerFacade
from aft_common.logger import configure_aft_logger
from aft_common.notifications import send_sns_message
from aft_common.organizations_provisioning import (
    GOVERNANCE_MODE_FAIL,
    validate_account_governance,
)
from aft_common.ssm import get_ssm_parameter_value
from boto3.session import Session

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object

configure_aft_logger()
logger = logging.getLogger("aft")

MOVE_KEYS = (
    "account_id",
    "destination_ou_id",
    "account_arn",
    "ou_arn",
    "ou_enabled_baseline_arns",
)


class GovernanceValidationError(Exception):
    """The account does not match its OU and the mode is "fail"."""


def gap_notification_message(
    move: Mapping[str, Any], gaps: List[Mapping[str, Any]]
) -> str:
    lines = [
        "AFT governance validation found gaps between an account and its OU in "
        "the aft-organizations-account-provisioning Step Function.",
        "",
        f"Account id: {move['account_id']}",
        f"Managed OU: {move['destination_ou_id']}",
        "Mode: warn (the account request continues)",
        "",
        f"Gaps ({len(gaps)}):",
    ]
    for gap in gaps:
        identifier = (
            gap.get("control_identifier")
            or gap.get("baseline_identifier")
            or gap.get("parent_identifier")
        )
        lines.append(f"- {gap['type']} {identifier}: {gap['detail']}")
    return "\n".join(lines)


def notify_gaps(
    session: Session, move: Mapping[str, Any], gaps: List[Mapping[str, Any]]
) -> None:
    """Publish the gaps found in warn mode to the AFT notifications topic.

    A failed publish is logged and does not fail the account request.
    """
    try:
        send_sns_message(
            session=session,
            topic=get_ssm_parameter_value(session, SSM_PARAM_SNS_TOPIC_ARN),
            sns_message=gap_notification_message(move, gaps),
            # SNS subjects are single-line and at most 100 characters.
            subject=f"AFT governance gaps for account {move['account_id']}"[:100],
        )
    except Exception:
        logger.exception("Could not publish the governance gaps notification")


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    auth = AuthClient()
    try:
        aft_management_session = auth.get_aft_management_session()
        enabled = get_ssm_parameter_value(
            aft_management_session, SSM_PARAM_GOVERNANCE_VALIDATION_ENABLED
        )
        if enabled != "true":
            logger.info("Governance validation is turned off; skipping")
            return {"compliant": True, "gaps": [], "mode": None, "skipped": True}

        move = event.get("move", {})
        missing = [key for key in MOVE_KEYS if not move.get(key)]
        if missing:
            raise ValueError(f"event['move'] is missing {missing}")

        mode = get_ssm_parameter_value(
            aft_management_session, SSM_PARAM_GOVERNANCE_VALIDATION_MODE
        )

        ct_management_session = auth.get_ct_management_session(
            role_name=ProvisionRoles.SERVICE_ROLE_NAME
        )
        result = validate_account_governance(
            ct_facade=ControlTowerFacade(ct_management_session=ct_management_session),
            account_id=move["account_id"],
            destination_ou_id=move["destination_ou_id"],
            targets=move,
            mode=mode,
        )
        if not result["compliant"]:
            message = (
                f"Account {sanitize_input_for_logging(move['account_id'])} does not match OU "
                f"{sanitize_input_for_logging(move['destination_ou_id'])}: {len(result['gaps'])} gap(s): "
                f"{sanitize_input_for_logging(result['gaps'])}"
            )
            if mode == GOVERNANCE_MODE_FAIL:
                raise GovernanceValidationError(message)
            logger.warning(message)
            notify_gaps(aft_management_session, move, result["gaps"])
        return result
    except Exception as error:
        logger.exception(
            {
                "FILE": __file__.split("/")[-1],
                "METHOD": inspect.stack()[0][3],
                "EXCEPTION": str(error),
            }
        )
        raise
