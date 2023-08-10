# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
import logging
from typing import Any, Dict, List

from aft_common import ddb
from aft_common.account_provisioning_framework import ProvisionRoles
from aft_common.aft_utils import emails_are_equal, get_high_retry_botoconfig
from aft_common.auth import AuthClient
from aft_common.constants import (
    SSM_PARAM_ACCOUNT_AUDIT_ACCOUNT_ID,
    SSM_PARAM_ACCOUNT_CT_MANAGEMENT_ACCOUNT_ID,
    SSM_PARAM_ACCOUNT_LOG_ARCHIVE_ACCOUNT_ID,
)
from aft_common.organizations import OrganizationsAgent
from aft_common.ssm import get_ssm_parameter_value
from boto3.session import Session

logger = logging.getLogger("aft")


def shared_account_request(event_record: Dict[str, Any], auth: AuthClient) -> bool:
    ct_params = ddb.unmarshal_ddb_item(event_record["dynamodb"]["NewImage"])[
        "control_tower_parameters"
    ]
    account_email = ct_params["AccountEmail"]
    account_name = ct_params["AccountName"]
    request_ou = ct_params["ManagedOrganizationalUnit"]
    shared_account_ids = get_shared_ids(
        aft_management_session=auth.get_aft_management_session()
    )
    ct_management_session = auth.get_ct_management_session(
        role_name=ProvisionRoles.SERVICE_ROLE_NAME
    )
    orgs_client = ct_management_session.client(
        "organizations", config=get_high_retry_botoconfig()
    )
    for shared_account_id in shared_account_ids:
        response = orgs_client.describe_account(AccountId=shared_account_id)
        if (
            emails_are_equal(response["Account"]["Email"], account_email)
            and response["Account"]["Name"] == account_name
        ):
            orgs_agent = OrganizationsAgent(ct_management_session=ct_management_session)
            if not orgs_agent.ou_contains_account(
                ou_name=request_ou, account_id=shared_account_id
            ):
                raise ValueError(
                    "Unsupported action: Cannot change OU for a Shared CT account or CT management account"
                )
            return True
        elif (
            emails_are_equal(response["Account"]["Email"], account_email)
            and response["Account"]["Name"] != account_name
        ):
            raise ValueError(
                f"Account Email {account_email} is a shared account email, however, the Account Name {account_name} does not match"
            )
        elif response["Account"]["Name"] == account_name and not emails_are_equal(
            response["Account"]["Email"], account_email
        ):
            raise ValueError(
                f"Account Name {account_name} is a shared account Name, however, the Account Email {account_email} does not match"
            )
    return False


def get_shared_ids(aft_management_session: Session) -> List[str]:
    shared_account_ssm_params = [
        SSM_PARAM_ACCOUNT_LOG_ARCHIVE_ACCOUNT_ID,
        SSM_PARAM_ACCOUNT_AUDIT_ACCOUNT_ID,
        SSM_PARAM_ACCOUNT_CT_MANAGEMENT_ACCOUNT_ID,
    ]
    return [
        get_ssm_parameter_value(session=aft_management_session, param=ssm_param)
        for ssm_param in shared_account_ssm_params
    ]
