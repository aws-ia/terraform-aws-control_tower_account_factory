# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Step logic for the ``aft-organizations-account-provisioning`` Step Function.

The state machine's Lambda handlers call these functions. The Organizations
vending method creates accounts with the Organizations API and relies on
Control Tower auto-enrollment to baseline them, so no Service Catalog
provisioned product is involved.
"""

import json
import logging
import math
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional, Sequence, Tuple

from aft_common.aft_utils import sanitize_input_for_logging
from aft_common.constants import (
    ORGANIZATIONS_LIFECYCLE_EVENT_DETAIL_TYPE,
    ORGANIZATIONS_LIFECYCLE_EVENT_SOURCE,
)
from aft_common.control_tower import ControlTowerFacade, EnabledControlStatus
from aft_common.feature_options import (
    delete_acls,
    delete_internet_gateways,
    delete_route_tables,
    delete_security_groups,
    delete_subnets,
    delete_vpc,
    get_vpc_acls,
    get_vpc_internet_gateways,
    get_vpc_route_tables,
    get_vpc_security_groups,
    get_vpc_subnets,
)
from aft_common.organizations import OrganizationsAgent
from boto3.session import Session
from botocore.config import Config
from botocore.exceptions import (
    ClientError,
    ConnectTimeoutError,
    EndpointConnectionError,
    ReadTimeoutError,
)

if TYPE_CHECKING:
    from mypy_boto3_ec2 import EC2Client
else:
    EC2Client = object

logger = logging.getLogger("aft")


def _organizations_arn(organization: Mapping[str, Any], resource: str) -> str:
    """Compose ``arn:<partition>:organizations::<mgmt>:<resource-type>/<org-id>/<id>``
    from a ``describe_organization`` result. ``resource`` is
    ``account/<account-id>`` or ``ou/<ou-id>``.
    """
    partition = organization["MasterAccountArn"].split(":")[1]
    resource_type, resource_id = resource.split("/", 1)
    return (
        f"arn:{partition}:organizations::{organization['MasterAccountId']}:"
        f"{resource_type}/{organization['Id']}/{resource_id}"
    )


class InvalidAccountRequestError(Exception):
    """The account request cannot be vended as it is. Retrying does not help;
    the request has to be corrected."""


def enabled_baseline_arns_for_vending(
    ct_facade: ControlTowerFacade, ou_arn: str, ou_label: str
) -> List[str]:
    """Return the ARNs of the baselines enabled on the OU ``ou_arn``, after
    checking that AFT can vend accounts into it.

    Raises InvalidAccountRequestError for an OU that:

    * has no enabled baseline: it is not registered with Control Tower, or it
      is a controls-only OU (enabled controls without a baseline), which this
      vending method does not support;
    * has BackupBaseline without AWSControlTowerBaseline, like the Security OU.

    ``ou_label`` names the OU in the error.
    """
    enabled = ct_facade.get_ou_enabled_baselines(ou_arn)
    if not enabled:
        if ct_facade.get_ou_enabled_controls(ou_arn):
            raise InvalidAccountRequestError(
                f"Organizational unit {ou_label} is a controls-only OU (enabled "
                "controls without an enabled baseline); controls-only OUs aren't "
                "supported by the organizations vending method"
            )
        raise InvalidAccountRequestError(
            f"Organizational unit {ou_label} is not registered with Control Tower"
        )
    names = set(enabled.values())
    if (
        ControlTowerFacade.BACKUP_BASELINE_NAME in names
        and ControlTowerFacade.CT_BASELINE_NAME not in names
    ):
        raise InvalidAccountRequestError(
            f"Organizational unit {ou_label} has BackupBaseline without "
            "AWSControlTowerBaseline, like the Security OU; the organizations "
            "vending method needs AWSControlTowerBaseline on the OU"
        )
    return list(enabled)


def resolve_enrollment_targets(
    ct_facade: ControlTowerFacade,
    orgs_agent: OrganizationsAgent,
    account_id: str,
    destination_ou_id: str,
) -> Dict[str, Any]:
    """Resolve the identifiers the baseline poll reads, none of which change
    during an execution: the account and destination OU ARNs, and the ARNs of
    every baseline enabled on the destination OU (AWSControlTowerBaseline and,
    for example, BackupBaseline).

    Raises InvalidAccountRequestError when AFT can't vend into the destination
    OU (see :func:`enabled_baseline_arns_for_vending`).
    """
    organization = orgs_agent.orgs_client.describe_organization()["Organization"]
    ou_arn = _organizations_arn(organization, f"ou/{destination_ou_id}")
    ou_enabled_baseline_arns = enabled_baseline_arns_for_vending(
        ct_facade, ou_arn, destination_ou_id
    )
    return {
        "account_arn": _organizations_arn(organization, f"account/{account_id}"),
        "ou_arn": ou_arn,
        "ou_enabled_baseline_arns": ou_enabled_baseline_arns,
    }


def resolve_managed_ou(
    orgs_agent: OrganizationsAgent, ct_facade: ControlTowerFacade, managed_ou_name: str
) -> str:
    """Return the id of the request's managed OU, after checking that it
    exists and that AFT can vend into it (see
    :func:`enabled_baseline_arns_for_vending`)."""
    ou_ids = orgs_agent.get_ou_ids_from_ou_names([managed_ou_name])
    if not ou_ids:
        raise InvalidAccountRequestError(
            f"Managed organizational unit '{managed_ou_name}' not found in the organization"
        )
    organization = orgs_agent.orgs_client.describe_organization()["Organization"]
    ou_arn = _organizations_arn(organization, f"ou/{ou_ids[0]}")
    enabled_baseline_arns_for_vending(ct_facade, ou_arn, f"'{managed_ou_name}'")
    return ou_ids[0]


def find_create_request_since(
    orgs_agent: OrganizationsAgent, account_name: str, since: datetime
) -> Optional[Dict[str, Any]]:
    """Return a CreateAccount request for ``account_name`` submitted at or
    after ``since`` that has not failed, preferring a SUCCEEDED one.

    Used to pick up a request this execution already submitted, for example
    when a retry submitted CreateAccount a second time.
    """
    matches = [
        request
        for request in orgs_agent.list_create_account_requests(
            ["IN_PROGRESS", "SUCCEEDED"]
        )
        if request.get("AccountName") == account_name
        and request["RequestedTimestamp"] >= since
    ]
    if not matches:
        return None
    matches.sort(
        key=lambda r: (r["State"] == "SUCCEEDED", r["RequestedTimestamp"]),
        reverse=True,
    )
    return dict(matches[0])


def _execution_start(window: Optional[Mapping[str, Any]]) -> datetime:
    start = _aware_time((window or {}).get("execution_start_time"))
    if start is None:
        raise ValueError(
            f"create_window {window} has no execution_start_time with a UTC offset"
        )
    return start


def start_create_account(
    orgs_agent: OrganizationsAgent,
    ct_facade: ControlTowerFacade,
    request: Dict[str, Any],
) -> Dict[str, Any]:
    """CreateAccount step: submit the async Organizations CreateAccount.

    The managed OU is checked first, so a request with an unknown or
    unregistered OU fails before any account exists. If this execution
    already submitted a CreateAccount for the account (a retried step), that
    request is returned instead of submitting another one. An existing
    account with the same email fails the request.

    Returns ``{"request_id": "car-...", "resumed": bool}`` to be polled by
    :func:`poll_create_account_status`.
    """
    ct_parameters = request["control_tower_parameters"]
    account_name = ct_parameters["AccountName"]
    email = ct_parameters["AccountEmail"]
    resolve_managed_ou(
        orgs_agent, ct_facade, ct_parameters["ManagedOrganizationalUnit"]
    )

    since = _execution_start(request.get("create_window"))
    existing = find_create_request_since(orgs_agent, account_name, since)
    if existing is not None:
        logger.info(
            f"Resuming CreateAccount request {sanitize_input_for_logging(existing['Id'])} for {sanitize_input_for_logging(account_name)}"
        )
        return {"request_id": existing["Id"], "resumed": True}

    if orgs_agent.get_account_by_email(email) is not None:
        raise InvalidAccountRequestError(
            "An account with this email already exists in the organization"
        )

    request_id = orgs_agent.create_account(
        email=email,
        account_name=account_name,
        role_name="AWSControlTowerExecution",
    )
    return {"request_id": request_id, "resumed": False}


def poll_create_account_status(
    orgs_agent: OrganizationsAgent,
    request_id: str,
    account_name: Optional[str] = None,
    create_window: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Poll one CreateAccount request. Returns a small dict the state machine
    branches on: ``State`` (IN_PROGRESS | SUCCEEDED | FAILED), ``AccountId``
    (when SUCCEEDED), ``FailureReason`` (when FAILED) and ``RequestId``.

    A request that failed with EMAIL_ALREADY_EXISTS can be the second of two
    submissions from the same execution. When ``account_name`` and
    ``create_window`` are given, the poll then follows the first one instead.
    """
    status: Dict[str, Any] = dict(orgs_agent.describe_create_account_status(request_id))
    if (
        status["State"] == "FAILED"
        and status.get("FailureReason") == "EMAIL_ALREADY_EXISTS"
        and account_name
        and create_window
    ):
        other = find_create_request_since(
            orgs_agent, account_name, _execution_start(create_window)
        )
        if other is not None and other["Id"] != request_id:
            logger.info(
                f"CreateAccount request {sanitize_input_for_logging(request_id)} failed with "
                f"EMAIL_ALREADY_EXISTS; following request {sanitize_input_for_logging(other['Id'])} from "
                "the same execution"
            )
            status = other
    return {
        "State": status["State"],
        "AccountId": status.get("AccountId"),
        "FailureReason": status.get("FailureReason"),
        "RequestId": status.get("Id", request_id),
    }


def move_account_to_managed_ou(
    orgs_agent: OrganizationsAgent,
    ct_facade: ControlTowerFacade,
    account_id: str,
    managed_ou_name: str,
    starting_parent_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Move the account from its current parent into its managed OU, and return
    the identifiers the baseline poll needs (see
    :func:`resolve_enrollment_targets`). Idempotent: if the account is already
    in the destination OU the move is skipped.

    ``moved`` says whether this execution moved the account, which is what
    starts Control Tower's auto-enroll. ``starting_parent_id`` is the
    account's parent when the execution started (see
    :func:`starting_parent_from_state`). With it, a retried attempt that finds
    the move already done still reports ``moved``; without it, only the
    current attempt counts.

    The destination OU must be registered with Control Tower; this is checked
    before the account is moved.
    """
    destination_ou_ids = orgs_agent.get_ou_ids_from_ou_names([managed_ou_name])
    if not destination_ou_ids:
        raise RuntimeError(
            f"Managed organizational unit '{managed_ou_name}' not found in the organization"
        )
    destination_ou_id = destination_ou_ids[0]
    targets = resolve_enrollment_targets(
        ct_facade, orgs_agent, account_id, destination_ou_id
    )
    result: Dict[str, Any] = {
        "account_id": account_id,
        "moved": False,
        "destination_ou_id": destination_ou_id,
        **targets,
    }

    current_parent_id = orgs_agent.get_parents_from_account_id(account_id)[0]["Id"]
    if current_parent_id == destination_ou_id:
        result["moved"] = (
            starting_parent_id is not None and starting_parent_id != destination_ou_id
        )
        logger.info(
            f"Account {sanitize_input_for_logging(account_id)} already in destination OU {sanitize_input_for_logging(destination_ou_id)}; "
            f"skipping move (moved by this execution: {sanitize_input_for_logging(result['moved'])})"
        )
        return result

    # The processor checked the landing zone before the execution started,
    # but CreateAccount takes minutes, so check it again before the move.
    readiness = ct_facade.get_landing_zone_readiness()
    if not readiness.is_ready:
        raise RuntimeError(
            f"{readiness.reason}; account {account_id} was not moved. Re-submit "
            "the account request once the landing zone is ACTIVE with "
            "auto-enrollment on."
        )
    orgs_agent.move_account(
        account_id=account_id,
        source_parent_id=current_parent_id,
        destination_parent_id=destination_ou_id,
    )
    result["moved"] = True
    return result


# starting_parent_from_state for an account this execution created: it starts
# in the organization root, never in its managed OU.
NEW_ACCOUNT_PARENT = "root"


def starting_parent_from_state(state: Mapping[str, Any]) -> Optional[str]:
    """The account's parent when the execution started: recorded by the UPDATE
    lookup step (``$.lookup.parent_id``), or the root for an account the
    CreateAccount steps created (``$.create_status``). None when unknown."""
    lookup = state.get("lookup") or {}
    if lookup.get("parent_id"):
        return str(lookup["parent_id"])
    if (state.get("create_status") or {}).get("AccountId"):
        return NEW_ACCOUNT_PARENT
    return None


# After the account's baseline is complete, the poll waits for Control Tower
# to list the destination OU's controls on the account until this long before
# the execution's TimeoutSeconds, so that ValidateGovernance and the lifecycle
# event publish run before the execution times out. When the wait ends with
# controls still missing or under change, the governance step reports them.
GOVERNANCE_RESERVE_SECONDS = 5 * 60
# Control statuses the poll waits on.
PENDING_CONTROL_STATUSES = frozenset({"UNDER_CHANGE"})
# A control in this status on the account is final: the poll fails the
# execution instead of waiting.
FAILED_CONTROL_STATUS = "FAILED"
# The Wait between two polls (``next_wait_seconds``) starts at
# POLL_WAIT_INITIAL_SECONDS and doubles up to POLL_WAIT_MAX_SECONDS. It starts
# again at POLL_WAIT_INITIAL_SECONDS when the baseline completes, because the
# OU's controls usually reach the account soon after. A Wait never ends more
# than POLL_WAIT_INITIAL_SECONDS after the deadline of the control wait, so
# the governance reserve holds. The cap keeps a long execution well below
# the Step Functions limit of 25,000 history events: each poll adds about 9.
POLL_WAIT_INITIAL_SECONDS = 30
POLL_WAIT_MAX_SECONDS = 5 * 60


def get_controls_inherited_from_ou(
    ct_facade: ControlTowerFacade, ou_arn: str, account_arn: str
) -> Dict[str, Optional[EnabledControlStatus]]:
    """Map each control enabled directly on the OU ``ou_arn`` to the account's
    entry for that control inherited from the OU, or None when the account
    lists none.

    An account entry counts only when its ``parentIdentifier`` is the OU's
    enabled control ARN for the same control: after an OU move the account can
    still list the control it inherited from its previous OU, which does not
    show that the destination OU's control applies to it.
    """
    ou_controls = ct_facade.get_ou_enabled_controls(ou_arn)
    inherited: Dict[str, Optional[EnabledControlStatus]] = {
        control_id: None for control_id in ou_controls
    }
    for control in ct_facade.get_account_enabled_controls(account_arn):
        expected_parent = ou_controls.get(control.control_identifier)
        if expected_parent and control.parent_identifier == expected_parent:
            inherited[control.control_identifier] = control
    return inherited


def _aware_time(value: Any) -> Optional[datetime]:
    """An ISO 8601 time with a UTC offset (or Z), else None."""
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def _complete_since(previous: Optional[Mapping[str, Any]]) -> Optional[datetime]:
    """The time a poll first saw the baseline complete, when the previous poll
    saw it complete; None otherwise."""
    if not previous or not previous.get("is_complete"):
        return None
    return _aware_time(previous.get("complete_since"))


def _controls_wait_deadline(
    poll_window: Optional[Mapping[str, Any]],
) -> Optional[datetime]:
    """GOVERNANCE_RESERVE_SECONDS before the execution's TimeoutSeconds, from
    the execution start time and timeout the state machine writes to
    ``poll_window``; None without them."""
    if poll_window is None:
        return None
    start = _aware_time(poll_window.get("execution_start_time"))
    timeout_seconds = poll_window.get("timeout_seconds")
    if start is None or not isinstance(timeout_seconds, int):
        logger.warning(
            f"poll_window {sanitize_input_for_logging(dict(poll_window))} needs an execution_start_time with "
            "a UTC offset and an integer timeout_seconds; the control wait does "
            "not end before the execution's TimeoutSeconds"
        )
        return None
    return start + timedelta(seconds=timeout_seconds - GOVERNANCE_RESERVE_SECONDS)


def _next_poll_wait_seconds(
    previous: Optional[Mapping[str, Any]],
    baseline_just_completed: bool,
    now: datetime,
    deadlines: Sequence[Optional[datetime]],
) -> int:
    """Seconds the state machine waits before the next poll (see
    POLL_WAIT_INITIAL_SECONDS)."""
    previous_wait = previous.get("next_wait_seconds") if previous else None
    if baseline_just_completed or not isinstance(previous_wait, int):
        wait = POLL_WAIT_INITIAL_SECONDS
    else:
        wait = min(
            max(previous_wait, POLL_WAIT_INITIAL_SECONDS) * 2, POLL_WAIT_MAX_SECONDS
        )
    for deadline in deadlines:
        if deadline is not None and deadline > now:
            remaining = math.ceil((deadline - now).total_seconds())
            wait = min(wait, max(remaining, POLL_WAIT_INITIAL_SECONDS))
    return wait


def get_baseline_status(
    ct_facade: ControlTowerFacade,
    account_id: str,
    destination_ou_id: str,
    targets: Mapping[str, Any],
    previous: Optional[Mapping[str, Any]] = None,
    now: Optional[datetime] = None,
    poll_window: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Read the account's Control Tower enrollment once. The state machine
    polls this with a Wait loop and passes the previous poll's result as
    ``previous`` and ``{"execution_start_time": ..., "timeout_seconds": ...}``
    as ``poll_window``. ``targets`` holds the ARNs the move step resolved (see
    :func:`resolve_enrollment_targets`), so a poll makes no Organizations calls.

    Only the baseline inherited from ``destination_ou_id`` counts: right after a
    move the account still reports its old OU's (usually SUCCEEDED) baseline,
    which would otherwise end the wait before auto-enroll has run.

    Once the baseline is complete, the poll also checks the OU's controls:
    ``controls_settled`` is True when every control enabled on the OU is listed
    on the account as inherited from the OU (see
    :func:`get_controls_inherited_from_ou`) and none of them is UNDER_CHANGE
    or FAILED. A FAILED control is final: ``failed_controls`` lists it and
    ``is_failed`` is True. ``complete_since`` is the time a poll first saw
    the baseline complete, carried forward through ``previous``.
    ``controls_wait_expired`` is True when the controls have not settled
    GOVERNANCE_RESERVE_SECONDS before the execution's TimeoutSeconds (only
    with ``poll_window``; without it, only TimeoutSeconds bounds the wait).

    ``baseline_seen_complete`` records, through ``previous``, that a poll of
    this execution saw the baseline complete. When the baseline is no longer
    complete (a later move or a baseline reset), the wait also expires at
    that deadline unless the baseline has failed, so that governance
    validation reports the incomplete baseline before the execution times
    out. Until a poll sees the baseline complete, only TimeoutSeconds bounds
    the poll loop.

    The state machine moves on to governance validation when the baseline is
    complete and the controls have settled, or when the wait has expired,
    and fails on ``is_failed``. Otherwise it waits ``next_wait_seconds``
    before the next poll (see POLL_WAIT_INITIAL_SECONDS).
    """
    ou_arn = targets["ou_arn"]
    account_arn = targets["account_arn"]
    status = ct_facade.get_account_baseline_status(
        account_arn, expected_parent_identifiers=targets["ou_enabled_baseline_arns"]
    )
    result: Dict[str, Any] = {
        "enrolled": status.enrolled,
        "operation_status": status.operation_status,
        "inheritance_drift_status": status.inheritance_drift_status,
        "is_complete": status.is_complete,
        "is_failed": status.is_failed,
        "controls_settled": False,
        "pending_control_count": None,
        "failed_controls": [],
        "complete_since": None,
        "controls_wait_seconds": 0,
        "controls_wait_expired": False,
        "baseline_seen_complete": status.is_complete
        or bool(previous and previous.get("baseline_seen_complete")),
    }
    # An account that was already in the destination OU gets no MoveAccount
    # event, so nothing starts its enrollment or remediates its inheritance
    # drift. Unless Control Tower is already working on it, waiting would only
    # end at TimeoutSeconds.
    result["enrollment_not_started"] = (
        not targets.get("moved", True)
        and not status.is_complete
        and not status.is_failed
        and status.operation_status != "UNDER_CHANGE"
        and not result["baseline_seen_complete"]
    )
    if result["enrollment_not_started"]:
        result["is_failed"] = True
        logger.error(
            f"Account {sanitize_input_for_logging(account_id)} is already in OU {sanitize_input_for_logging(destination_ou_id)} but its "
            "Control Tower enrollment is not complete and nothing is enrolling "
            f"it: baseline operation status {sanitize_input_for_logging(status.operation_status)}, "
            f"inheritance drift status {sanitize_input_for_logging(status.inheritance_drift_status)}"
        )
        return result

    now = now or datetime.now(timezone.utc)
    deadline = _controls_wait_deadline(poll_window)
    past_deadline = deadline is not None and now >= deadline
    if not status.is_complete:
        if result["baseline_seen_complete"] and past_deadline and not status.is_failed:
            result["controls_wait_expired"] = True
            logger.warning(
                f"The baseline of account {sanitize_input_for_logging(account_id)} from OU "
                f"{sanitize_input_for_logging(destination_ou_id)} is no longer complete at the execution's "
                "deadline; governance validation reports it"
            )
        result["next_wait_seconds"] = _next_poll_wait_seconds(
            previous, baseline_just_completed=False, now=now, deadlines=[deadline]
        )
        return result

    complete_since = _complete_since(previous) or now
    inherited = get_controls_inherited_from_ou(ct_facade, ou_arn, account_arn)
    pending = sorted(
        control_id
        for control_id, control in inherited.items()
        if control is None or control.status in PENDING_CONTROL_STATUSES
    )
    failed = sorted(
        control_id
        for control_id, control in inherited.items()
        if control is not None and control.status == FAILED_CONTROL_STATUS
    )
    wait_seconds = int((now - complete_since).total_seconds())
    expired = bool(pending) and not failed and past_deadline
    result.update(
        is_failed=bool(failed),
        failed_controls=failed,
        controls_settled=not pending and not failed,
        pending_control_count=len(pending),
        complete_since=complete_since.isoformat(),
        controls_wait_seconds=wait_seconds,
        controls_wait_expired=expired,
        next_wait_seconds=_next_poll_wait_seconds(
            previous,
            baseline_just_completed=_complete_since(previous) is None,
            now=now,
            deadlines=[deadline],
        ),
    )
    if failed:
        logger.error(
            f"Control Tower failed to deploy {len(failed)} control(s) of OU "
            f"{sanitize_input_for_logging(destination_ou_id)} to account {sanitize_input_for_logging(account_id)}: {sanitize_input_for_logging(failed)}"
        )
    elif not pending:
        logger.info(
            f"The {len(inherited)} control(s) of OU {sanitize_input_for_logging(destination_ou_id)} are on "
            f"account {sanitize_input_for_logging(account_id)} {wait_seconds}s after its baseline completed"
        )
    elif expired:
        logger.warning(
            f"{len(pending)} control(s) of OU {sanitize_input_for_logging(destination_ou_id)} are not on "
            f"account {sanitize_input_for_logging(account_id)} {wait_seconds}s after its baseline completed; "
            "the wait ends at the execution's deadline and governance "
            f"validation reports them: {sanitize_input_for_logging(pending)}"
        )
    else:
        logger.info(
            f"Waiting for {len(pending)} control(s) of OU {sanitize_input_for_logging(destination_ou_id)} on "
            f"account {sanitize_input_for_logging(account_id)}, {wait_seconds}s after its baseline completed"
        )
    return result


GOVERNANCE_MODE_WARN = "warn"
GOVERNANCE_MODE_FAIL = "fail"


def validate_account_governance(
    ct_facade: ControlTowerFacade,
    account_id: str,
    destination_ou_id: str,
    targets: Mapping[str, Any],
    mode: str = GOVERNANCE_MODE_WARN,
) -> Dict[str, Any]:
    """Compare what is enabled on the destination OU with what the account
    inherited from it, and report every gap. Reads the current state once.

    ``targets`` holds the ARNs the move step resolved (see
    :func:`resolve_enrollment_targets`). The expected set is every baseline
    and control enabled on the OU; the actual set is the account's entries
    inherited from the OU (matched by ``parentIdentifier``, so entries left
    over from a previous OU don't count). A gap is a baseline that is missing
    or not complete, or an OU control that is missing on the account or not in
    sync.

    Never raises on a gap; ``mode`` is returned so the caller decides whether
    a gap fails the execution.
    """
    gaps: List[Dict[str, Any]] = []

    baseline_status = ct_facade.get_account_baseline_status(
        targets["account_arn"],
        expected_parent_identifiers=targets["ou_enabled_baseline_arns"],
    )
    for parent in baseline_status.missing:
        gaps.append(
            {
                "type": "baseline",
                "parent_identifier": parent,
                "detail": "Baseline enabled on the OU is not on the account",
            }
        )
    for baseline in baseline_status.baselines:
        if not baseline.is_complete:
            gaps.append(
                {
                    "type": "baseline",
                    "baseline_identifier": baseline.baseline_identifier,
                    "detail": (
                        f"Baseline not complete on the account "
                        f"(status={baseline.status}, "
                        f"inheritance={baseline.inheritance_drift_status})"
                    ),
                }
            )

    inherited = get_controls_inherited_from_ou(
        ct_facade, targets["ou_arn"], targets["account_arn"]
    )
    for control_id in sorted(inherited):
        control = inherited[control_id]
        if control is None:
            gaps.append(
                {
                    "type": "control",
                    "control_identifier": control_id,
                    "detail": "Control enabled on the OU is not on the account",
                }
            )
        elif not control.is_in_sync:
            gaps.append(
                {
                    "type": "control",
                    "control_identifier": control_id,
                    "detail": (
                        f"Control not in sync on the account "
                        f"(status={control.status}, drift={control.drift_status})"
                    ),
                }
            )

    compliant = not gaps
    logger.info(
        f"Governance validation for account {sanitize_input_for_logging(account_id)} in OU "
        f"{sanitize_input_for_logging(destination_ou_id)}: compliant={compliant}, gaps={len(gaps)}, mode={sanitize_input_for_logging(mode)}"
    )
    return {"compliant": compliant, "gaps": gaps, "mode": mode}


# A Region whose EC2 endpoint cannot be reached is skipped rather than failing
# the whole deletion (same set the AFT management account deletion skips).
UNREACHABLE_REGION_ERRORS = (
    EndpointConnectionError,
    ConnectTimeoutError,
    ReadTimeoutError,
)

# EC2 client settings for the default VPC deletion. botocore's defaults (a 60 s
# connect timeout, 5 attempts) let one unreachable Region take about 5 minutes,
# the whole Lambda timeout; these keep it to seconds, so the remaining Regions
# still run.
DEFAULT_VPC_CONNECT_TIMEOUT_SECONDS = 5
DEFAULT_VPC_READ_TIMEOUT_SECONDS = 30
DEFAULT_VPC_MAX_ATTEMPTS = 3


def default_vpc_botoconfig() -> Config:
    return Config(
        connect_timeout=DEFAULT_VPC_CONNECT_TIMEOUT_SECONDS,
        read_timeout=DEFAULT_VPC_READ_TIMEOUT_SECONDS,
        retries={"total_max_attempts": DEFAULT_VPC_MAX_ATTEMPTS, "mode": "standard"},
    )


# DescribeRegions OptInStatus values of a Region the account can use. A
# governed opt-in Region stays "not-opted-in" for a new account until Control
# Tower enables it during enrollment, and its default VPC only exists then.
ENABLED_OPT_IN_STATUSES = frozenset({"opt-in-not-required", "opted-in"})

# How long, from the execution start, the default VPC deletion waits for
# governed Regions not enabled for the account yet, and for Regions where EC2
# failed: while it returns pending, the state machine runs it again every 60 s.
# The deletion runs before the baseline poll, so its time comes out of the
# poll's wait, not out of GOVERNANCE_RESERVE_SECONDS.
DEFAULT_VPC_REGION_WAIT_SECONDS = 30 * 60


class DefaultVpcDeletionError(Exception):
    """The default VPC deletion failed in one or more Regions."""


def _error_code(error: Exception) -> str:
    if isinstance(error, ClientError):
        return str(error.response.get("Error", {}).get("Code", "Unknown"))
    return type(error).__name__


def split_regions_by_opt_in(
    target_account_session: Session, regions: List[str]
) -> Tuple[List[str], List[str]]:
    """Split *regions* into ``(enabled, not_enabled)`` for the account
    *target_account_session* belongs to, keeping their order, with one EC2
    DescribeRegions call in the session's own Region.

    A Region the response does not list counts as not enabled, and one listed
    without an OptInStatus as enabled. When the call fails, for example
    because the session's Region is an opt-in Region not enabled for the
    account yet, every Region counts as not enabled.
    """
    try:
        client = target_account_session.client("ec2", config=default_vpc_botoconfig())
        listed = client.describe_regions(AllRegions=True, RegionNames=regions)[
            "Regions"
        ]
    except (ClientError,) + UNREACHABLE_REGION_ERRORS as error:
        logger.warning(
            f"Could not read the opt-in status of {sanitize_input_for_logging(regions)} "
            f"({sanitize_input_for_logging(_error_code(error))}); treating them as not "
            "enabled for the account yet"
        )
        return [], list(regions)
    status = {
        region["RegionName"]: region.get("OptInStatus", "opt-in-not-required")
        for region in listed
    }
    enabled = [
        region for region in regions if status.get(region) in ENABLED_OPT_IN_STATUSES
    ]
    not_enabled = [region for region in regions if region not in enabled]
    return enabled, not_enabled


def is_region_disabled_error(error: Exception) -> bool:
    """True for the error STS AssumeRole returns when the Region of its
    endpoint is an opt-in Region not enabled for the account that owns the
    role: for a new account, the landing zone's home Region when it is an
    opt-in Region, until Control Tower enables it during enrollment."""
    return (
        isinstance(error, ClientError)
        and _error_code(error) == "RegionDisabledException"
    )


def regions_not_enabled_result(regions: List[str]) -> Dict[str, Any]:
    """The delete_default_vpcs_in_account result for an account that cannot
    be reached yet: every Region in ``not_enabled`` and nothing touched, as
    when DescribeRegions fails."""
    return {
        "deleted": {},
        "absent": [],
        "unreachable": [],
        "not_enabled": list(regions),
        "failed": {},
    }


def default_vpc_wait_pending(
    waiting_regions: Sequence[str],
    create_window: Optional[Mapping[str, Any]],
    now: Optional[datetime] = None,
) -> bool:
    """True while *waiting_regions* (not enabled for the account yet, or
    where the deletion failed) lists Regions and less than
    DEFAULT_VPC_REGION_WAIT_SECONDS have passed since the execution started
    (``$.create_window``): the state machine then runs the deletion again."""
    if not waiting_regions:
        return False
    now = now or datetime.now(timezone.utc)
    return now < _execution_start(create_window) + timedelta(
        seconds=DEFAULT_VPC_REGION_WAIT_SECONDS
    )


def find_default_vpc(client: EC2Client) -> Optional[str]:
    """The id of the default VPC of *client*'s Region, or None when it has
    none. Errors raise; unlike feature_options.get_default_vpc, a failed call
    is never taken for a Region without a default VPC."""
    vpcs = client.describe_vpcs(Filters=[{"Name": "isDefault", "Values": ["true"]}])[
        "Vpcs"
    ]
    # A Region has at most one default VPC.
    return str(vpcs[0]["VpcId"]) if vpcs else None


def _deletion_error_message(
    failed: Mapping[str, str], unreachable: List[str], not_enabled: List[str]
) -> str:
    message = "Default VPC deletion failed in: " + ", ".join(
        f"{region} ({code})" for region, code in sorted(failed.items())
    )
    if unreachable:
        message += ". Skipped, EC2 endpoint unreachable: " + ", ".join(unreachable)
    if not_enabled:
        message += ". Not enabled for the account yet: " + ", ".join(not_enabled)
    return message


def delete_default_vpcs_in_account(
    target_account_session: Session, regions: List[str]
) -> Dict[str, Any]:
    """Delete the default VPC, and the resources AWS creates with it, in each
    of *regions* that is enabled for the account *target_account_session*
    belongs to. The Regions not enabled for it yet (split_regions_by_opt_in)
    are returned in ``not_enabled`` and not touched.

    Best effort per Region, like the AFT management account deletion: a Region
    whose EC2 endpoint is unreachable is reported in ``unreachable``, logged as
    a warning, and the remaining Regions are still processed. An error from
    EC2 in a Region does not stop the remaining Regions either: the Region and
    its error code are reported in ``failed``, and raise_for_failed_regions
    raises for them once the caller stops waiting. A later run finds no
    default VPC in the Regions already done and reports them in ``absent``.
    Any other exception raises at once.

    Returns ``{"deleted": {region: vpc_id}, "absent": [...], "unreachable": [...],
    "not_enabled": [...], "failed": {region: error_code}}``.
    """
    enabled, not_enabled = split_regions_by_opt_in(target_account_session, regions)
    deleted: Dict[str, str] = {}
    absent: List[str] = []
    unreachable: List[str] = []
    failed: Dict[str, str] = {}
    for region in enabled:
        try:
            client = target_account_session.client(
                "ec2", region_name=region, config=default_vpc_botoconfig()
            )
            vpc = find_default_vpc(client)
            if vpc is None:
                logger.info(f"No default VPC in {sanitize_input_for_logging(region)}")
                absent.append(region)
                continue
            resource = target_account_session.resource(
                "ec2", region_name=region, config=default_vpc_botoconfig()
            )
            subnets = get_vpc_subnets(resource, vpc)
            route_tables = get_vpc_route_tables(resource, vpc)
            acls = get_vpc_acls(resource, vpc)
            security_groups = get_vpc_security_groups(resource, vpc)
            internet_gateways = get_vpc_internet_gateways(resource, vpc)
            delete_internet_gateways(client, internet_gateways, vpc)
            delete_subnets(client, subnets)
            delete_route_tables(client, route_tables)
            delete_acls(client, acls)
            delete_security_groups(client, security_groups)
            delete_vpc(client, vpc)
            logger.info(
                f"Deleted default VPC {sanitize_input_for_logging(vpc)} in {sanitize_input_for_logging(region)}"
            )
            deleted[region] = vpc
        except UNREACHABLE_REGION_ERRORS as region_error:
            logger.warning(
                f"Skipping default VPC deletion in {sanitize_input_for_logging(region)}: endpoint unreachable "
                f"({type(region_error).__name__})"
            )
            unreachable.append(region)
        except ClientError as region_error:
            failed[region] = _error_code(region_error)
            logger.warning(
                f"Default VPC deletion failed in {sanitize_input_for_logging(region)} "
                f"({sanitize_input_for_logging(failed[region])}); continuing with the "
                "remaining Regions"
            )
    return {
        "deleted": deleted,
        "absent": absent,
        "unreachable": unreachable,
        "not_enabled": not_enabled,
        "failed": failed,
    }


def raise_for_failed_regions(result: Mapping[str, Any]) -> None:
    """Raise one DefaultVpcDeletionError naming every Region in the ``failed``
    of a delete_default_vpcs_in_account *result* and its error code, plus the
    Regions skipped or not enabled, so the caller can retry. Does nothing when
    no Region failed."""
    if result["failed"]:
        raise DefaultVpcDeletionError(
            _deletion_error_message(
                result["failed"], result["unreachable"], result["not_enabled"]
            )
        )


def lookup_account_by_email(
    orgs_agent: OrganizationsAgent, request: Dict[str, Any]
) -> Dict[str, Any]:
    """UPDATE step: find the existing account by its email.

    The Organizations vending method has no provisioned product to update, so
    an UPDATE is resolved to an account id by Organizations lookup. Raises if
    the account does not exist (an UPDATE for a non-existent account is
    invalid).

    Also records the account's parent before the execution moves it
    (``parent_id``): the move step compares it with the destination OU to tell
    whether this execution moved the account, even when a retried attempt
    finds the move already done.
    """
    email = request["control_tower_parameters"]["AccountEmail"]
    account = orgs_agent.get_account_by_email(email)
    if account is None:
        raise RuntimeError(
            f"Account email {email} not found in Organization; cannot UPDATE"
        )
    parent_id = orgs_agent.get_parents_from_account_id(account["Id"])[0]["Id"]
    return {"account_id": account["Id"], "parent_id": parent_id}


def resolve_account_id_from_state(state: Dict[str, Any]) -> str:
    """Resolve the account id from the state machine state, supporting both
    branches: the UPDATE lookup result (``$.lookup.account_id``) and the
    CreateAccount status (``$.create_status.AccountId``). The lookup result is
    preferred when present.
    """
    lookup = state.get("lookup") or {}
    if lookup.get("account_id"):
        return str(lookup["account_id"])
    return str(state["create_status"]["AccountId"])


def build_lifecycle_event_detail(
    operation: str,
    account_id: str,
    account_name: Optional[str] = None,
    organizational_unit_name: Optional[str] = None,
    organizational_unit_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a Control-Tower-shaped event Detail for a provisioned account.

    AFT's own consumers only read ``detail.eventName`` and
    ``detail.serviceEventDetails.<create|update>ManagedAccountStatus.account.accountId``.
    But the whole event is also passed verbatim to customers'
    aft-account-provisioning-customizations as ``control_tower_event``, so we
    populate the same ``account`` and ``organizationalUnit`` fields a real
    Control Tower event carries, to the extent the provisioning flow knows them.
    Fields that are unknown are omitted rather than sent empty.
    """
    if operation == "ADD":
        event_name = "CreateManagedAccount"
        status_key = "createManagedAccountStatus"
    elif operation == "UPDATE":
        event_name = "UpdateManagedAccount"
        status_key = "updateManagedAccountStatus"
    else:
        raise RuntimeError(f"Unsupported operation for lifecycle event: {operation}")

    account: Dict[str, str] = {"accountId": account_id}
    if account_name is not None:
        account["accountName"] = account_name

    status: Dict[str, Any] = {"account": account, "state": "SUCCEEDED"}

    if organizational_unit_name is not None or organizational_unit_id is not None:
        organizational_unit: Dict[str, str] = {}
        if organizational_unit_name is not None:
            organizational_unit["organizationalUnitName"] = organizational_unit_name
        if organizational_unit_id is not None:
            organizational_unit["organizationalUnitId"] = organizational_unit_id
        status["organizationalUnit"] = organizational_unit

    return {
        "eventName": event_name,
        "serviceEventDetails": {status_key: status},
    }


def publish_lifecycle_event(
    session: Session,
    event_bus_name: str,
    operation: str,
    account_id: str,
    account_name: Optional[str] = None,
    organizational_unit_name: Optional[str] = None,
    organizational_unit_id: Optional[str] = None,
) -> None:
    """Publish an ``aft.organizations`` lifecycle event onto the AFT event bus.

    The event mimics a Control Tower CreateManagedAccount / UpdateManagedAccount
    event (Detail shape via :func:`build_lifecycle_event_detail`) but carries
    ``Source = "aft.organizations"`` so a dedicated EventBridge rule routes it to
    the same logger + provisioning-framework targets.

    PutEvents does not raise when EventBridge rejects an entry (throttling, an
    internal error): it returns ``FailedEntryCount > 0``. We raise in that case
    so the Step Function's Retry/Catch handles it, rather than reporting success
    while the event was silently dropped and customizations never run.
    """
    detail = build_lifecycle_event_detail(
        operation=operation,
        account_id=account_id,
        account_name=account_name,
        organizational_unit_name=organizational_unit_name,
        organizational_unit_id=organizational_unit_id,
    )
    client = session.client("events")
    logger.info(
        f"Publishing aft.organizations lifecycle event {sanitize_input_for_logging(detail['eventName'])} "
        f"for account {sanitize_input_for_logging(account_id)}"
    )
    response = client.put_events(
        Entries=[
            {
                "Source": ORGANIZATIONS_LIFECYCLE_EVENT_SOURCE,
                "DetailType": ORGANIZATIONS_LIFECYCLE_EVENT_DETAIL_TYPE,
                "Detail": json.dumps(detail),
                "EventBusName": event_bus_name,
            }
        ]
    )
    failed_count = response.get("FailedEntryCount", 0)
    if failed_count:
        entries = response.get("Entries", [{}])
        error_code = entries[0].get("ErrorCode", "Unknown")
        error_message = entries[0].get("ErrorMessage", "")
        raise RuntimeError(
            f"PutEvents rejected the aft.organizations lifecycle event for "
            f"account {account_id}: {error_code} {error_message}"
        )
