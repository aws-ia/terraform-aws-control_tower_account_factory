# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
from typing import TYPE_CHECKING, Any, Dict

from aft_common import aft_utils as utils
from aft_common import notifications
from aft_common.feature_options import (
    create_trail,
    event_selectors_exists,
    get_log_bucket_arns,
    put_event_selectors,
    start_logging,
    trail_exists,
    trail_is_logging,
)
from boto3.session import Session

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object

logger = utils.get_logger()

CLOUDTRAIL_TRAIL_NAME = "aws-aft-CustomizationsCloudTrail"


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> None:
    aft_session = Session()
    try:
        ct_session = utils.get_ct_management_session(aft_session)
        log_archive_session = utils.get_log_archive_session(aft_session)

        # Get SSM Parameters
        cloudtrail_enabled = utils.get_ssm_parameter_value(
            aft_session, utils.SSM_PARAM_FEATURE_CLOUDTRAIL_DATA_EVENTS_ENABLED
        )
        s3_log_bucket_arn = utils.get_ssm_parameter_value(
            aft_session, "/aft/account/log-archive/log_bucket_arn"
        )
        s3_bucket_name = s3_log_bucket_arn.split(":::")[1]
        kms_key_arn = utils.get_ssm_parameter_value(
            aft_session, "/aft/account/log-archive/kms_key_arn"
        )
        log_bucket_arns = get_log_bucket_arns(log_archive_session)

        if cloudtrail_enabled == "true":
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
