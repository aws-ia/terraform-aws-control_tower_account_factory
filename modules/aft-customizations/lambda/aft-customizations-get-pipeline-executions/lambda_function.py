import inspect
import boto3
import re
import aft_common.aft_utils as utils

logger = utils.get_logger()

CUSTOMIZATIONS_PIPELINE_PATTERN = "^\d\d\d\d\d\d\d\d\d\d\d\d-.*$"


def list_pipelines(session):
    try:
        pattern = re.compile(CUSTOMIZATIONS_PIPELINE_PATTERN)
        pipelines = []
        client = session.client('codepipeline')
        logger.info("Listing Pipelines - ")
        response = client.list_pipelines()
        logger.info(response)

        for p in response['pipelines']:
            if re.match(pattern, p['name']):
                pipelines.append(p['name'])

        logger.info("The following pipelines were matched: " + str(pipelines))
        return pipelines

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def get_running_pipeline_count(session, names):
    try:
        pipeline_counter = 0
        client = session.client('codepipeline')

        for p in names:
            logger.info("Getting pipeline executions for " + p)
            response = client.list_pipeline_executions(
                pipelineName=p
            )
            logger.info(response)
            latest_execution = sorted(response['pipelineExecutionSummaries'], key=lambda i: i['startTime'], reverse=True)[0]
            logger.info ("Latest Execution: ")
            logger.info(latest_execution)
            if latest_execution['status'] == 'InProgress':
                pipeline_counter += 1
        logger.info("The number of running pipelines is " + str(pipeline_counter))
        return pipeline_counter

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def lambda_handler(event, context):
    logger.info("Lambda_handler Event")
    logger.info(event)
    try:
        if event["offline"]:
            return True
    except KeyError:
        pass

    try:
        session = boto3.session.Session()
        pipelines = list_pipelines(session)
        running_pipelines = get_running_pipeline_count(session, pipelines)

        return {
            'running_pipelines': running_pipelines
        }

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
