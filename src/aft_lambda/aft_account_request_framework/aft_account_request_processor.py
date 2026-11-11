# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
import json
import logging
import os
import time
from typing import TYPE_CHECKING, Any, Dict

import aft_common.ssm
from aft_common import constants as utils
from aft_common import notifications, sqs
from aft_common.account_provisioning_framework import ProvisionRoles
from aft_common.account_request_framework import (
    AccountRequest,
    create_new_account,
    get_account_vending_method,
    modify_ct_request_is_valid,
    new_ct_request_is_valid,
    start_organizations_account_provisioning,
    update_existing_account,
)
from aft_common.aft_utils import sanitize_input_for_logging
from aft_common.auth import AuthClient
from aft_common.control_tower import ControlTowerFacade
from aft_common.exceptions import NoAccountFactoryPortfolioFound
from aft_common.logger import configure_aft_logger
from aft_common.metrics import AFTMetrics
from boto3.session import Session

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object

configure_aft_logger()
logger = logging.getLogger("aft")


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> None:
    aft_management_session = Session()
    auth = AuthClient()
    threshold = int(os.environ["AFT_PROVISIONING_CONCURRENCY"])

    try:
        use_organizations = (
            get_account_vending_method(aft_management_session)
            == utils.VENDING_METHOD_ORGANIZATIONS
        )
        account_request = AccountRequest(auth=auth)
        account_request_queue = aft_common.ssm.get_ssm_parameter_value(
            aft_management_session, utils.SSM_PARAM_ACCOUNT_REQUEST_QUEUE
        )

        ct_management_session = auth.get_ct_management_session(
            role_name=ProvisionRoles.SERVICE_ROLE_NAME
        )

        if use_organizations:
            # No Service Catalog: skip the portfolio association. Vend only
            # while the landing zone is ACTIVE with auto-enrollment on. The
            # check runs only when a request is waiting, and before it is
            # received: a received message goes to the DLQ when this run
            # fails. The SQS message stays queued until the landing zone is
            # ready.
            if not sqs.count_pending_sqs_messages(
                aft_management_session, account_request_queue
            ):
                logger.info("No account requests pending processing")
                return None
            ct_facade = ControlTowerFacade(ct_management_session=ct_management_session)
            readiness = ct_facade.get_landing_zone_readiness()
            if readiness.is_updating:
                # A landing zone update or reset ends on its own; wait for it
                # without a failure notification every run.
                logger.info(
                    f"{sanitize_input_for_logging(readiness.reason)}; "
                    "leaving the account request queued"
                )
                return None
            if not readiness.is_ready:
                raise RuntimeError(
                    f"{readiness.reason}; the organizations vending method needs "
                    "an ACTIVE landing zone with auto-enrollment on"
                )
        else:
            try:
                account_request.associate_aft_service_role_with_account_factory()
            except NoAccountFactoryPortfolioFound:
                logger.warning(
                    f"Failed to automatically associate {ProvisionRoles.SERVICE_ROLE_NAME} to portfolio {AccountRequest.ACCOUNT_FACTORY_PORTFOLIO_NAME}. Manual intervention may be required"
                )

        if account_request.provisioning_threshold_reached(
            threshold=threshold, use_organizations=use_organizations
        ):
            logger.info("Concurrent account provisioning threshold reached, exiting")
            return None
        else:
            sqs_message = sqs.receive_sqs_message(
                aft_management_session, account_request_queue
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
                        if use_organizations:
                            start_organizations_account_provisioning(
                                session=aft_management_session, request=sqs_body
                            )
                        else:
                            create_new_account(
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
                        if use_organizations:
                            start_organizations_account_provisioning(
                                session=aft_management_session, request=sqs_body
                            )
                        else:
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
