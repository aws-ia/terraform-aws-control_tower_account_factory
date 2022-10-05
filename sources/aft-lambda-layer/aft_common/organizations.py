# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
import re
from copy import deepcopy
from typing import TYPE_CHECKING, List, Optional, Tuple

from aft_common.aft_utils import get_logger
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

logger = get_logger()


class OrganizationsAgent:
    ROOT_OU = "Root"
    # https://docs.aws.amazon.com/organizations/latest/APIReference/API_OrganizationalUnit.html
    # Ex: Sandbox (ou-1234-zxcv)
    OU_ID_PATTERN = r"\(ou-.*\)"
    OU_NAME_PATTERN = r".{1,128}"
    NESTED_OU_NAME_PATTERN = (
        rf"{OU_NAME_PATTERN}\s{OU_ID_PATTERN}"  # <Name> space (<Id>)
    )

    def __init__(self, ct_management_session: Session):
        self.orgs_client: OrganizationsClient = ct_management_session.client(
            "organizations"
        )

        # Memoize expensive all-org traversal
        self.org_ous: Optional[List[OrganizationalUnitTypeDef]] = None

    @staticmethod
    def ou_name_is_nested_format(ou_name: str) -> bool:
        pattern = re.compile(OrganizationsAgent.NESTED_OU_NAME_PATTERN)
        if pattern.match(ou_name) is not None:
            return True
        return False

    @staticmethod
    def get_name_and_id_from_nested_ou(
        nested_ou_name: str,
    ) -> Optional[Tuple[str, str]]:
        if not OrganizationsAgent.ou_name_is_nested_format(ou_name=nested_ou_name):
            return None

        pattern = re.compile(OrganizationsAgent.OU_ID_PATTERN)
        match = pattern.search(nested_ou_name)
        if match is None:
            return None
        first_id_idx, last_id_idx = match.span()

        # Grab the matched ID from the nested-ou-string using the span,
        id = nested_ou_name[first_id_idx:last_id_idx]
        id = id.strip("()")

        # The name is what remains of the nested OU without the ID, minus
        # the whitespace between the name and ID
        name = nested_ou_name[: first_id_idx - 1]
        return (name, id)

    def get_root_ou_id(self) -> str:
        return self.orgs_client.list_roots()["Roots"][0]["Id"]

    def get_ous_for_root(self) -> List[OrganizationalUnitTypeDef]:
        return self.get_children_ous_from_parent_id(parent_id=self.get_root_ou_id())

    def get_all_org_ous(self) -> List[OrganizationalUnitTypeDef]:
        # Memoize calls / cache previous results
        # Cache is not shared between invocations so staleness due to org updates is unlikely
        if self.org_ous is not None:
            return self.org_ous

        # Including the root OU
        list_root_response = self.orgs_client.list_roots()
        root_ou: OrganizationalUnitTypeDef = {
            "Id": list_root_response["Roots"][0]["Id"],
            "Arn": list_root_response["Roots"][0]["Arn"],
            "Name": list_root_response["Roots"][0]["Name"],
        }

        org_ous = [root_ou]

        # Get the children OUs of the root as the first pass
        root_children = self.get_ous_for_root()
        org_ous.extend(root_children)

        # Exclude root to avoid double counting children
        ous_to_query = deepcopy(root_children)

        # Recursively search all children OUs for further children
        while len(ous_to_query) > 0:
            parent_id: str = ous_to_query.pop()["Id"]
            children_ous = self.get_children_ous_from_parent_id(parent_id=parent_id)
            org_ous.extend(children_ous)
            ous_to_query.extend(children_ous)

        self.org_ous = org_ous

        return self.org_ous

    def get_children_ous_from_parent_id(
        self, parent_id: str
    ) -> List[OrganizationalUnitTypeDef]:

        paginator = self.orgs_client.get_paginator(
            "list_organizational_units_for_parent"
        )
        pages = paginator.paginate(ParentId=parent_id)
        children_ous = []
        for page in pages:
            children_ous.extend(page["OrganizationalUnits"])
        return children_ous

    def get_ou_ids_from_ou_names(self, target_ou_names: List[str]) -> List[str]:
        ous = self.get_all_org_ous()
        ou_map = {}

        # Convert list of OUs to name->id map for constant time lookups
        for ou in ous:
            ou_map[ou["Name"]] = ou["Id"]

        # Search the map for every target exactly once
        matched_ou_ids = []
        for target_name in target_ou_names:
            # Only match nested OU targets if both name and ID are the same
            nested_parsed = OrganizationsAgent.get_name_and_id_from_nested_ou(
                nested_ou_name=target_name
            )
            if nested_parsed is not None:  # Nested OU pattern matched!
                target_name, target_id = nested_parsed
                if ou_map[target_name] == target_id:
                    matched_ou_ids.append(ou_map[target_name])
            else:
                if target_name in ou_map:
                    matched_ou_ids.append(ou_map[target_name])

        return matched_ou_ids

    def get_ou_from_account_id(
        self, account_id: str
    ) -> Optional[OrganizationalUnitTypeDef]:
        if self.account_id_is_member_of_root(account_id=account_id):
            list_root_response = self.orgs_client.list_roots()
            root_ou: OrganizationalUnitTypeDef = {
                "Id": list_root_response["Roots"][0]["Id"],
                "Arn": list_root_response["Roots"][0]["Arn"],
                "Name": list_root_response["Roots"][0]["Name"],
            }
            return root_ou

        ous = self.get_all_org_ous()
        for ou in ous:
            account_ids = [acct["Id"] for acct in self.get_accounts_for_ou(ou["Id"])]
            if account_id in account_ids:
                return ou
        return None

    def get_accounts_for_ou(self, ou_id: str) -> List[AccountTypeDef]:
        paginator = self.orgs_client.get_paginator("list_accounts_for_parent")
        pages = paginator.paginate(ParentId=ou_id)
        accounts = []
        for page in pages:
            accounts.extend(page["Accounts"])
        return accounts

    def get_account_ids_in_ous(self, ou_names: List[str]) -> List[str]:
        ou_ids = self.get_ou_ids_from_ou_names(target_ou_names=ou_names)
        account_ids = []
        for ou_id in ou_ids:
            account_ids.extend(
                [acct["Id"] for acct in self.get_accounts_for_ou(ou_id=ou_id)]
            )
        return account_ids

    def account_id_is_member_of_root(self, account_id: str) -> bool:
        root_id = self.get_root_ou_id()
        accounts_under_root = self.get_accounts_for_ou(ou_id=root_id)
        return account_id in [account["Id"] for account in accounts_under_root]

    def ou_contains_account(self, ou_name: str, account_id: str) -> bool:
        if ou_name == OrganizationsAgent.ROOT_OU:
            return self.account_id_is_member_of_root(account_id=account_id)
        current_ou = self.get_ou_from_account_id(account_id=account_id)
        if current_ou:
            if ou_name == current_ou["Name"]:
                return True
        return False

    def list_tags_for_resource(self, resource: str) -> List[TagTypeDef]:
        return self.orgs_client.list_tags_for_resource(ResourceId=resource)["Tags"]
