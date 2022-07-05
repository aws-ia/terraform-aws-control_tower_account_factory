# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
from typing import TYPE_CHECKING, List, Optional

from boto3.session import Session

if TYPE_CHECKING:
    from mypy_boto3_organizations import OrganizationsClient
    from mypy_boto3_organizations.type_defs import (
        AccountTypeDef,
        DescribeOrganizationalUnitResponseTypeDef,
        OrganizationalUnitTypeDef,
        TagTypeDef,
    )

else:
    DescribeOrganizationalUnitResponseTypeDef = object
    OrganizationsClient = object
    TagTypeDef = object
    OrganizationalUnitTypeDef = object
    AccountTypeDef = object


class OrganizationsAgent:
    ROOT_OU = "Root"

    def __init__(self, ct_management_session: Session):
        self.orgs_client: OrganizationsClient = ct_management_session.client(
            "organizations"
        )

    def get_root_ou_id(self) -> str:
        return self.orgs_client.list_roots()["Roots"][0]["Id"]

    def get_ous_for_root(self) -> List[OrganizationalUnitTypeDef]:
        paginator = self.orgs_client.get_paginator(
            "list_organizational_units_for_parent"
        )
        pages = paginator.paginate(ParentId=self.get_root_ou_id())
        ous_under_root = []
        for page in pages:
            ous_under_root.extend(page["OrganizationalUnits"])
        return ous_under_root

    def list_tags_for_resource(self, resource: str) -> List[TagTypeDef]:
        return self.orgs_client.list_tags_for_resource(ResourceId=resource)["Tags"]

    def get_ou_for_account_id(
        self, account_id: str
    ) -> Optional[DescribeOrganizationalUnitResponseTypeDef]:
        ou_ids = [ou["Id"] for ou in self.get_ous_for_root()]
        for ou_id in ou_ids:
            ou_accounts = self.get_accounts_for_ou(ou_id=ou_id)
            if account_id in [account_object["Id"] for account_object in ou_accounts]:
                return self.orgs_client.describe_organizational_unit(
                    OrganizationalUnitId=ou_id
                )
        return None

    def get_accounts_for_ou(self, ou_id: str) -> List[AccountTypeDef]:
        paginator = self.orgs_client.get_paginator("list_accounts_for_parent")
        pages = paginator.paginate(ParentId=ou_id)
        accounts = []
        for page in pages:
            accounts.extend(page["Accounts"])
        return accounts

    def account_id_is_member_of_root(self, account_id: str) -> bool:
        root_id = self.get_root_ou_id()
        accounts_under_root = self.get_accounts_for_ou(ou_id=root_id)
        return account_id in [account["Id"] for account in accounts_under_root]

    def ou_contains_account(self, ou_name: str, account_id: str) -> bool:
        if ou_name == OrganizationsAgent.ROOT_OU:
            return self.account_id_is_member_of_root(account_id=account_id)
        current_ou = self.get_ou_for_account_id(account_id=account_id)
        if current_ou:
            current_ou_name = current_ou["OrganizationalUnit"]["Name"]
            if current_ou_name == ou_name:
                return True
        return False
