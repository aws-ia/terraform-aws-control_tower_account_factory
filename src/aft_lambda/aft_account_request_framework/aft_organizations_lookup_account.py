# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Look up an existing account by email for the UPDATE branch.

The Organizations vending method has no provisioned product to update, so an
UPDATE request is resolved to an account id via Organizations lookup before the
move and baseline-wait steps run.
"""

import inspect
import logging
from typing import TYPE_CHECKING, Any, Dict

from aft_common.account_provisioning_framework import ProvisionRoles
from aft_common.auth import AuthClient
from aft_common.logger import configure_aft_logger
from aft_common.organizations import OrganizationsAgent
from aft_common.organizations_provisioning import lookup_account_by_email

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
        account_email = ct_parameters.get("AccountEmail")
        if not account_email:
            raise ValueError(
                "event['control_tower_parameters'] must contain 'AccountEmail'"
            )
        ct_management_session = auth.get_ct_management_session(
            role_name=ProvisionRoles.SERVICE_ROLE_NAME
        )
        orgs_agent = OrganizationsAgent(ct_management_session)
        return lookup_account_by_email(orgs_agent=orgs_agent, request=event)
    except Exception as error:
        logger.exception(
            {
                "FILE": __file__.split("/")[-1],
                "METHOD": inspect.stack()[0][3],
                "EXCEPTION": str(error),
            }
        )
        raise
