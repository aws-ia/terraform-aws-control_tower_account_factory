import inspect
import json
import os
import sys
import boto3
import aft_common.aft_utils as utils

logger = utils.get_logger()


def get_account_metadata_record(session, table, account_id):
    try:
        dynamodb = session.resource('dynamodb')
        table = dynamodb.Table(table)
        logger.info("Getting account metadata record for " + account_id)
        response = table.get_item(
            Key={
                'id': account_id
            }
        )
        logger.info(response['Item'])
        return response['Item']

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def get_account_request_record(session, table, email_address):
    try:
        dynamodb = session.resource('dynamodb')
        table = dynamodb.Table(table)
        logger.info("Getting account request record for " + email_address)
        response = table.get_item(
            Key={
                'id': email_address
            }
        )
        logger.info(response['Item'])
        return response['Item']

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def build_invoke_event(account_request_record):
    try:
        logger.info("Building invoke event for " + str(account_request_record))
        account_request_record['account_tags'] = json.loads(account_request_record['account_tags'])
        invoke_event = {'account_request': account_request_record, 'control_tower_event': {},
                        'account_provisioning': {}}
        invoke_event['account_provisioning']['run_create_pipeline'] = "false"

        logger.info(str(invoke_event))
        return invoke_event

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def invoke_account_provisioning_sfn(session, sfn_name, event):
    try:
        client = session.client('stepfunctions')
        logger.info("Invoking SFN - " + sfn_name)
        response = client.start_execution(
            stateMachineArn=utils.build_sfn_arn(session, sfn_name),
            input=json.dumps(event)
        )
        logger.info(response)

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def lambda_handler(event, context):
    try:
        if event["offline"]:
            return True
    except KeyError:
        pass

    try:
        logger.info("Lambda_handler Event")
        logger.info(event)
        session = boto3.session.Session()

        pending_account_ids = event['targets']['pending_accounts']
        account_metadata_table = utils.get_ssm_parameter_value(session, utils.SSM_PARAM_AFT_DDB_META_TABLE)
        account_request_table = utils.get_ssm_parameter_value(session, utils.SSM_PARAM_AFT_DDB_REQ_TABLE)
        provisioning_framework_sfn = utils.get_ssm_parameter_value(session, utils.SSM_PARAM_AFT_SFN_NAME)

        for a in pending_account_ids:
            account_metadata_record = get_account_metadata_record(session, account_metadata_table, a)
            account_request_email = account_metadata_record['email']
            account_request_record = get_account_request_record(session, account_request_table, account_request_email)
            sfn_event = build_invoke_event(account_request_record)
            invoke_account_provisioning_sfn(session, provisioning_framework_sfn, sfn_event)

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
