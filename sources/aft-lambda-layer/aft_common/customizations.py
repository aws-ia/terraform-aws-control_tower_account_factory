# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import json
import logging
import os
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import jsonschema
from aft_common.aft_utils import get_high_retry_botoconfig
from aft_common.constants import SSM_PARAM_AFT_DDB_META_TABLE
from aft_common.organizations import OrganizationsAgent
from aft_common.ssm import get_ssm_parameter_value
from boto3.session import Session

if TYPE_CHECKING:
    from mypy_boto3_organizations import OrganizationsClient
else:
    OrganizationsClient = object

AFT_SHARED_ACCOUNT_NAMES = ["ct-management", "log-archive", "audit"]

logger = logging.getLogger("aft")


def validate_identify_targets_request(payload: Dict[str, Any]) -> bool:
    logger.info("Function Start - validate_identify_targets_request")
    schema_path = os.path.join(
        os.path.dirname(__file__), "schemas/identify_targets_request_schema.json"
    )
    with open(schema_path) as schema_file:
        schema_object = json.load(schema_file)
    logger.info("Schema Loaded:" + json.dumps(schema_object))
    validated = jsonschema.validate(payload, schema_object)
    if validated is None:
        logger.info("Request Validated")
        return True
    else:
        raise Exception("Failure validating request.\n{validated}")


def get_all_aft_account_ids(aft_management_session: Session) -> List[str]:
    table_name = get_ssm_parameter_value(
        aft_management_session, SSM_PARAM_AFT_DDB_META_TABLE
    )
    dynamodb = aft_management_session.resource("dynamodb")
    table = dynamodb.Table(table_name)
    logger.info("Scanning DynamoDB table: " + table_name)

    items: List[Dict[str, Any]] = []
    response = table.scan(ProjectionExpression="id", ConsistentRead=True)
    items.extend(response["Items"])
    while "LastEvaluatedKey" in response:
        logger.debug(
            "Paginated response found, continuing at {}".format(
                response["LastEvaluatedKey"]
            )
        )
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response["Items"])

    aft_account_ids = [item["id"] for item in items]

    if not aft_account_ids:
        raise Exception("No accounts found in the Account Metadata table")

    return aft_account_ids


def filter_non_aft_accounts(
    session: Session, account_list: List[str], operation: str = "include"
) -> List[str]:
    aft_accounts = get_all_aft_account_ids(session)
    core_accounts = get_core_accounts(session)
    logger.info("Running AFT Filter for accounts " + str(account_list))
    filtered_accounts = []
    for a in account_list:
        logger.info("Evaluating account " + a)
        if a not in aft_accounts:
            if operation == "include":
                if a not in core_accounts:
                    logger.info("Account " + a + " is being filtered.")
                    filtered_accounts.append(a)
                else:
                    logger.info("Account " + a + " is NOT being filtered.")
        else:
            logger.info("Account " + a + " is NOT being filtered.")
    for a in filtered_accounts:
        if a in account_list:
            account_list.remove(a)
    return account_list


def get_core_accounts(aft_management_session: Session) -> List[str]:
    core_accounts = []
    logger.info("Getting core accounts -")
    for a in AFT_SHARED_ACCOUNT_NAMES:
        id = get_ssm_parameter_value(
            aft_management_session, "/aft/account/" + a + "/account-id"
        )
        logger.info("Account ID for " + a + " is " + id)
        core_accounts.append(id)
    logger.info("Core accounts: " + str(core_accounts))
    return core_accounts


# TODO: Refactor to method of OrganizationsAgent
def get_accounts_by_tags(
    aft_mgmt_session: Session, ct_mgmt_session: Session, tags: List[Dict[str, str]]
) -> Optional[List[str]]:
    logger.info("Getting Account with tags - " + str(tags))
    # Get all AFT Managed Accounts
    all_accounts = get_all_aft_account_ids(aft_mgmt_session)
    matched_accounts = []
    client: OrganizationsClient = ct_mgmt_session.client(
        "organizations", config=get_high_retry_botoconfig()
    )
    # Loop through AFT accounts, requesting tags
    if all_accounts is None:
        return None

    for a in all_accounts:
        account_tags = {}
        response = client.list_tags_for_resource(ResourceId=a)
        # Format tags as a dictionary rather than a list
        for t in response["Tags"]:
            account_tags[t["Key"]] = t["Value"]
        logger.info("Account tags for " + a + ": " + str(account_tags))
        counter = 0
        # Loop through tag filter. Append account to matched_accounts if all tags in filter match/ are present
        for x in tags:
            for k, v in x.items():
                if k in account_tags.keys():
                    if account_tags[k] == v:
                        counter += 1
                        if counter == len(tags):
                            logger.info(
                                "Account " + a + " MATCHED with tags " + str(tags)
                            )
                            matched_accounts.append(a)
    logger.info(matched_accounts)
    if len(matched_accounts) > 0:
        return matched_accounts
    else:
        return None


def get_included_accounts(
    aft_management_session: Session,
    ct_mgmt_session: Session,
    orgs_agent: OrganizationsAgent,
    included: List[Dict[str, Any]],
) -> List[str]:
    all_aft_accounts = get_all_aft_account_ids(aft_management_session)
    logger.info("All AFT accounts: " + str(all_aft_accounts))
    included_accounts = []
    for d in included:
        if d["type"] == "all":
            if all_aft_accounts is not None:
                included_accounts.extend(all_aft_accounts)
        if d["type"] == "core":
            core_accounts = get_core_accounts(aft_management_session)
            included_accounts.extend(core_accounts)
        if d["type"] == "ous":
            included_accounts.extend(
                orgs_agent.get_account_ids_in_ous(ou_names=d["target_value"])
            )
        if d["type"] == "tags":
            tag_accounts = get_accounts_by_tags(
                aft_management_session, ct_mgmt_session, d["target_value"]
            )
            if tag_accounts is not None:
                included_accounts.extend(tag_accounts)
        if d["type"] == "accounts":
            included_accounts.extend(d["target_value"])
    # Remove Duplicates
    included_accounts = list(set(included_accounts))
    logger.info("Included Accounts (pre-AFT filter): " + str(included_accounts))

    # Filter non-AFT accounts
    included_accounts = filter_non_aft_accounts(
        aft_management_session, included_accounts
    )

    logger.info("Included Accounts (post-AFT filter): " + str(included_accounts))
    return included_accounts


def get_excluded_accounts(
    aft_management_session: Session,
    ct_mgmt_session: Session,
    orgs_agent: OrganizationsAgent,
    excluded: List[Dict[str, Any]],
) -> List[str]:
    excluded_accounts = []
    for d in excluded:
        if d["type"] == "core":
            core_accounts = get_core_accounts(aft_management_session)
            excluded_accounts.extend(core_accounts)
        if d["type"] == "ous":
            excluded_accounts.extend(
                orgs_agent.get_account_ids_in_ous(ou_names=d["target_value"])
            )
        if d["type"] == "tags":
            tag_accounts = get_accounts_by_tags(
                aft_management_session, ct_mgmt_session, d["target_value"]
            )
            if tag_accounts is not None:
                excluded_accounts.extend(tag_accounts)
        if d["type"] == "accounts":
            excluded_accounts.extend(d["target_value"])
    # Remove Duplicates
    excluded_accounts = list(set(excluded_accounts))
    logger.info("Excluded Accounts (pre-AFT filter): " + str(excluded_accounts))

    # Filter non-AFT accounts
    excluded_accounts = filter_non_aft_accounts(
        aft_management_session, excluded_accounts, "exclude"
    )

    logger.info("Excluded Accounts (post-AFT filter): " + str(excluded_accounts))
    return excluded_accounts


def get_target_accounts(
    included_accounts: List[str], excluded_accounts: List[str]
) -> List[str]:
    for i in excluded_accounts:
        if i in included_accounts:
            included_accounts.remove(i)
    logger.info("TARGET ACCOUNTS: " + str(included_accounts))
    return included_accounts
