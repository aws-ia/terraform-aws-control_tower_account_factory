# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from typing import TYPE_CHECKING

from aft_common.aft_utils import (
    get_high_retry_botoconfig,
    resubmit_request_on_boto_throttle,
)
from boto3.session import Session
from botocore.config import Config

if TYPE_CHECKING:
    from mypy_boto3_support import SupportClient
else:
    SupportClient = object

SUPPORT_API_REGION = "us-east-1"


@resubmit_request_on_boto_throttle
def account_enrollment_requested(
    ct_management_session: Session, account_id: str
) -> bool:
    """
    Query the open support cases, if a case is open with the expected title, return True
    else we return False
    """
    submitted_enroll_case_title = f"Add Account {account_id} to Enterprise Support"

    # Must use us-east-1 region for Support API
    botoconfig = Config.merge(
        get_high_retry_botoconfig(), Config(region_name=SUPPORT_API_REGION)
    )
    client: SupportClient = ct_management_session.client("support", config=botoconfig)
    paginator = client.get_paginator("describe_cases")
    pages = paginator.paginate(
        includeResolvedCases=True,
        language="en",
        includeCommunications=False,
    )
    for page in pages:
        for case in page["cases"]:
            if case["subject"] == submitted_enroll_case_title:
                return True

    return False


def generate_case(session: Session, account_id: str) -> None:
    support: SupportClient = session.client("support", region_name=SUPPORT_API_REGION)
    support.create_case(
        issueType="customer-service",
        serviceCode="account-management",
        categoryCode="billing",
        severityCode="low",
        subject=f"Add Account {account_id} to Enterprise Support",
        communicationBody=f"Please add account number {account_id} to our enterprise support plan.",
        language="en",
    )
