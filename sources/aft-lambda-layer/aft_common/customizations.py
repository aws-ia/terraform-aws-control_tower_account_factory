import json
import os
import re
from typing import Any, Dict, List

import aft_common.aft_utils as utils
import jsonschema
from boto3.session import Session

CUSTOMIZATIONS_PIPELINE_PATTERN = "^\d\d\d\d\d\d\d\d\d\d\d\d-.*$"

AFT_PIPELINE_ACCOUNTS = ["ct-management", "log-archive", "audit"]

logger = utils.get_logger()


def get_pipeline_for_account(session: Session, account: str) -> str:
    current_account = session.client("sts").get_caller_identity()["Account"]
    current_region = session.region_name
    client = session.client("codepipeline")
    logger.info("Getting pipeline name for " + account)

    response = client.list_pipelines()

    pipelines = response["pipelines"]
    while "nextToken" in response:
        response = client.list_pipelines(nextToken=response["nextToken"])
        pipelines.extend(response["pipelines"])

    for p in pipelines:
        name = p["name"]
        if name.startswith(account + "-"):
            pipeline_arn = (
                "arn:aws:codepipeline:"
                + current_region
                + ":"
                + current_account
                + ":"
                + name
            )
            response = client.list_tags_for_resource(resourceArn=pipeline_arn)
            for t in response["tags"]:
                if t["key"] == "managed_by" and t["value"] == "AFT":
                    pipeline_name: str = p["name"]
                    return pipeline_name
    raise Exception("Pipelines for account id " + current_account + " was not found")


def pipeline_is_running(session: Session, name: str) -> bool:
    client = session.client("codepipeline")

    logger.info("Getting pipeline executions for " + name)

    response = client.list_pipeline_executions(pipelineName=name)
    pipeline_execution_summaries = response["pipelineExecutionSummaries"]

    while "nextToken" in response:
        response = client.list_pipeline_executions(
            pipelineName=name, nextToken=response["nextToken"]
        )
        pipeline_execution_summaries.extend(response["pipelineExecutionSummaries"])

    latest_execution = sorted(
        pipeline_execution_summaries, key=lambda i: i["startTime"], reverse=True  # type: ignore
    )[0]
    logger.info("Latest Execution: ")
    logger.info(latest_execution)
    if latest_execution["status"] == "InProgress":
        return True
    else:
        return False


def execute_pipeline(session: Session, account: str) -> None:
    client = session.client("codepipeline")
    name = get_pipeline_for_account(session, account)
    if not pipeline_is_running(session, name):
        logger.info("Executing pipeline - " + name)
        response = client.start_pipeline_execution(name=name)
        logger.info(response)
    else:
        logger.info("Pipeline is currently running")


def list_pipelines(session: Session) -> List[Any]:
    pattern = re.compile(CUSTOMIZATIONS_PIPELINE_PATTERN)
    matched_pipelines = []
    client = session.client("codepipeline")
    logger.info("Listing Pipelines - ")

    response = client.list_pipelines()

    pipelines = response["pipelines"]
    while "nextToken" in response:
        response = client.list_pipelines(nextToken=response["nextToken"])
        pipelines.extend(response["pipelines"])

    for p in pipelines:
        if re.match(pattern, p["name"]):
            matched_pipelines.append(p["name"])

    logger.info("The following pipelines were matched: " + str(matched_pipelines))
    return matched_pipelines


def get_running_pipeline_count(session: Session, names: List[str]) -> int:
    pipeline_counter = 0
    client = session.client("codepipeline")

    for p in names:
        logger.info("Getting pipeline executions for " + p)

        response = client.list_pipeline_executions(pipelineName=p)
        pipeline_execution_summaries = response["pipelineExecutionSummaries"]

        while "nextToken" in response:
            response = client.list_pipeline_executions(
                pipelineName=p, nextToken=response["nextToken"]
            )
            pipeline_execution_summaries.extend(response["pipelineExecutionSummaries"])

        latest_execution = sorted(
            pipeline_execution_summaries, key=lambda i: i["startTime"], reverse=True  # type: ignore
        )[0]
        logger.info("Latest Execution: ")
        logger.info(latest_execution)

        if latest_execution["status"] == "InProgress":
            pipeline_counter += 1

    logger.info("The number of running pipelines is " + str(pipeline_counter))

    return pipeline_counter


def validate_request(payload: Dict[str, Any]) -> bool:
    logger.info("Function Start - validate_request")
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


def filter_non_aft_accounts(
    session: Session, account_list: List[str], operation: str = "include"
) -> List[str]:
    aft_accounts = utils.get_all_aft_account_ids(session)
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


def get_core_accounts(session: Session) -> List[str]:
    core_accounts = []
    logger.info("Getting core accounts -")
    for a in AFT_PIPELINE_ACCOUNTS:
        id = utils.get_ssm_parameter_value(session, "/aft/account/" + a + "/account-id")
        logger.info("Account ID for " + a + " is " + id)
        core_accounts.append(id)
    logger.info("Core accounts: " + str(core_accounts))
    return core_accounts


def get_included_accounts(
    session: Session, ct_mgmt_session: Session, included: List[Dict[str, Any]]
) -> List[str]:
    all_aft_accounts = utils.get_all_aft_account_ids(session)
    logger.info("All AFT accounts: " + str(all_aft_accounts))
    included_accounts = []
    for d in included:
        if d["type"] == "all":
            if all_aft_accounts is not None:
                included_accounts.extend(all_aft_accounts)
        if d["type"] == "core":
            core_accounts = get_core_accounts(session)
            included_accounts.extend(core_accounts)
        if d["type"] == "ous":
            ou_accounts = utils.get_account_ids_in_ous(
                ct_mgmt_session, d["target_value"]
            )
            if ou_accounts is not None:
                included_accounts.extend(ou_accounts)
        if d["type"] == "tags":
            tag_accounts = utils.get_accounts_by_tags(
                session, ct_mgmt_session, d["target_value"]
            )
            if tag_accounts is not None:
                included_accounts.extend(tag_accounts)
        if d["type"] == "accounts":
            included_accounts.extend(d["target_value"])
    # Remove Duplicates
    included_accounts = list(set(included_accounts))
    logger.info("Included Accounts (pre-AFT filter): " + str(included_accounts))

    # Filter non-AFT accounts
    included_accounts = filter_non_aft_accounts(session, included_accounts)

    logger.info("Included Accounts (post-AFT filter): " + str(included_accounts))
    return included_accounts


def get_excluded_accounts(
    session: Session, ct_mgmt_session: Session, excluded: List[Dict[str, Any]]
) -> List[str]:
    excluded_accounts = []
    for d in excluded:
        if d["type"] == "core":
            core_accounts = get_core_accounts(session)
            excluded_accounts.extend(core_accounts)
        if d["type"] == "ous":
            ou_accounts = utils.get_account_ids_in_ous(
                ct_mgmt_session, d["target_value"]
            )
            if ou_accounts is not None:
                excluded_accounts.extend(ou_accounts)
        if d["type"] == "tags":
            tag_accounts = utils.get_accounts_by_tags(
                session, ct_mgmt_session, d["target_value"]
            )
            if tag_accounts is not None:
                excluded_accounts.extend(tag_accounts)
        if d["type"] == "accounts":
            excluded_accounts.extend(d["target_value"])
    # Remove Duplicates
    excluded_accounts = list(set(excluded_accounts))
    logger.info("Excluded Accounts (pre-AFT filter): " + str(excluded_accounts))

    # Filter non-AFT accounts
    excluded_accounts = filter_non_aft_accounts(session, excluded_accounts, "exclude")

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


def get_account_metadata_record(
    session: Session, table_name: str, account_id: str
) -> Dict[str, Any]:
    dynamodb = session.resource("dynamodb")
    table = dynamodb.Table(table_name)
    logger.info("Getting account metadata record for " + account_id)
    response = table.get_item(Key={"id": account_id})
    item: Dict[str, Any] = response["Item"]
    logger.info(item)
    return item


def get_account_request_record(
    session: Session, table_name: str, email_address: str
) -> Dict[str, Any]:
    dynamodb = session.resource("dynamodb")
    table = dynamodb.Table(table_name)
    logger.info("Getting account request record for " + email_address)
    response = table.get_item(Key={"id": email_address})
    item: Dict[str, Any] = response["Item"]
    logger.info(item)
    return item


def build_invoke_event(account_request_record: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Building invoke event for " + str(account_request_record))
    account_request_record["account_tags"] = json.loads(
        account_request_record["account_tags"]
    )
    invoke_event: Dict[str, Any]
    invoke_event = {
        "account_request": account_request_record,
        "control_tower_event": {},
        "account_provisioning": {},
    }
    invoke_event["account_provisioning"]["run_create_pipeline"] = "false"

    logger.info(str(invoke_event))
    return invoke_event


def invoke_account_provisioning_sfn(
    session: Session, sfn_name: str, event: Dict[str, Any]
) -> None:
    client = session.client("stepfunctions")
    logger.info("Invoking SFN - " + sfn_name)
    response = client.start_execution(
        stateMachineArn=utils.build_sfn_arn(session, sfn_name),
        input=json.dumps(event),
    )
    logger.info(response)
