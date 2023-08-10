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
from aft_common.logger import customization_request_logger
from aft_common.premium_support import account_enrollment_requested, generate_case
from boto3.session import Session

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> None:
    request_id = event["customization_request_id"]
    target_account_id = event["account_info"]["account"]["id"]

    logger = customization_request_logger(
        aws_account_id=target_account_id, customization_request_id=request_id
    )

    auth = AuthClient()
    aft_session = Session()
    try:
        ct_mgmt_session = auth.get_ct_management_session(
            role_name=ProvisionRoles.SERVICE_ROLE_NAME
        )

        if (
            aft_common.ssm.get_ssm_parameter_value(
                aft_session, utils.SSM_PARAM_FEATURE_ENTERPRISE_SUPPORT_ENABLED
            ).lower()
            == "true"
        ):
            if not account_enrollment_requested(ct_mgmt_session, target_account_id):
                logger.info(
                    "Generating support case for enrolling target account into AWS Enterprise Support"
                )
                generate_case(ct_mgmt_session, target_account_id)

    except Exception as error:
        notifications.send_lambda_failure_sns_message(
            session=aft_session,
            message=str(error),
            context=context,
            subject="AFT: Failed to enroll into Enterprise Support",
        )
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(error),
        }
        logger.exception(message)
        raise
