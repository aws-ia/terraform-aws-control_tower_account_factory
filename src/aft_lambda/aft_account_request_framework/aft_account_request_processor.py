# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
import json
import time
from typing import TYPE_CHECKING, Any, Dict

from aft_common import aft_utils as utils
from aft_common import notifications, sqs
from aft_common.account_provisioning_framework import ProvisionRoles
from aft_common.account_request_framework import (
    AccountRequest,
    create_new_account,
    modify_ct_request_is_valid,
    new_ct_request_is_valid,
    update_existing_account,
)
from aft_common.auth import AuthClient
from aft_common.exceptions import NoAccountFactoryPortfolioFound
from aft_common.metrics import AFTMetrics
from boto3.session import Session

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object

logger = utils.get_logger()


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> None:
    aft_management_session = Session()
    auth = AuthClient()

    try:
        account_request = AccountRequest(auth=auth)
        try:
            account_request.associate_aft_service_role_with_account_factory()
        except NoAccountFactoryPortfolioFound:
            logger.warning(
                message=f"Failed to automatically associate {ProvisionRoles.SERVICE_ROLE_NAME} to portfolio {AccountRequest.ACCOUNT_FACTORY_PORTFOLIO_NAME}. Manual intervention may be required"
            )

        ct_management_session = auth.get_ct_management_session(
            role_name=ProvisionRoles.SERVICE_ROLE_NAME
        )

        if account_request.provisioning_in_progress():
            logger.info("Exiting due to provisioning in progress")
            return None
        else:
            sqs_message = sqs.receive_sqs_message(
                aft_management_session,
                utils.get_ssm_parameter_value(
                    aft_management_session, utils.SSM_PARAM_ACCOUNT_REQUEST_QUEUE
                ),
            )
            if sqs_message is not None:

                aft_metrics = AFTMetrics()

                sqs_body = json.loads(sqs_message["Body"])
                ct_request_is_valid = True
                if sqs_body["operation"] == "ADD":
                    ct_request_is_valid = new_ct_request_is_valid(
                        ct_management_session, sqs_body
                    )
                    if ct_request_is_valid:
                        response = create_new_account(
                            session=aft_management_session,
                            ct_management_session=ct_management_session,
                            request=sqs_body,
                        )

                        action = "new-account-creation-invoked"
                        try:
                            aft_metrics.post_event(action=action, status="SUCCEEDED")
                            logger.info(
                                f"Successfully logged metrics. Action: {action}"
                            )
                        except Exception as e:
                            logger.info(
                                f"Unable to report metrics. Action: {action}; Error: {e}"
                            )

                elif sqs_body["operation"] == "UPDATE":
                    ct_request_is_valid = modify_ct_request_is_valid(sqs_body)
                    if ct_request_is_valid:
                        update_existing_account(
                            session=aft_management_session,
                            ct_management_session=ct_management_session,
                            request=sqs_body,
                        )

                        action = "existing-account-update-invoked"
                        try:
                            aft_metrics.post_event(action=action, status="SUCCEEDED")
                            logger.info(
                                f"Successfully logged metrics. Action: {action}"
                            )
                        except Exception as e:
                            logger.info(
                                f"Unable to report metrics. Action: {action}; Error: {e}"
                            )
                else:
                    logger.info("Unknown operation received in message")
                    raise RuntimeError("Unknown operation received in message")

                sqs.delete_sqs_message(aft_management_session, sqs_message)
                if not ct_request_is_valid:
                    logger.exception("CT Request is not valid")
                    raise RuntimeError("CT Request is not valid")

    except Exception as error:
        notifications.send_lambda_failure_sns_message(
            session=aft_management_session,
            message=str(error),
            context=context,
            subject="AFT account request failed",
        )
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(error),
        }
        logger.exception(message)
        raise
