# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
import re
from typing import Any, List

import aft_common.aft_utils as utils
from boto3.session import Session

logger = utils.get_logger()

AFT_CUSTOMIZATIONS_PIPELINE_NAME_PATTERN = "^\d\d\d\d\d\d\d\d\d\d\d\d-.*$"


def get_pipeline_for_account(session: Session, account_id: str) -> str:
    current_account = session.client("sts").get_caller_identity()["Account"]
    current_region = session.region_name
    client = session.client("codepipeline")
    logger.info("Getting pipeline name for " + account_id)

    response = client.list_pipelines()

    pipelines = response["pipelines"]
    while "nextToken" in response:
        response = client.list_pipelines(nextToken=response["nextToken"])
        pipelines.extend(response["pipelines"])

    for p in pipelines:
        name = p["name"]
        if name.startswith(account_id + "-"):
            pipeline_arn = (
                f"arn:{utils.get_aws_partition(session)}:codepipeline:"
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
    raise Exception("Pipelines for account id " + account_id + " was not found")


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


def execute_pipeline(session: Session, account_id: str) -> None:
    client = session.client("codepipeline")
    name = get_pipeline_for_account(session, account_id)
    if not pipeline_is_running(session, name):
        logger.info("Executing pipeline - " + name)
        response = client.start_pipeline_execution(name=name)
        logger.info(response)
    else:
        logger.info("Pipeline is currently running")


def list_pipelines(session: Session) -> List[Any]:
    pattern = re.compile(AFT_CUSTOMIZATIONS_PIPELINE_NAME_PATTERN)
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


def delete_customization_pipeline(
    aft_management_session: Session, account_id: str
) -> None:
    client = aft_management_session.client("codepipeline")

    pipeline_name = get_pipeline_for_account(
        session=aft_management_session, account_id=account_id
    )
    if not pipeline_is_running(session=aft_management_session, name=pipeline_name):
        client.delete_pipeline(name=pipeline_name)
        logger.info(f"Deleted customization pipeline for {account_id}")
    else:
        logger.warning(
            f"Cannot delete running customization pipeline: {pipeline_name}, skipping"
        )
