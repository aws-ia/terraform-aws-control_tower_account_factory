# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
import logging
import re
from typing import Any, List

import aft_common.aft_utils as utils
from boto3.session import Session

logger = logging.getLogger("aft")

AFT_CUSTOMIZATIONS_PIPELINE_NAME_PATTERN = r"^\d\d\d\d\d\d\d\d\d\d\d\d-.*$"


def get_pipeline_for_account(session: Session, account_id: str) -> str:
    current_account = session.client("sts").get_caller_identity()["Account"]
    current_region = session.region_name

    sanitized_account_id = utils.sanitize_input_for_logging(account_id)
    logger.info("Getting pipeline name for " + sanitized_account_id)

    client = session.client("codepipeline", config=utils.get_high_retry_botoconfig())
    paginator = client.get_paginator("list_pipelines")

    pipelines = []
    for page in paginator.paginate():
        pipelines.extend(page["pipelines"])

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
    raise Exception(
        "Pipelines for account id " + sanitized_account_id + " was not found"
    )


def pipeline_is_running(session: Session, name: str) -> bool:
    logger.info("Getting pipeline executions for " + name)

    client = session.client("codepipeline", config=utils.get_high_retry_botoconfig())
    paginator = client.get_paginator("list_pipeline_executions")

    pipeline_execution_summaries = []
    for page in paginator.paginate(pipelineName=name):
        pipeline_execution_summaries.extend(page["pipelineExecutionSummaries"])

    if not pipeline_execution_summaries:
        # No executions for this pipeline in the last 12 months, so cannot be currently running
        return False

    latest_execution = sorted(
        pipeline_execution_summaries, key=lambda i: i["startTime"], reverse=True  # type: ignore
    )[0]

    logger.info(f"Latest Execution: {latest_execution}")
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
        sanitized_response = utils.sanitize_input_for_logging(response)
        logger.info(sanitized_response)
    else:
        logger.info("Pipeline is currently running")


def list_pipelines(session: Session) -> List[Any]:
    logger.info("Listing Pipelines - ")

    client = session.client("codepipeline", config=utils.get_high_retry_botoconfig())
    paginator = client.get_paginator("list_pipelines")

    pipelines = []
    for page in paginator.paginate():
        pipelines.extend(page["pipelines"])

    pattern = re.compile(AFT_CUSTOMIZATIONS_PIPELINE_NAME_PATTERN)
    matched_pipelines = []
    for p in pipelines:
        if re.match(pattern, p["name"]):
            matched_pipelines.append(p["name"])

    logger.info("The following pipelines were matched: " + str(matched_pipelines))
    return matched_pipelines


def get_running_pipeline_count(session: Session, pipeline_names: List[str]) -> int:
    pipeline_counter = 0
    client = session.client("codepipeline", config=utils.get_high_retry_botoconfig())

    for name in pipeline_names:
        logger.info("Getting pipeline executions for " + name)

        paginator = client.get_paginator("list_pipeline_executions")
        pipeline_execution_summaries = []
        for page in paginator.paginate(pipelineName=name):
            pipeline_execution_summaries.extend(page["pipelineExecutionSummaries"])

        if not pipeline_execution_summaries:
            # No executions for this pipeline in the last 12 months
            continue
        else:
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
        logger.info(
            f"Deleted customization pipeline for {utils.sanitize_input_for_logging(account_id)}"
        )
    else:
        logger.warning(
            f"Cannot delete running customization pipeline: {pipeline_name}, skipping"
        )
