# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
import json
from typing import TYPE_CHECKING, Any, Dict

import boto3
from aft_common import aft_utils as utils
from aft_common import notifications
from aft_common.account_provisioning_framework import (
    SSM_PARAMETER_PATH,
    ProvisionRoles,
    delete_ssm_parameters,
    get_ssm_parameters_names_by_path,
    put_ssm_parameters,
)
from aft_common.auth import AuthClient

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object

logger = utils.get_logger()


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> None:
    auth = AuthClient()
    try:
        account_request = event["payload"]["account_request"]
        custom_fields = json.loads(account_request.get("custom_fields", "{}"))
        target_account_id = event["payload"]["account_info"]["account"]["id"]

        # Create the custom field parameters in the AFT home region
        session = auth.get_aft_management_session()
        target_region = session.region_name

        aft_ssm_session_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": [
                        "ssm:GetParametersByPath",
                        "ssm:PutParameter",
                        "ssm:DeleteParameters",
                    ],
                    "Effect": "Allow",
                    "Resource": f"arn:{utils.get_aws_partition(session)}:ssm:{target_region}:{target_account_id}:parameter{SSM_PARAMETER_PATH}*",
                }
            ],
        }

        target_account_session = auth.get_target_account_session(
            account_id=target_account_id,
            session_policy=json.dumps(aft_ssm_session_policy),
            role_name=ProvisionRoles.SERVICE_ROLE_NAME,
        )

        params = get_ssm_parameters_names_by_path(
            target_account_session, SSM_PARAMETER_PATH
        )

        existing_keys = set(params)
        new_keys = set(custom_fields.keys())

        # Delete SSM parameters which do not exist in new custom fields
        params_to_remove = list(existing_keys.difference(new_keys))
        logger.info(message=f"Deleting SSM params: {params_to_remove}")
        delete_ssm_parameters(target_account_session, params_to_remove)

        # Update / Add SSM parameters for custom fields provided
        logger.info(message=f"Adding/Updating SSM params: {custom_fields}")
        put_ssm_parameters(target_account_session, custom_fields)

    except Exception as error:
        notifications.send_lambda_failure_sns_message(
            session=auth.get_aft_management_session(),
            message=str(error),
            context=context,
            subject="AFT account provisioning failed",
        )
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(error),
        }
        logger.exception(message)
        raise
