# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Publish the account lifecycle event for the Organizations vending method.

Terminal step of both the CreateAccount and UpdateAccount branches. Emits an
``aft.organizations`` event (Control-Tower-shaped Detail) onto the AFT event bus
so the existing logger and provisioning-framework consumers run unchanged.
"""

import inspect
import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

from aft_common.auth import AuthClient
from aft_common.constants import SSM_PARAM_AFT_EVENTS_FROM_CT_MANAGEMENT_BUS_NAME
from aft_common.logger import configure_aft_logger
from aft_common.organizations import OrganizationsAgent
from aft_common.organizations_provisioning import (
    publish_lifecycle_event,
    resolve_account_id_from_state,
)
from aft_common.ssm import get_ssm_parameter_value

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object

configure_aft_logger()
logger = logging.getLogger("aft")


def _organizational_unit_name(managed_ou: Optional[str]) -> Optional[str]:
    """The bare OU name, as a Control Tower event carries it.

    For a nested OU, ManagedOrganizationalUnit is ``Name (ou-xxxx)``; the
    event's organizationalUnitName is just ``Name``. The id comes from the move
    step instead.
    """
    if managed_ou is None:
        return None
    nested = OrganizationsAgent.get_name_and_id_from_nested_ou(
        nested_ou_name=managed_ou
    )
    return nested[0] if nested else managed_ou


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> None:
    auth = AuthClient()
    aft_management_session = auth.get_aft_management_session()
    try:
        operation = event.get("operation")
        if not operation:
            raise ValueError("event must contain 'operation'")
        event_bus_name = get_ssm_parameter_value(
            aft_management_session,
            SSM_PARAM_AFT_EVENTS_FROM_CT_MANAGEMENT_BUS_NAME,
        )
        ct_parameters = event.get("control_tower_parameters", {})
        move = event.get("move", {})
        publish_lifecycle_event(
            session=aft_management_session,
            event_bus_name=event_bus_name,
            operation=operation,
            account_id=resolve_account_id_from_state(event),
            account_name=ct_parameters.get("AccountName"),
            organizational_unit_name=_organizational_unit_name(
                ct_parameters.get("ManagedOrganizationalUnit")
            ),
            organizational_unit_id=move.get("destination_ou_id"),
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
