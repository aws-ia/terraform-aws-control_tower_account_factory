# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
from typing import Any, Dict, List

from aft_common import aft_utils as utils
from aft_common.aft_utils import (
    SSM_PARAM_ACCOUNT_AUDIT_ACCOUNT_ID,
    SSM_PARAM_ACCOUNT_CT_MANAGEMENT_ACCOUNT_ID,
    SSM_PARAM_ACCOUNT_LOG_ARCHIVE_ACCOUNT_ID,
)
from aft_common.auth import AuthClient
from aft_common.organizations import OrganizationsAgent
from boto3.session import Session

logger = utils.get_logger()


def shared_account_request(
    aft_management_session: Session, event_record: Dict[str, Any]
) -> bool:
    ct_params = utils.unmarshal_ddb_item(event_record["dynamodb"]["NewImage"])[
        "control_tower_parameters"
    ]
    account_email = ct_params["AccountEmail"]
    account_name = ct_params["AccountName"]
    request_ou = ct_params["ManagedOrganizationalUnit"]
    auth = AuthClient()
    shared_account_ids = get_shared_ids(
        aft_management_session=auth.get_aft_management_session()
    )

    for shared_account_id in shared_account_ids:
        orgs_client = auth.get_ct_management_session().client("organizations")
        response = orgs_client.describe_account(AccountId=shared_account_id)
        if (
            response["Account"]["Email"] == account_email
            and response["Account"]["Name"] == account_name
        ):
            orgs_agent = OrganizationsAgent(
                orgs_session=auth.get_ct_management_session()
            )
            if not orgs_agent.ou_contains_account(
                ou_name=request_ou, account_id=shared_account_id
            ):
                raise ValueError(
                    "Unsupported action: Cannot change OU for a Shared CT account or CT management account"
                )
            return True
        elif (
            response["Account"]["Email"] == account_email
            and response["Account"]["Name"] != account_name
        ):
            logger.error(
                f"Account Email {account_email} is a shared account email, however, the Account Name {account_name} does not match"
            )
        elif (
            response["Account"]["Name"] == account_name
            and response["Account"]["Email"] != account_email
        ):
            logger.error(
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
        utils.get_ssm_parameter_value(session=aft_management_session, param=ssm_param)
        for ssm_param in shared_account_ssm_params
    ]
