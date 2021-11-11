import inspect
import os
import sys
import boto3
import aft_common.aft_utils as utils

logger = utils.get_logger()


def get_pipeline_for_account(session, account):
    try:
        current_account = session.client('sts').get_caller_identity().get('Account')
        current_region = session.region_name
        client = session.client('codepipeline')
        logger.info("Getting pipeline name for " + account)
        response = client.list_pipelines()
        for p in response['pipelines']:
            name = p['name']
            if name.startswith(account + "-"):
                pipeline_arn = "arn:aws:codepipeline:" + current_region + ":" + current_account + ":" + name
                response = client.list_tags_for_resource(
                    resourceArn=pipeline_arn
                )
                for t in response['tags']:
                    if t['key'] == 'managed_by' and t['value'] == 'AFT':
                        return p['name']

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def pipeline_is_running(session, name):
    try:
        client = session.client('codepipeline')

        logger.info("Getting pipeline executions for " + name)
        response = client.list_pipeline_executions(
            pipelineName=name
        )
        logger.info(response)
        latest_execution = sorted(response['pipelineExecutionSummaries'], key=lambda i: i['startTime'], reverse=True)[0]
        logger.info("Latest Execution: ")
        logger.info(latest_execution)
        if latest_execution['status'] == 'InProgress':
            return True
        else:
            return False

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def execute_pipeline(session, account):
    try:
        client = session.client('codepipeline')
        name = get_pipeline_for_account(session, account)
        if not pipeline_is_running(session, name):
            logger.info("Executing pipeline - " + name)
            response = client.start_pipeline_execution(
                name=name
            )
            logger.info(response)
        else:
            logger.info("Pipeline is currently running")

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
        logger.info("Lambda_handler Event")
        logger.info(event)
        session = boto3.session.Session()
        maximum_concurrent_pipelines = int(utils.get_ssm_parameter_value(
            session, utils.SSM_PARAM_AFT_MAXIMUM_CONCURRENT_CUSTOMIZATIONS
        ))

        running_pipelines = int(event['running_executions']['running_pipelines'])
        pipelines_to_run = maximum_concurrent_pipelines - running_pipelines
        accounts = event['targets']['pending_accounts']
        logger.info("Accounts submitted for execution: " + str(len(accounts)))
        for p in accounts[:pipelines_to_run]:
            execute_pipeline(session, str(p))
            accounts.remove(p)
        logger.info("Accounts remaining to be executed - ")
        logger.info(accounts)
        return {
            'number_pending_accounts': len(accounts),
            'pending_accounts': accounts
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
