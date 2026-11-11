# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import logging
from typing import TYPE_CHECKING

from aft_common import ddb
from aft_common.aft_utils import get_aws_partition, sanitize_input_for_logging
from boto3.session import Session
from botocore.config import Config
from botocore.exceptions import ClientError, UnknownRegionError

if TYPE_CHECKING:
    from mypy_boto3_support import SupportClient
else:
    SupportClient = object

logger = logging.getLogger("aft")

SUPPORT_API_REGION = "us-east-1"
_SUPPORT_API_LEADER_REGIONS = {"aws-cn": "cn-north-1", "aws-eusc": "eusc-de-east-1"}
METADATA_SUPPORT_FIELD = "enterprise_support_case_created"

THROTTLING_ERROR_CODES = [
    "ThrottlingException",
    "TooManyRequestsException",
    "RequestLimitExceeded",
]

_SUPPORT_BOTOCONFIG = Config(
    retries={"total_max_attempts": 3, "mode": "standard"},
)


def _support_api_region(session: Session) -> str:
    if session.region_name is None:
        return SUPPORT_API_REGION
    try:
        partition = get_aws_partition(session)
    except UnknownRegionError:
        return SUPPORT_API_REGION
    return _SUPPORT_API_LEADER_REGIONS.get(partition, SUPPORT_API_REGION)


def _support_client(session: Session) -> SupportClient:
    return session.client(
        "support", region_name=_support_api_region(session), config=_SUPPORT_BOTOCONFIG
    )


def is_enrollment_flagged_in_metadata(
    session: Session, table_name: str, account_id: str
) -> bool:
    item = ddb.get_ddb_item(
        session=session, table_name=table_name, primary_key={"id": account_id}
    )
    if item is None:
        return False
    return item.get(METADATA_SUPPORT_FIELD) == "true"


def set_enrollment_flag_in_metadata(
    session: Session, table_name: str, account_id: str
) -> None:
    dynamodb = session.resource("dynamodb")
    table = dynamodb.Table(table_name)
    try:
        # Only update existing records to avoid creating sparse metadata entries
        table.update_item(
            Key={"id": account_id},
            UpdateExpression="SET #field = :val",
            ExpressionAttributeNames={"#field": METADATA_SUPPORT_FIELD},
            ExpressionAttributeValues={":val": "true"},
            ConditionExpression="attribute_exists(id)",
        )
        logger.info(
            f"Set {METADATA_SUPPORT_FIELD} flag for account "
            f"{sanitize_input_for_logging(account_id)}"
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            logger.error(
                f"Cannot set enrollment flag: metadata record does not exist "
                f"for account {sanitize_input_for_logging(account_id)}"
            )
        raise


def account_enrollment_requested(
    ct_management_session: Session, account_id: str
) -> bool:
    submitted_enroll_case_title = f"Add Account {account_id} to Enterprise Support"

    client = _support_client(ct_management_session)
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
    support = _support_client(session)
    support.create_case(
        issueType="customer-service",
        serviceCode="account-management",
        categoryCode="billing",
        severityCode="low",
        subject=f"Add Account {account_id} to Enterprise Support",
        communicationBody=f"Please add account number {account_id} to our enterprise support plan.",
        language="en",
    )


def ensure_enterprise_support_enrollment(
    aft_session: Session,
    ct_management_session: Session,
    metadata_table_name: str,
    account_id: str,
) -> None:
    if is_enrollment_flagged_in_metadata(aft_session, metadata_table_name, account_id):
        logger.info(
            f"Enterprise support enrollment already recorded for account "
            f"{sanitize_input_for_logging(account_id)}"
        )
        return

    case_exists = False
    try:
        case_exists = account_enrollment_requested(ct_management_session, account_id)
    except ClientError as e:
        if e.response["Error"]["Code"] in THROTTLING_ERROR_CODES:
            logger.info(
                f"DescribeCases throttled: {e}; proceeding to create a new case"
            )
        else:
            raise

    if not case_exists:
        generate_case(ct_management_session, account_id)

    # Flag is set after case creation so that a failure here triggers a SFN retry.
    # A retry will re-check via DescribeCases (or get throttled and create a harmless
    # duplicate case), which is safer than setting the flag before the case exists.
    set_enrollment_flag_in_metadata(aft_session, metadata_table_name, account_id)
