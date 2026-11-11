# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Send the one failure notification of an organizations provisioning execution.

Invoked two ways:

* by the state machine's NotifyFailure step, with
  ``{"execution_arn": ..., "state": <the execution's state>}``. It returns the
  error and cause, which the Fail state after it reports as the execution's
  error and cause.
* by an EventBridge rule, with the Step Functions Execution Status Change
  event of an execution that timed out.
"""

import inspect
import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

from aft_common.account_provisioning_framework import ProvisionRoles
from aft_common.aft_utils import sanitize_input_for_logging
from aft_common.auth import AuthClient
from aft_common.logger import configure_aft_logger
from aft_common.organizations import OrganizationsAgent
from aft_common.organizations_failures import (
    EXECUTION_STATUS_CHANGE,
    add_existing_account,
    describe_provisioning_failure,
    failure_from_status_change,
    notify_provisioning_failure,
)

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object

configure_aft_logger()
logger = logging.getLogger("aft")


def _with_existing_account(failure: Dict[str, Any]) -> Dict[str, Any]:
    """Look up the account of a timed-out execution (see
    :func:`add_existing_account`); the notification is sent either way."""
    try:
        orgs_agent = OrganizationsAgent(
            ct_management_session=AuthClient().get_ct_management_session(
                role_name=ProvisionRoles.SERVICE_ROLE_NAME
            )
        )
    except Exception:
        logger.exception("Could not reach the CT management account")
        return {**failure, "account_id_unknown": not failure.get("account_id")}
    return add_existing_account(failure, orgs_agent)


def lambda_handler(
    event: Dict[str, Any], context: LambdaContext
) -> Optional[Dict[str, Any]]:
    from_state_machine = event.get("detail-type") != EXECUTION_STATUS_CHANGE
    if from_state_machine:
        failure = describe_provisioning_failure(
            event.get("state") or {}, execution_arn=str(event.get("execution_arn"))
        )
    else:
        failure = _with_existing_account(failure_from_status_change(event))
    logger.error(
        "Organizations account provisioning failed: "
        + sanitize_input_for_logging(failure)
    )

    notified = True
    try:
        notify_provisioning_failure(AuthClient().get_aft_management_session(), failure)
    except Exception as error:
        logger.exception(
            {
                "FILE": __file__.split("/")[-1],
                "METHOD": inspect.stack()[0][3],
                "EXCEPTION": str(error),
            }
        )
        if not from_state_machine:
            # Asynchronous invoke: raising lets Lambda retry the notification.
            raise
        # The execution still fails with the real error and cause below, and
        # the failure is in this log group; a notification that cannot be sent
        # must not hide them.
        notified = False

    if not from_state_machine:
        return None
    return {"error": failure["error"], "cause": failure["cause"], "notified": notified}
