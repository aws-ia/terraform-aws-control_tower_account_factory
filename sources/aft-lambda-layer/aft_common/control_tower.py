# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Tuple

from aft_common.aft_utils import (
    get_high_retry_botoconfig,
    sanitize_input_for_logging,
    yield_from_paginated_api,
)
from boto3.session import Session

if TYPE_CHECKING:
    from mypy_boto3_controltower import ControlTowerClient
    from mypy_boto3_controltower.type_defs import EnabledBaselineSummaryTypeDef
else:
    ControlTowerClient = object
    EnabledBaselineSummaryTypeDef = object

logger = logging.getLogger("aft")


@dataclass(frozen=True)
class EnabledBaselineStatus:
    """Snapshot of one Control Tower baseline as it applies to a member account.

    ``baseline_identifier`` is the baseline ARN (e.g. AWSControlTowerBaseline or
    BackupBaseline). ``status`` is the operation status (SUCCEEDED |
    UNDER_CHANGE | FAILED) and ``inheritance_drift_status`` the inheritance
    drift state (IN_SYNC when the account matches the baseline enabled on its
    OU). ``parent_identifier`` is the ARN of the OU's enabled baseline the
    account inherits this one from.
    """

    baseline_identifier: str
    status: Optional[str] = None
    inheritance_drift_status: Optional[str] = None
    parent_identifier: Optional[str] = None

    @property
    def is_complete(self) -> bool:
        return self.status == "SUCCEEDED" and self.inheritance_drift_status == "IN_SYNC"

    @property
    def is_failed(self) -> bool:
        return self.status == "FAILED"


@dataclass(frozen=True)
class AccountBaselineStatus:
    """Control Tower baseline enrollment of an account, across every baseline
    it inherits from its OU.

    ``baselines`` holds one entry per inherited baseline. ``missing`` lists the
    OU enabled-baseline ARNs that were expected but are not yet on the account.
    The account is enrolled once every expected baseline is present, complete
    once all of them are SUCCEEDED and IN_SYNC, and failed if any one failed.
    None of this covers the OU's controls: right after auto-enrollment an
    account can report complete before Control Tower lists the OU's controls
    on it.
    """

    baselines: Tuple[EnabledBaselineStatus, ...] = ()
    missing: Tuple[str, ...] = ()

    @property
    def enrolled(self) -> bool:
        return bool(self.baselines) and not self.missing

    @property
    def is_complete(self) -> bool:
        return self.enrolled and all(b.is_complete for b in self.baselines)

    @property
    def is_failed(self) -> bool:
        return any(b.is_failed for b in self.baselines)

    @property
    def operation_status(self) -> Optional[str]:
        """Combined status: FAILED or UNDER_CHANGE if any baseline is, SUCCEEDED
        if all are, None if the account has no inherited baseline."""
        statuses = {b.status for b in self.baselines}
        for status in ("FAILED", "UNDER_CHANGE"):
            if status in statuses:
                return status
        if statuses == {"SUCCEEDED"}:
            return "SUCCEEDED"
        return None

    @property
    def inheritance_drift_status(self) -> Optional[str]:
        """Combined inheritance drift: IN_SYNC only if every baseline is,
        otherwise the first other status seen."""
        drift = [b.inheritance_drift_status for b in self.baselines]
        if drift and all(d == "IN_SYNC" for d in drift):
            return "IN_SYNC"
        return next((d for d in drift if d != "IN_SYNC"), None)


@dataclass(frozen=True)
class EnabledControlStatus:
    """Snapshot of one Control Tower control as it applies to a target
    (an OU or a member account).

    ``control_identifier`` is the control ARN. ``status`` is the control's
    operation status (SUCCEEDED | UNDER_CHANGE | FAILED) and ``drift_status``
    its drift status (IN_SYNC | DRIFTED | NOT_CHECKING | UNKNOWN). Only DRIFTED
    counts as a gap. ``parent_identifier`` is, for a control an account
    inherits from an OU, the ARN of the OU's enabled control it comes from;
    None for a control enabled directly on the target.
    """

    control_identifier: str
    status: Optional[str] = None
    drift_status: Optional[str] = None
    parent_identifier: Optional[str] = None

    @property
    def is_in_sync(self) -> bool:
        """True when the control's status is SUCCEEDED and its drift status is
        not DRIFTED."""
        return self.status == "SUCCEEDED" and self.drift_status != "DRIFTED"


@dataclass(frozen=True)
class LandingZoneReadiness:
    """The landing zone state that decides whether AFT can vend an account
    now: AFT moves accounts only while the landing zone's ``status`` is ACTIVE
    and auto-enrollment is on."""

    ACTIVE_STATUS = "ACTIVE"
    PROCESSING_STATUS = "PROCESSING"

    exists: bool
    status: Optional[str] = None
    auto_enroll_enabled: bool = False

    @property
    def is_ready(self) -> bool:
        return (
            self.exists
            and self.status == self.ACTIVE_STATUS
            and self.auto_enroll_enabled
        )

    @property
    def is_updating(self) -> bool:
        """The landing zone is being updated or reset; it becomes ACTIVE again
        without an operator."""
        return self.exists and self.status == self.PROCESSING_STATUS

    @property
    def reason(self) -> Optional[str]:
        """Why AFT can't vend an account now; None when it can."""
        if not self.exists:
            return "No Control Tower landing zone found"
        if self.status != self.ACTIVE_STATUS:
            return (
                f"The Control Tower landing zone is {self.status}, not "
                f"{self.ACTIVE_STATUS}; AFT vends accounts only while it is "
                f"{self.ACTIVE_STATUS}"
            )
        if not self.auto_enroll_enabled:
            return (
                "Control Tower account auto-enrollment is off on the landing zone "
                "(remediationTypes has no INHERITANCE_DRIFT)"
            )
        return None


class ControlTowerFacade:
    CT_BASELINE_NAME = "AWSControlTowerBaseline"
    BACKUP_BASELINE_NAME = "BackupBaseline"

    def __init__(self, ct_management_session: Session):
        self.ct_client: ControlTowerClient = ct_management_session.client(
            "controltower", config=get_high_retry_botoconfig()
        )
        # Memoize the baseline ARN since it won't change during a Lambda invocation
        self._ct_baseline_arn: Optional[str] = None
        self._baseline_names: Optional[Dict[str, str]] = None

    @property
    def ct_baseline_arn(self) -> str:
        """
        Discovers the AWSControlTowerBaseline ARN via the ListBaselines API.
        The result is cached for the lifetime of this instance.
        """
        if self._ct_baseline_arn is not None:
            return self._ct_baseline_arn

        for baseline in yield_from_paginated_api(
            self.ct_client, "list_baselines", result_key="baselines"
        ):
            if baseline["name"] == self.CT_BASELINE_NAME:
                self._ct_baseline_arn = baseline["arn"]
                return self._ct_baseline_arn

        raise Exception(f"Control Tower baseline '{self.CT_BASELINE_NAME}' not found")

    def list_enabled_baselines(
        self,
        baseline_identifiers: Optional[List[str]] = None,
        target_identifiers: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
        include_children: bool = False,
    ) -> List[EnabledBaselineSummaryTypeDef]:
        """
        Lists enabled baselines with optional filters for baseline identifiers,
        target identifiers, and statuses. Handles pagination automatically.

        ``include_children`` also returns the account-level baselines that an
        OU's baseline extends to its member accounts. Without it, accounts
        enrolled through their OU are not returned at all.
        """
        filter_params = {
            k: v
            for k, v in {
                "baselineIdentifiers": baseline_identifiers,
                "targetIdentifiers": target_identifiers,
                "statuses": statuses,
            }.items()
            if v
        }
        kwargs: Dict[str, Any] = {"filter": filter_params} if filter_params else {}
        if include_children:
            kwargs["includeChildren"] = True

        return list(
            yield_from_paginated_api(
                self.ct_client,
                "list_enabled_baselines",
                result_key="enabledBaselines",
                **kwargs,
            )
        )

    def get_enabled_baselines_under_change_count(self) -> int:
        """
        Returns the count of enabled CT baselines currently in UNDER_CHANGE status.
        This is used to determine if the concurrent account provisioning threshold
        has been reached.
        """
        enabled_baselines = self.list_enabled_baselines(
            baseline_identifiers=[self.ct_baseline_arn],
            statuses=["UNDER_CHANGE"],
        )
        count = len(enabled_baselines)
        logger.info(f"Found {count} CT baselines currently UNDER_CHANGE")
        return count

    AUTO_ENROLL_REMEDIATION_TYPE = "INHERITANCE_DRIFT"

    def _get_landing_zone(self) -> Optional[Dict[str, Any]]:
        """Return GetLandingZone's ``landingZone`` object for the organization's
        landing zone, or None when no landing zone exists."""
        landing_zones = list(
            yield_from_paginated_api(
                self.ct_client, "list_landing_zones", result_key="landingZones"
            )
        )
        if not landing_zones:
            return None
        landing_zone: Dict[str, Any] = self.ct_client.get_landing_zone(
            landingZoneIdentifier=landing_zones[0]["arn"]
        )["landingZone"]
        return landing_zone

    def get_governed_regions(self) -> List[str]:
        """Return the Regions the landing zone governs (``manifest.governedRegions``).

        :raises RuntimeError: if the organization has no landing zone, or the
            landing zone manifest lists no governed Regions.
        """
        landing_zone = self._get_landing_zone()
        if landing_zone is None:
            raise RuntimeError("No Control Tower landing zone found")
        regions: List[str] = list(
            (landing_zone.get("manifest") or {}).get("governedRegions") or []
        )
        if not regions:
            raise RuntimeError("The landing zone manifest lists no governed Regions")
        logger.info(
            f"Landing zone governed Regions: {sanitize_input_for_logging(regions)}"
        )
        return regions

    def get_landing_zone_readiness(self) -> "LandingZoneReadiness":
        """Return the landing zone's ``status`` and whether auto-enrollment is
        on (see :class:`LandingZoneReadiness`)."""
        landing_zone = self._get_landing_zone()
        if landing_zone is None:
            logger.info("Landing zone pre-flight: no landing zone found")
            return LandingZoneReadiness(exists=False)

        remediation_types = landing_zone.get("remediationTypes") or []
        readiness = LandingZoneReadiness(
            exists=True,
            status=landing_zone.get("status"),
            auto_enroll_enabled=self.AUTO_ENROLL_REMEDIATION_TYPE in remediation_types,
        )
        logger.info(
            f"Landing zone pre-flight: status={readiness.status}, "
            f"remediationTypes={remediation_types}, "
            f"auto_enroll_enabled={readiness.auto_enroll_enabled}"
        )
        return readiness

    def get_baseline_names(self) -> Dict[str, str]:
        """Map each baseline ARN (``baselineIdentifier``) to its name, for
        example AWSControlTowerBaseline or BackupBaseline. Cached for the
        lifetime of this instance."""
        if self._baseline_names is None:
            self._baseline_names = {
                str(baseline["arn"]): str(baseline["name"])
                for baseline in yield_from_paginated_api(
                    self.ct_client, "list_baselines", result_key="baselines"
                )
            }
        return self._baseline_names

    def get_ou_enabled_baselines(self, ou_arn: str) -> Dict[str, str]:
        """Map the ARN of each baseline enabled on an OU (for example
        AWSControlTowerBaseline and BackupBaseline; its member accounts inherit
        each one) to the name of the baseline it enables (see
        :meth:`get_baseline_names`)."""
        names = self.get_baseline_names()
        return {
            str(enabled["arn"]): names.get(
                str(enabled.get("baselineIdentifier")),
                str(enabled.get("baselineIdentifier")),
            )
            for enabled in self.list_enabled_baselines(target_identifiers=[ou_arn])
        }

    def get_account_enabled_baselines(
        self, account_target_identifier: str
    ) -> List[EnabledBaselineStatus]:
        """Return every baseline an account inherits from its OU."""
        baselines = []
        for baseline in self.list_enabled_baselines(
            target_identifiers=[account_target_identifier],
            include_children=True,
        ):
            if not baseline.get("parentIdentifier"):
                continue
            baselines.append(
                EnabledBaselineStatus(
                    baseline_identifier=str(baseline.get("baselineIdentifier")),
                    status=baseline.get("statusSummary", {}).get("status"),
                    inheritance_drift_status=baseline.get("driftStatusSummary", {})
                    .get("types", {})
                    .get("inheritance", {})
                    .get("status"),
                    parent_identifier=baseline.get("parentIdentifier"),
                )
            )
        return baselines

    def get_account_baseline_status(
        self,
        account_target_identifier: str,
        expected_parent_identifiers: Optional[Sequence[str]] = None,
    ) -> AccountBaselineStatus:
        """Return the Control Tower baseline enrollment status for one account.

        ``account_target_identifier`` is the account's Organizations ARN
        (e.g. ``arn:aws:organizations::<mgmt>:account/<org-id>/<account-id>``).

        ``expected_parent_identifiers`` are the enabled-baseline ARNs of the OU
        the account was moved to (see :meth:`get_ou_enabled_baselines`).
        Only baselines inherited from those count, and the account is not
        enrolled until it has all of them. Right after a move the account still
        lists the baselines of its old OU; this ignores them. Without it, every
        baseline the account inherits counts.
        """
        baselines = self.get_account_enabled_baselines(account_target_identifier)
        missing: Tuple[str, ...] = ()
        if expected_parent_identifiers is not None:
            expected = set(expected_parent_identifiers)
            baselines = [b for b in baselines if b.parent_identifier in expected]
            seen = {b.parent_identifier for b in baselines}
            missing = tuple(sorted(expected - seen))

        status = AccountBaselineStatus(baselines=tuple(baselines), missing=missing)
        logger.info(
            f"Baseline status for {account_target_identifier}: "
            f"operation={status.operation_status}, "
            f"inheritance={status.inheritance_drift_status}, "
            f"baselines={len(baselines)}, missing={len(missing)}"
        )
        return status

    def list_enabled_controls(
        self,
        target_identifier: str,
        include_children: bool = False,
    ) -> List[Dict[str, Any]]:
        """List the controls enabled on a target (an OU ARN or an account ARN).

        ``include_children`` also returns the account-level controls that an OU's
        controls extend to its member accounts — the same inheritance mechanism
        baselines use. Without it, controls inherited by an account through its OU
        are not returned when the target is the account.

        Returns the raw ``enabledControls`` summaries (each carries
        ``controlIdentifier``, ``statusSummary.status``,
        ``driftStatusSummary.driftStatus`` and ``parentIdentifier``). Pagination
        is handled automatically.
        """
        kwargs: Dict[str, Any] = {"targetIdentifier": target_identifier}
        if include_children:
            kwargs["includeChildren"] = True
        return list(
            yield_from_paginated_api(
                self.ct_client,
                "list_enabled_controls",
                result_key="enabledControls",
                **kwargs,
            )
        )

    def get_ou_enabled_controls(self, ou_arn: str) -> Dict[str, str]:
        """Return ``{control identifier: enabled control ARN}`` for the controls
        enabled directly on an OU — the governance posture a member account is
        expected to inherit. A member account lists each one as an entry whose
        ``parentIdentifier`` is the OU's enabled control ARN.
        """
        return {
            str(control["controlIdentifier"]): str(control.get("arn") or "")
            for control in self.list_enabled_controls(ou_arn)
            if control.get("controlIdentifier")
        }

    def get_account_enabled_controls(
        self,
        account_target_identifier: str,
    ) -> List[EnabledControlStatus]:
        """Return the controls an account has inherited, with each control's
        status and drift — the *actual* governance posture of the account.

        ``account_target_identifier`` is the account's Organizations ARN
        (``arn:<partition>:organizations::<mgmt>:account/<org-id>/<account-id>``).
        ``include_children`` is set so OU-inherited controls are returned for the
        account target, mirroring :meth:`get_account_baseline_status`. Each
        entry carries its ``parentIdentifier``: right after an OU move the
        account can still list controls inherited from its previous OU.
        """
        controls = []
        for control in self.list_enabled_controls(
            account_target_identifier, include_children=True
        ):
            drift_status = control.get("driftStatusSummary", {}).get("driftStatus")
            controls.append(
                EnabledControlStatus(
                    control_identifier=str(control.get("controlIdentifier")),
                    status=control.get("statusSummary", {}).get("status"),
                    drift_status=drift_status,
                    parent_identifier=control.get("parentIdentifier"),
                )
            )
        return controls
