# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
import json
import logging
from typing import TYPE_CHECKING, List

from boto3.session import Session

logger = logging.getLogger("aft")

if TYPE_CHECKING:
    from aft_common.aft_types import AftInvokeAccountCustomizationPayload
else:
    AftInvokeAccountCustomizationPayload = object


def put_target_account_info(
    session: Session,
    bucket: str,
    key: str,
    target_account_info: List[AftInvokeAccountCustomizationPayload],
) -> None:

    s3 = session.resource("s3")
    json_data = json.dumps(target_account_info)

    logger.info(f"Uploading target account info to s3://{bucket}/{key}")
    s3.Object(bucket, key).put(Body=json_data)
    logger.info(f"Successfully uploaded target account info to s3://{bucket}/{key}")
