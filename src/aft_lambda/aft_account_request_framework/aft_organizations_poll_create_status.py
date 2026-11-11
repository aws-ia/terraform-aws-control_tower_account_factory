# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Poll the status of an in-flight Organizations CreateAccount request.

The state machine calls this in a Wait loop and branches on the returned
``State`` (IN_PROGRESS | SUCCEEDED | FAILED).
"""

import inspect
import logging
from typing import TYPE_CHECKING, Any, Dict

from aft_common.account_provisioning_framework import ProvisionRoles
from aft_common.auth import AuthClient
from aft_common.logger import configure_aft_logger
from aft_common.organizations import OrganizationsAgent
from aft_common.organizations_provisioning import poll_create_account_status

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object

configure_aft_logger()
logger = logging.getLogger("aft")


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    auth = AuthClient()
    try:
        create = event.get("create", {})
        request_id = create.get("request_id")
        if not request_id:
            raise ValueError("event['create'] must contain 'request_id'")
        ct_management_session = auth.get_ct_management_session(
            role_name=ProvisionRoles.SERVICE_ROLE_NAME
        )
        orgs_agent = OrganizationsAgent(ct_management_session)
        return poll_create_account_status(
            orgs_agent=orgs_agent,
            request_id=request_id,
            account_name=event.get("control_tower_parameters", {}).get("AccountName"),
            create_window=event.get("create_window"),
        )
    except Exception as error:
        logger.exception(
            {
                "FILE": __file__.split("/")[-1],
                "METHOD": inspect.stack()[0][3],
                "EXCEPTION": str(error),
            }
        )
        raise
