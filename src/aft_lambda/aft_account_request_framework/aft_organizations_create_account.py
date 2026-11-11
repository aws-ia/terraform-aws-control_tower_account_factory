# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""CreateAccount step of the aft-organizations-account-provisioning SFN.

Checks the managed OU, then submits the asynchronous Organizations
CreateAccount (or picks up the request this execution already submitted) and
returns the request Id for the state machine to poll.
"""

import inspect
import logging
from typing import TYPE_CHECKING, Any, Dict

from aft_common.account_provisioning_framework import ProvisionRoles
from aft_common.auth import AuthClient
from aft_common.control_tower import ControlTowerFacade
from aft_common.logger import configure_aft_logger
from aft_common.organizations import OrganizationsAgent
from aft_common.organizations_provisioning import start_create_account

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object

configure_aft_logger()
logger = logging.getLogger("aft")


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    auth = AuthClient()
    try:
        ct_parameters = event.get("control_tower_parameters", {})
        account_name = ct_parameters.get("AccountName")
        account_email = ct_parameters.get("AccountEmail")
        managed_ou = ct_parameters.get("ManagedOrganizationalUnit")
        if not account_name or not account_email or not managed_ou:
            raise ValueError(
                "event['control_tower_parameters'] must contain "
                "'AccountName', 'AccountEmail' and 'ManagedOrganizationalUnit'"
            )
        ct_management_session = auth.get_ct_management_session(
            role_name=ProvisionRoles.SERVICE_ROLE_NAME
        )
        orgs_agent = OrganizationsAgent(ct_management_session)
        ct_facade = ControlTowerFacade(ct_management_session=ct_management_session)
        return start_create_account(
            orgs_agent=orgs_agent, ct_facade=ct_facade, request=event
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
