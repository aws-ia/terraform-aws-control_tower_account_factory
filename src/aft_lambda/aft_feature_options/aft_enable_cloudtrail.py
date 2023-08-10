# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
from typing import TYPE_CHECKING, Any, Dict

import aft_common.ssm
from aft_common import constants as utils
from aft_common import notifications
from aft_common.account_provisioning_framework import ProvisionRoles
from aft_common.auth import AuthClient
from aft_common.feature_options import (
    create_trail,
    event_selectors_exists,
    get_log_bucket_arns,
    put_event_selectors,
    start_logging,
    trail_exists,
    trail_is_logging,
)
from aft_common.logger import customization_request_logger
from boto3.session import Session

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object

CLOUDTRAIL_TRAIL_NAME = "aws-aft-CustomizationsCloudTrail"


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> None:
    request_id = event["customization_request_id"]
    target_account_id = event["account_info"]["account"]["id"]

    logger = customization_request_logger(
        aws_account_id=target_account_id, customization_request_id=request_id
    )

    auth = AuthClient()
    aft_session = Session()

    try:
        ct_session = auth.get_ct_management_session(
            role_name=ProvisionRoles.SERVICE_ROLE_NAME
        )
        log_archive_session = auth.get_log_archive_session(
            role_name=ProvisionRoles.SERVICE_ROLE_NAME
        )

        # Get SSM Parameters
        cloudtrail_enabled = aft_common.ssm.get_ssm_parameter_value(
            aft_session, utils.SSM_PARAM_FEATURE_CLOUDTRAIL_DATA_EVENTS_ENABLED
        )
        s3_log_bucket_arn = aft_common.ssm.get_ssm_parameter_value(
            aft_session, "/aft/account/log-archive/log_bucket_arn"
        )
        s3_bucket_name = s3_log_bucket_arn.split(":::")[1]
        kms_key_arn = aft_common.ssm.get_ssm_parameter_value(
            aft_session, "/aft/account/log-archive/kms_key_arn"
        )
        log_bucket_arns = get_log_bucket_arns(log_archive_session)

        if cloudtrail_enabled == "true":
            logger.info("Enabling Cloudtrail")
            if not trail_exists(ct_session):
                create_trail(ct_session, s3_bucket_name, kms_key_arn)
            if not event_selectors_exists(ct_session):
                put_event_selectors(ct_session, log_bucket_arns)
            if not trail_is_logging(ct_session):
                start_logging(ct_session)

    except Exception as error:
        notifications.send_lambda_failure_sns_message(
            session=aft_session,
            message=str(error),
            context=context,
            subject="AFT: Failed to enable cloudtrail",
        )
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(error),
        }
        logger.exception(message)
        raise
