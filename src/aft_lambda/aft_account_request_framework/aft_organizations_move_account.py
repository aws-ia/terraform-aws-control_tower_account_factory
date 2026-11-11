# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Move an account into its managed OU.

Resolves the account id from the state (CreateAccount status for the create
branch, or the lookup result for the update branch) and the target OU name from
the account request, then moves the account into the managed OU. Idempotent.
Also returns the ARNs the baseline poll reads, resolved once here.
"""

import inspect
import logging
from typing import TYPE_CHECKING, Any, Dict

from aft_common.account_provisioning_framework import ProvisionRoles
from aft_common.auth import AuthClient
from aft_common.control_tower import ControlTowerFacade
from aft_common.logger import configure_aft_logger
from aft_common.organizations import OrganizationsAgent
from aft_common.organizations_provisioning import (
    move_account_to_managed_ou,
    resolve_account_id_from_state,
    starting_parent_from_state,
)

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
        managed_ou_name = ct_parameters.get("ManagedOrganizationalUnit")
        if not managed_ou_name:
            raise ValueError(
                "event['control_tower_parameters'] must contain "
                "'ManagedOrganizationalUnit'"
            )
        ct_management_session = auth.get_ct_management_session(
            role_name=ProvisionRoles.SERVICE_ROLE_NAME
        )
        orgs_agent = OrganizationsAgent(ct_management_session)
        ct_facade = ControlTowerFacade(ct_management_session=ct_management_session)
        account_id = resolve_account_id_from_state(event)
        return move_account_to_managed_ou(
            orgs_agent=orgs_agent,
            ct_facade=ct_facade,
            account_id=account_id,
            managed_ou_name=managed_ou_name,
            starting_parent_id=starting_parent_from_state(event),
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
