# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Delete the default VPCs of a newly created account.

Step of the CreateAccount branch only, run right after the move and before the
baseline poll, when ``/aft/config/feature/delete-vended-account-default-vpcs-enabled``
is "true". The UpdateAccount branch never runs it: an existing account may use
its default VPC.

It deletes the default VPC in each Region the landing zone governs that is
enabled for the account, and returns ``pending`` while governed Regions are not
enabled yet or EC2 failed in them, up to DEFAULT_VPC_REGION_WAIT_SECONDS after
the execution started. Regions it could not finish are named in one warning to
the AFT notifications topic; the account request never fails here.

The account has no AFT roles yet, so the step uses AWSControlTowerExecution,
the role Organizations CreateAccount created.
"""

import inspect
import json
import logging
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional

from aft_common.account_provisioning_framework import ProvisionRoles
from aft_common.aft_utils import sanitize_input_for_logging
from aft_common.auth import AuthClient
from aft_common.constants import (
    SSM_PARAM_FEATURE_VENDED_ACCOUNT_DEFAULT_VPCS_ENABLED,
    SSM_PARAM_SNS_TOPIC_ARN,
)
from aft_common.control_tower import ControlTowerFacade
from aft_common.logger import configure_aft_logger
from aft_common.notifications import send_sns_message
from aft_common.organizations_provisioning import (
    default_vpc_wait_pending,
    delete_default_vpcs_in_account,
    is_region_disabled_error,
    raise_for_failed_regions,
    regions_not_enabled_result,
)
from aft_common.ssm import get_ssm_parameter_value
from boto3.session import Session
from botocore.exceptions import ClientError

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object

configure_aft_logger()
logger = logging.getLogger("aft")


def _read_feature_enabled(session: Session) -> bool:
    """Enabled only when the flag is "true". The deployment always creates the
    parameter, so a failed read raises, like any other error of the step,
    instead of silently skipping the deletion."""
    value = get_ssm_parameter_value(
        session, SSM_PARAM_FEATURE_VENDED_ACCOUNT_DEFAULT_VPCS_ENABLED
    )
    return value.strip().lower() == "true"


def _step_error_message(error: Any) -> Any:
    """The Lambda's errorMessage from a Step Functions error, whose Cause is
    the Lambda error as JSON with its stack trace. Falls back to the raw
    Cause, or to the error itself when it has none."""
    if not isinstance(error, Mapping) or "Cause" not in error:
        return error
    try:
        return json.loads(error["Cause"])["errorMessage"]
    except (TypeError, ValueError, KeyError):
        return error["Cause"]


def incomplete_deletion_message(
    account_id: str,
    unreachable: Optional[List[str]] = None,
    error: Optional[Any] = None,
    not_enabled: Optional[List[str]] = None,
) -> str:
    lines = [
        f"AFT could not delete every default VPC of the new account {account_id}. "
        "The account request continued.",
        "",
    ]
    if unreachable:
        lines.append(
            "Regions skipped because their EC2 endpoint was unreachable: "
            + ", ".join(unreachable)
        )
    if not_enabled:
        lines.append(
            "Regions not enabled for the account when the wait for them ended, "
            "or whose opt-in status could not be read: " + ", ".join(not_enabled)
        )
    if error is not None:
        error_name = error.get("Error") if isinstance(error, Mapping) else None
        failed = (
            f"The default VPC deletion step failed with {error_name}"
            if error_name
            else "The default VPC deletion step failed"
        )
        lines.append(f"{failed}: {_step_error_message(error)}")
    lines += [
        "",
        "Delete the remaining default VPCs in the account, or apply your "
        "network baseline over them. AFT does not retry this for an existing "
        "account.",
    ]
    return "\n".join(lines)


def notify_incomplete_deletion(
    session: Session,
    account_id: str,
    unreachable: Optional[List[str]] = None,
    error: Optional[Any] = None,
    not_enabled: Optional[List[str]] = None,
) -> None:
    """Publish one warning to the AFT notifications topic. A failed publish is
    logged and does not fail the account request."""
    try:
        send_sns_message(
            session=session,
            topic=get_ssm_parameter_value(session, SSM_PARAM_SNS_TOPIC_ARN),
            sns_message=incomplete_deletion_message(
                account_id, unreachable, error, not_enabled=not_enabled
            ),
            # SNS subjects are single-line and at most 100 characters.
            subject=f"AFT default VPCs not deleted for account {account_id}"[:100],
        )
    except Exception:
        logger.exception("Could not publish the default VPC deletion warning")


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    auth = AuthClient()
    aft_management_session = auth.get_aft_management_session()
    account_id = str(event["move"]["account_id"])

    if "default_vpcs_error" in event:
        # The deletion step failed after its retries; report it and go on.
        error = event["default_vpcs_error"]
        logger.warning(
            f"Default VPC deletion in account {sanitize_input_for_logging(account_id)} "
            f"failed (best effort, provisioning continues): "
            f"{sanitize_input_for_logging(error)}"
        )
        notify_incomplete_deletion(aft_management_session, account_id, error=error)
        return {"reported": True, "pending": False}

    try:
        if not _read_feature_enabled(aft_management_session):
            logger.info("Default VPC deletion for new accounts is disabled; skipping")
            return {"skipped": True, "pending": False}

        ct_management_session = auth.get_ct_management_session(
            role_name=ProvisionRoles.SERVICE_ROLE_NAME
        )
        regions = ControlTowerFacade(
            ct_management_session=ct_management_session
        ).get_governed_regions()
        logger.info(
            f"Deleting default VPCs in account {sanitize_input_for_logging(account_id)}: "
            f"{sanitize_input_for_logging(regions)}"
        )
        try:
            target_account_session = auth.get_target_account_session(
                account_id=account_id,
                hub_session=ct_management_session,
                role_name=AuthClient.CONTROL_TOWER_EXECUTION_ROLE_NAME,
            )
        except ClientError as error:
            if not is_region_disabled_error(error):
                raise
            # The home Region is an opt-in Region that Control Tower has not
            # enabled for the account yet. Like a failed DescribeRegions,
            # every Region counts as not enabled, so the step waits.
            logger.warning(
                f"Cannot reach account {sanitize_input_for_logging(account_id)} "
                "yet (RegionDisabledException); treating "
                f"{sanitize_input_for_logging(regions)} as not enabled for the "
                "account yet"
            )
            result = regions_not_enabled_result(regions)
        else:
            result = delete_default_vpcs_in_account(target_account_session, regions)
        pending = default_vpc_wait_pending(
            [*result["not_enabled"], *result["failed"]], event.get("create_window")
        )
        if not pending:
            # The wait has ended: Regions where EC2 still fails raise, so the
            # state machine retries the step and reports it once.
            raise_for_failed_regions(result)
    except Exception as error:
        logger.exception(
            {
                "FILE": __file__.split("/")[-1],
                "METHOD": inspect.stack()[0][3],
                "EXCEPTION": sanitize_input_for_logging(error),
            }
        )
        raise

    if pending:
        # No warning yet: the next run retries these Regions, and the
        # unreachable ones with them.
        logger.info(
            f"Default VPC deletion in account {sanitize_input_for_logging(account_id)} "
            "waits for Regions not enabled for the account yet: "
            f"{sanitize_input_for_logging(result['not_enabled'])}, and Regions where "
            f"it failed: {sanitize_input_for_logging(result['failed'])} (unreachable: "
            f"{sanitize_input_for_logging(result['unreachable'])})"
        )
    elif result["unreachable"] or result["not_enabled"]:
        logger.warning(
            f"Default VPC deletion in account {sanitize_input_for_logging(account_id)} "
            f"skipped unreachable Regions {sanitize_input_for_logging(result['unreachable'])} "
            "and Regions not enabled for the account "
            f"{sanitize_input_for_logging(result['not_enabled'])} "
            "(best effort, provisioning continues)"
        )
        notify_incomplete_deletion(
            aft_management_session,
            account_id,
            unreachable=result["unreachable"],
            not_enabled=result["not_enabled"],
        )
    return {"skipped": False, "pending": pending, **result}
