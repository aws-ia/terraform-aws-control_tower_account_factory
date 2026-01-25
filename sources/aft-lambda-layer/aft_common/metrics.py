# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import argparse
import logging
from datetime import datetime
from typing import Any, Dict, Optional, TypedDict

import aft_common.constants
import requests
from aft_common import aft_utils as utils
from aft_common.auth import AuthClient
from aft_common.ssm import get_ssm_parameter_value
from boto3.session import Session

logger = logging.getLogger("aft")


class MetricsPayloadType(TypedDict):
    Solution: str
    TimeStamp: str
    Version: Optional[str]
    UUID: Optional[str]
    Account_id: Optional[str]
    Data: Dict[str, Any]


class AFTMetrics:
    def __init__(self) -> None:
        self.solution_id = "SO0089-aft"
        self.api_endpoint = "https://metrics.awssolutionsbuilder.com/generic"
        self.auth = AuthClient()

    def _get_uuid(self, aft_management_session: Session) -> str:
        uuid = get_ssm_parameter_value(
            aft_management_session,
            aft_common.constants.SSM_PARAM_AFT_METRICS_REPORTING_UUID,
        )
        return uuid

    def _metrics_reporting_enabled(self, aft_management_session: Session) -> bool:
        flag = get_ssm_parameter_value(
            aft_management_session, aft_common.constants.SSM_PARAM_AFT_METRICS_REPORTING
        )

        if flag.lower() == "true":
            return True
        return False

    def _get_aft_deployment_config(
        self, aft_management_session: Session
    ) -> Dict[str, str]:
        config = {}

        config["cloud_trail_enabled"] = get_ssm_parameter_value(
            aft_management_session,
            aft_common.constants.SSM_PARAM_FEATURE_CLOUDTRAIL_DATA_EVENTS_ENABLED,
        )
        config["enterprise_support_enabled"] = get_ssm_parameter_value(
            aft_management_session,
            aft_common.constants.SSM_PARAM_FEATURE_ENTERPRISE_SUPPORT_ENABLED,
        )
        config["delete_default_vpc_enabled"] = get_ssm_parameter_value(
            aft_management_session,
            aft_common.constants.SSM_PARAM_FEATURE_DEFAULT_VPCS_ENABLED,
        )

        config["aft_version"] = get_ssm_parameter_value(
            aft_management_session, aft_common.constants.SSM_PARAM_ACCOUNT_AFT_VERSION
        )

        config["terraform_version"] = get_ssm_parameter_value(
            aft_management_session,
            aft_common.constants.SSM_PARAM_ACCOUNT_TERRAFORM_VERSION,
        )

        config["region"] = utils.get_session_info(aft_management_session)["region"]

        config["ct_management_account_id"] = get_ssm_parameter_value(
            aft_management_session,
            aft_common.constants.SSM_PARAM_ACCOUNT_CT_MANAGEMENT_ACCOUNT_ID,
        )

        return config

    def wrap_event_for_api(
        self, aft_management_session: Session, event: Dict[str, Any]
    ) -> MetricsPayloadType:
        payload: MetricsPayloadType = {
            "Solution": self.solution_id,
            "TimeStamp": datetime.now(tz=None).isoformat(timespec="seconds"),
            "Version": None,
            "UUID": None,
            "Account_id": None,
            "Data": {},
        }
        payload["Solution"] = self.solution_id

        data_body: Dict[str, Any] = {}
        data_body["event"] = event

        errors = []

        try:
            payload["Version"] = get_ssm_parameter_value(
                aft_management_session,
                aft_common.constants.SSM_PARAM_ACCOUNT_AFT_VERSION,
            )
        except Exception as e:
            payload["Version"] = None
            errors.append(str(e))

        try:
            payload["UUID"] = self._get_uuid(aft_management_session)
        except Exception as e:
            payload["UUID"] = None
            errors.append(str(e))
        try:
            payload["Account_id"] = get_ssm_parameter_value(
                aft_management_session,
                aft_common.constants.SSM_PARAM_ACCOUNT_AFT_MANAGEMENT_ACCOUNT_ID,
            )
        except Exception as e:
            payload["Account_id"] = None
            errors.append(str(e))
        try:
            data_body["config"] = self._get_aft_deployment_config(
                aft_management_session
            )
        except Exception as e:
            data_body["config"] = None
            errors.append(str(e))

        if not errors:
            data_body["error"] = None
        else:
            data_body["error"] = " | ".join(errors)

        payload["Data"] = data_body

        return payload

    def post_event(self, action: str, status: Optional[str] = None) -> None:
        aft_management_session = self.auth.get_aft_management_session()

        if self._metrics_reporting_enabled(aft_management_session):
            event = {"action": action, "status": status}

            payload = self.wrap_event_for_api(aft_management_session, event)

            response = requests.post(self.api_endpoint, json=payload)

        return None


# Executes when run as a script from the CodeBuild containers
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script called from within CodeBuild containers to report back AFT usage metrics"
    )

    parser.add_argument(
        "--codebuild-name", type=str, help="Name of the build container"
    )
    parser.add_argument(
        "--codebuild-status",
        type=int,
        help="Whether the build succeeded or not (1 or 0)",
    )

    args = parser.parse_args()

    codebuild_name = args.codebuild_name
    codebuild_status = "SUCCEEDED" if args.codebuild_status == 1 else "FAILED"

    try:
        aft_metrics = AFTMetrics()
        aft_metrics.post_event(action=args.codebuild_name, status=args.codebuild_status)
        logger.info(f"Successfully logged metrics. Action: {args.codebuild_name}")
    except Exception as e:
        logger.info(
            f"Unable to report metrics. Action: {args.codebuild_name}; Error: {e}"
        )
