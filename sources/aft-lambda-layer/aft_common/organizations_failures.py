# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Failure notification for the organizations account-provisioning Step Function.

The state machine sends one notification per failed execution: every step's
Catch, and the failed-baseline branch, go to a NotifyFailure step that calls
:func:`notify_provisioning_failure` with the execution's state. An EventBridge
rule calls it with the status-change event of an execution that timed out,
which no state of the execution can catch. The step Lambdas themselves send
nothing, so a failed attempt that the step's Retry recovers is not reported.

By the time an execution fails, the account request processor has already
deleted the request from the SQS queue, so the notification names the request
for the operator to re-submit.
"""

import json
import logging
from typing import Any, Dict, Mapping, Optional

from aft_common.constants import SSM_PARAM_SNS_FAILURE_TOPIC_ARN
from aft_common.notifications import send_sns_message
from aft_common.organizations import OrganizationsAgent
from aft_common.ssm import get_ssm_parameter_value
from boto3.session import Session

logger = logging.getLogger("aft")

EXECUTION_STATUS_CHANGE = "Step Functions Execution Status Change"
# A Fail state's Cause is limited to 32768 characters; the cause also goes
# into the notification.
MAX_CAUSE_LENGTH = 4096

# Raised by the ValidateGovernance step in mode "fail".
GOVERNANCE_VALIDATION_ERROR = "GovernanceValidationError"
GOVERNANCE_VALIDATION_NEXT_STEP = (
    "Resolve the gaps listed in the cause in Control Tower. Re-submitting the "
    "unchanged account request does not validate governance again: once all "
    "of the account's baselines are complete, AFT handles the request as a "
    "customization request. Only a change to control_tower_parameters runs "
    "this Step Function, and the validation, again."
)


def _error_message(cause: Any) -> str:
    """The message of a Catch result's Cause: a Lambda error's Cause is a JSON
    document whose errorMessage is the exception's message."""
    if not isinstance(cause, str):
        return "" if cause is None else str(cause)
    try:
        parsed = json.loads(cause)
    except ValueError:
        return cause
    if isinstance(parsed, dict) and parsed.get("errorMessage"):
        return str(parsed["errorMessage"])
    return cause


def _account_id(state: Mapping[str, Any]) -> Optional[str]:
    for value in (
        (state.get("move") or {}).get("account_id"),
        (state.get("lookup") or {}).get("account_id"),
        (state.get("create_status") or {}).get("AccountId"),
    ):
        if value:
            return str(value)
    return None


def describe_provisioning_failure(
    state: Mapping[str, Any], execution_arn: str, timed_out: bool = False
) -> Dict[str, Any]:
    """Describe why the execution with state ``state`` failed.

    ``state["error"]`` is a Catch result (``Error`` and ``Cause``). Without it,
    a failed CreateAccount request (``state["create_status"]``), a failed
    baseline (``state["baseline"]["is_failed"]``) or ``timed_out`` explains
    the failure.
    """
    error = state.get("error") or {}
    create_status = state.get("create_status") or {}
    baseline = state.get("baseline") or {}
    next_step: Optional[str] = None
    if error:
        error_name = str(error.get("Error") or "States.TaskFailed")
        cause = _error_message(error.get("Cause"))
        if error_name == GOVERNANCE_VALIDATION_ERROR:
            next_step = GOVERNANCE_VALIDATION_NEXT_STEP
    elif create_status.get("State") == "FAILED":
        error_name = "CreateAccountFailed"
        cause = (
            "Organizations CreateAccount failed: "
            f"{create_status.get('FailureReason') or 'no FailureReason returned'}"
        )
    elif baseline.get("enrollment_not_started"):
        error_name = "BaselineEnrollmentNotStarted"
        cause = (
            "The account is already in its managed OU, so it was not moved, and "
            "Control Tower is not enrolling it: baseline operation status "
            f"{baseline.get('operation_status')}, inheritance drift status "
            f"{baseline.get('inheritance_drift_status')}. Re-register the OU or "
            "reset the account's baseline in Control Tower, then re-submit the "
            "request."
        )
    elif baseline.get("failed_controls"):
        error_name = "ControlDeploymentFailed"
        cause = (
            "Control Tower failed to deploy these controls of the managed OU to "
            f"the account: {', '.join(baseline['failed_controls'])}"
        )
    elif baseline.get("is_failed"):
        error_name = "BaselineEnrollmentFailed"
        cause = (
            "Control Tower failed to enroll the account in its managed OU: "
            f"baseline operation status {baseline.get('operation_status')}, "
            f"inheritance drift status {baseline.get('inheritance_drift_status')}"
        )
    elif timed_out:
        error_name = "States.Timeout"
        cause = (
            "The execution exceeded TimeoutSeconds "
            "(aft_organizations_provisioning_timeout_seconds)"
        )
    else:
        error_name = "ProvisioningFailed"
        cause = "The execution failed without an error"

    ct_parameters = state.get("control_tower_parameters") or {}
    failure: Dict[str, Any] = {
        "operation": state.get("operation"),
        "account_email": ct_parameters.get("AccountEmail"),
        "account_id": _account_id(state),
        "managed_ou": ct_parameters.get("ManagedOrganizationalUnit"),
        "execution_arn": execution_arn,
        "error": error_name,
        "cause": cause[:MAX_CAUSE_LENGTH],
    }
    if next_step:
        failure["next_step"] = next_step
    return failure


def failure_from_status_change(event: Mapping[str, Any]) -> Dict[str, Any]:
    """Describe the execution in a Step Functions Execution Status Change event."""
    detail = event.get("detail") or {}
    try:
        state = json.loads(detail.get("input") or "{}")
    except ValueError:
        state = {}
    return describe_provisioning_failure(
        state if isinstance(state, dict) else {},
        execution_arn=str(detail.get("executionArn")),
        timed_out=detail.get("status") == "TIMED_OUT",
    )


def add_existing_account(
    failure: Dict[str, Any], orgs_agent: OrganizationsAgent
) -> Dict[str, Any]:
    """Complete the failure of a timed-out execution with the account, if it
    exists.

    The status-change event carries only the execution's input, which has no
    account id, although an ADD that timed out in the baseline poll has
    already created the account. Looks it up by email and, when it exists,
    records its id and current OU and says it was not enrolled in time. A
    lookup that fails leaves the account unknown rather than "not created".
    """
    if failure.get("account_id") or not failure.get("account_email"):
        return failure
    try:
        account = orgs_agent.get_account_by_email(failure["account_email"])
        if account is None:
            return failure
        ou = orgs_agent.get_ou_from_account_id(account["Id"])
    except Exception:
        logger.exception("Could not look up the account of the timed-out execution")
        return {**failure, "account_id_unknown": True}
    return {
        **failure,
        "account_id": account["Id"],
        "account_ou": f"{ou['Name']} ({ou['Id']})",
        "next_step": (
            "The account exists, but the execution timed out before Control "
            "Tower finished enrolling it. Re-submitting the account request "
            "handles it as an existing account: it creates no new account and "
            "waits for the enrollment."
        ),
    }


def _account_id_line(failure: Mapping[str, Any]) -> str:
    if failure.get("account_id"):
        return str(failure["account_id"])
    if failure.get("account_id_unknown"):
        return "unknown (the account lookup failed)"
    return "not created or not found"


def failure_message(failure: Mapping[str, Any]) -> str:
    lines = [
        "An AFT account request failed in the "
        "aft-organizations-account-provisioning Step Function.",
        "",
        f"Operation: {failure['operation']}",
        f"Account email: {failure['account_email']}",
        f"Account id: {_account_id_line(failure)}",
        f"Managed OU: {failure['managed_ou']}",
    ]
    if failure.get("account_ou"):
        lines.append(f"Account's current OU: {failure['account_ou']}")
    lines += [
        f"Execution: {failure['execution_arn']}",
        f"Error: {failure['error']}",
        f"Cause: {failure['cause']}",
        "",
        "The request is no longer queued.",
        failure.get("next_step")
        or "After fixing the cause, re-submit the account request to retry it.",
    ]
    return "\n".join(lines)


def notify_provisioning_failure(session: Session, failure: Mapping[str, Any]) -> None:
    """Publish one failure notification to the AFT failure SNS topic."""
    operation = failure.get("operation") or "account request"
    send_sns_message(
        session=session,
        topic=get_ssm_parameter_value(session, SSM_PARAM_SNS_FAILURE_TOPIC_ARN),
        sns_message=failure_message(failure),
        # SNS subjects are single-line and at most 100 characters.
        subject=f"AFT organizations {operation} failed: {failure['error']}"[:100],
    )
