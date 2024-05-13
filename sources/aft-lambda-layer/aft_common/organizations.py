# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
import logging
import re
from copy import deepcopy
from typing import TYPE_CHECKING, List, Optional, Sequence, Tuple, cast

from aft_common.aft_types import AftAccountInfo
from aft_common.aft_utils import (
    emails_are_equal,
    get_high_retry_botoconfig,
    resubmit_request_on_boto_throttle,
)
from boto3.session import Session

if TYPE_CHECKING:
    from mypy_boto3_organizations import OrganizationsClient
    from mypy_boto3_organizations.type_defs import (
        AccountTypeDef,
        DescribeAccountResponseTypeDef,
        OrganizationalUnitTypeDef,
        ParentTypeDef,
        TagTypeDef,
    )

else:
    DescribeAccountResponseTypeDef = object
    OrganizationsClient = object
    TagTypeDef = object
    OrganizationalUnitTypeDef = object
    AccountTypeDef = object
    ParentTypeDef = object

logger = logging.getLogger("aft")


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
            "organizations", config=get_high_retry_botoconfig()
        )

        # Memoization - cache org query results
        # Cache is not shared between AFT invocations so staleness due to org updates is unlikely
        self.org_root_ou_id: Optional[str] = None
        self.org_ous: Optional[List[OrganizationalUnitTypeDef]] = None
        self.org_accounts: Optional[List[AccountTypeDef]] = None

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

    @staticmethod
    def get_nested_ou_format_from_name_and_id(ou_name: str, ou_id: str) -> str:
        return f"{ou_name} ({ou_id})"

    def get_root_ou_id(self) -> str:
        if self.org_root_ou_id is not None:
            return self.org_root_ou_id

        # Assumes single-root organizations
        self.org_root_ou_id = self.orgs_client.list_roots()["Roots"][0]["Id"]
        return self.org_root_ou_id

    def get_ous_for_root(self) -> List[OrganizationalUnitTypeDef]:
        return self.get_children_ous_from_parent_id(parent_id=self.get_root_ou_id())

    def get_all_org_accounts(self) -> List[AccountTypeDef]:
        if self.org_accounts is not None:
            return self.org_accounts

        paginator = self.orgs_client.get_paginator("list_accounts")
        accounts = []
        for page in paginator.paginate():
            accounts.extend(page["Accounts"])

        self.org_accounts = accounts
        return self.org_accounts

    def get_all_org_ous(self) -> List[OrganizationalUnitTypeDef]:
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

    def get_parents_from_account_id(self, account_id: str) -> List[ParentTypeDef]:
        paginator = self.orgs_client.get_paginator("list_parents")
        pages = paginator.paginate(ChildId=account_id)
        parents = []
        for page in pages:
            parents.extend(page["Parents"])
        return parents

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
        org_ou_map = {}

        # Convert list of OUs to id->name map for constant time lookups
        for ou in ous:
            org_ou_map[ou["Id"]] = ou["Name"]

        # Search the map for every target exactly once
        matched_ou_ids = []
        for target_name in target_ou_names:
            # Only match nested OU targets if both name and ID are the same
            nested_parsed = OrganizationsAgent.get_name_and_id_from_nested_ou(
                nested_ou_name=target_name
            )
            if nested_parsed is not None:  # Nested OU pattern matched!
                target_name, target_id = nested_parsed
                if target_id in org_ou_map.keys():
                    if org_ou_map[target_id] == target_name:
                        matched_ou_ids.append(target_id)
            else:
                if target_name in org_ou_map.values():
                    target_id = [
                        id for id, name in org_ou_map.items() if target_name == name
                    ][0]
                    matched_ou_ids.append(target_id)

        return matched_ou_ids

    def get_ou_from_account_id(self, account_id: str) -> OrganizationalUnitTypeDef:
        # NOTE: Assumes single-parent accounts
        parents = self.get_parents_from_account_id(account_id=account_id)
        parent = parents[0]

        # Child of Root
        if parent["Type"] == "ROOT":
            list_root_response = self.orgs_client.list_roots()
            # NOTE: Assumes single root structure
            root_ou: OrganizationalUnitTypeDef = {
                "Id": list_root_response["Roots"][0]["Id"],
                "Arn": list_root_response["Roots"][0]["Arn"],
                "Name": list_root_response["Roots"][0]["Name"],
            }
            return root_ou

        # Child of non-Root OU
        describe_ou_response = self.orgs_client.describe_organizational_unit(
            OrganizationalUnitId=parent["Id"]
        )
        parent_ou: OrganizationalUnitTypeDef = describe_ou_response[
            "OrganizationalUnit"
        ]
        return parent_ou

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

    def account_is_member_of_root(self, account_id: str) -> bool:
        # Handles (future) multi-parent case
        account_parents = self.get_parents_from_account_id(account_id=account_id)
        return any([parent["Type"] == "ROOT" for parent in account_parents])

    def ou_contains_account(self, ou_name: str, account_id: str) -> bool:
        # NOTE: Assumes single-parent accounts
        current_ou = self.get_ou_from_account_id(account_id=account_id)
        if current_ou:
            if ou_name == current_ou["Name"]:
                return True
        return False

    @resubmit_request_on_boto_throttle
    def tag_org_resource(
        self,
        resource: str,
        tags: Sequence[TagTypeDef],
        rollback: bool = False,
    ) -> None:
        if rollback:
            current_tags = self.orgs_client.list_tags_for_resource(ResourceId=resource)
            self.orgs_client.untag_resource(
                ResourceId=resource, TagKeys=[tag["Key"] for tag in tags]
            )
            self.orgs_client.tag_resource(
                ResourceId=resource, Tags=cast(Sequence[TagTypeDef], current_tags)
            )

        else:
            self.orgs_client.tag_resource(ResourceId=resource, Tags=tags)

    def list_tags_for_resource(self, resource: str) -> List[TagTypeDef]:
        return self.orgs_client.list_tags_for_resource(ResourceId=resource)["Tags"]

    def get_account_email_from_id(self, account_id: str) -> str:
        response: DescribeAccountResponseTypeDef = self.orgs_client.describe_account(
            AccountId=account_id
        )
        return response["Account"]["Email"]

    def get_account_id_from_email(
        self, email: str, ou_name: Optional[str] = None
    ) -> str:
        if ou_name is not None:
            # If OU known, search it instead of the entire org; supports nested OU format
            # NOTE: Be careful using this parameter as the OU in account request is
            # NOT always equal to the OU an account is currently in (move-OU requests)
            account_ids_in_ou = self.get_account_ids_in_ous(ou_names=[ou_name])
            for account_id in account_ids_in_ou:
                account_email = self.get_account_email_from_id(account_id=account_id)
                if emails_are_equal(account_email, email):
                    return account_id

        for account in self.get_all_org_accounts():
            if emails_are_equal(account["Email"], email):
                return account["Id"]

        raise Exception(f"Account email {email} not found in Organization")

    def get_aft_account_info(self, account_id: str) -> AftAccountInfo:
        logger.info(f"Getting details for {account_id}")

        describe_response = self.orgs_client.describe_account(AccountId=account_id)
        account = describe_response["Account"]

        # NOTE: Assumes single-parent accounts
        parents = self.get_parents_from_account_id(account_id=account_id)
        parent = parents[0]

        aft_account_info = AftAccountInfo(
            id=account["Id"],
            email=account["Email"],
            name=account["Name"],
            joined_method=account["JoinedMethod"],
            joined_date=str(account["JoinedTimestamp"]),
            status=account["Status"],
            parent_id=parent["Id"],
            parent_type=parent["Type"],
            type="account",
            vendor="aws",
        )

        logger.info(f"Account details: {aft_account_info}")

        return aft_account_info
