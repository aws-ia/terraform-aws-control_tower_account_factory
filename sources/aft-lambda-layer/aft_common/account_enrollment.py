# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Whether a requested account already exists and is enrolled in Control
Tower, for either account vending method."""

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Optional

from aft_common import ddb
from aft_common.account_provisioning_framework import ProvisionRoles
from aft_common.auth import AuthClient
from aft_common.constants import (
    SSM_PARAM_ACCOUNT_VENDING_METHOD,
    VENDING_METHOD_ORGANIZATIONS,
)
from aft_common.control_tower import ControlTowerFacade
from aft_common.organizations import OrganizationsAgent
from aft_common.service_catalog import get_account_id_if_healthy_product_exists
from aft_common.ssm import get_ssm_parameter_value
from boto3.session import Session

if TYPE_CHECKING:
    from mypy_boto3_organizations.type_defs import AccountTypeDef
else:
    AccountTypeDef = object

logger = logging.getLogger("aft")


@dataclass(frozen=True)
class AccountEnrollment:
    """Whether the account a request names already exists and is enrolled in
    Control Tower.

    ``account_id`` is set whenever an account with the request's email exists
    in Organizations, whether or not it is enrolled.
    """

    account_id: Optional[str]
    enrolled: bool
    vending_method: str

    @property
    def awaiting_enrollment(self) -> bool:
        """Organizations method: the account exists, but Control Tower has not
        finished enrolling it (a baseline under change or failed, or one the
        account does not list yet). AFT handles it as an existing account and
        waits for its enrollment, instead of creating it again.

        With the Service Catalog method, an account without a healthy
        provisioned product is handled as a new account.
        """
        return (
            self.account_id is not None
            and not self.enrolled
            and self.vending_method == VENDING_METHOD_ORGANIZATIONS
        )


def get_account_enrollment(record: Dict[str, Any]) -> AccountEnrollment:
    """Look up the account the DynamoDB stream ``record`` requests.

    Whether the account exists comes from Organizations alone: an account
    with the request's email exists. Whether it is enrolled depends on the
    account vending method (SSM ``/aft/config/account-vending-method``):

    * ``service_catalog`` (default): it has a healthy Account Factory
      provisioned product.
    * ``organizations``: its Control Tower baseline has finished successfully
      (``is_complete``). There is no Service Catalog provisioned product with
      this method.
    """
    auth = AuthClient()
    ct_management_session = auth.get_ct_management_session(
        role_name=ProvisionRoles.SERVICE_ROLE_NAME
    )
    account_email = ddb.unmarshal_ddb_item(record["dynamodb"]["NewImage"])[
        "control_tower_parameters"
    ]["AccountEmail"]
    vending_method = get_ssm_parameter_value(
        auth.get_aft_management_session(),
        SSM_PARAM_ACCOUNT_VENDING_METHOD,
    )

    orgs_agent = OrganizationsAgent(ct_management_session=ct_management_session)
    account = orgs_agent.get_account_by_email(account_email)
    if account is None:
        logger.info("Account not found in Organizations")
        return AccountEnrollment(
            account_id=None, enrolled=False, vending_method=vending_method
        )

    if vending_method == VENDING_METHOD_ORGANIZATIONS:
        enrolled = _baseline_complete(ct_management_session, account)
    else:
        enrolled = (
            get_account_id_if_healthy_product_exists(ct_management_session, account)
            is not None
        )
    return AccountEnrollment(
        account_id=account["Id"], enrolled=enrolled, vending_method=vending_method
    )


def _baseline_complete(
    ct_management_session: Session, account: "AccountTypeDef"
) -> bool:
    """organizations method: enrolled iff the account's Control Tower baseline
    has completed."""
    ct_facade = ControlTowerFacade(ct_management_session=ct_management_session)
    baseline_status = ct_facade.get_account_baseline_status(
        account_target_identifier=account["Arn"]
    )
    if baseline_status.is_complete:
        logger.info("Control Tower baseline complete for account")
        return True

    logger.info(
        "Account exists in Organizations but Control Tower baseline is not complete"
    )
    return False
