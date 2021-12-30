import inspect
import re
from typing import Any, Dict, List, Union

import aft_common.aft_utils as utils
import boto3
from boto3.session import Session

logger = utils.get_logger()

CUSTOMIZATIONS_PIPELINE_PATTERN = "^\d\d\d\d\d\d\d\d\d\d\d\d-.*$"


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


def lambda_handler(
    event: Dict[str, Any], context: Union[Dict[str, Any], None]
) -> Dict[str, int]:

    logger.info("Lambda_handler Event")
    logger.info(event)

    try:
        session = boto3.session.Session()
        pipelines = list_pipelines(session)
        running_pipelines = get_running_pipeline_count(session, pipelines)

        return {"running_pipelines": running_pipelines}

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


if __name__ == "__main__":
    import json
    import sys
    from optparse import OptionParser

    logger.info("Local Execution")
    parser = OptionParser()
    parser.add_option(
        "-f", "--event-file", dest="event_file", help="Event file to be processed"
    )
    (options, args) = parser.parse_args(sys.argv)
    if options.event_file is not None:
        with open(options.event_file) as json_data:
            event = json.load(json_data)
            lambda_handler(event, None)
    else:
        lambda_handler({}, None)
