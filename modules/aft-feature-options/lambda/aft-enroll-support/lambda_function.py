import inspect
import os
import sys
import boto3
import botocore
import aft_common.aft_utils as utils

logger = utils.get_logger()


def lookup_cases(session, account_id):
    try:
        client = session.client('support', region_name='us-east-1')
        response = client.describe_cases(
            includeResolvedCases=True,
            language='en',
            includeCommunications=False
        )
        for c in response['cases']:
            if c['subject'] == "Add Account " + account_id + " to Enterprise Support":
                return True

        return False

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def generate_case(session, account_id):
    try:
        support = session.client('support')
        support.create_case(
            issueType='customer-service',
            serviceCode='account-management',
            categoryCode='billing',
            severityCode='low',
            subject=f'Add Account {account_id} to Enterprise Support',
            communicationBody=f'Please add account number {account_id} to our enterprise support plan.',
            language='en'
        )
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
        aft_session = boto3.session.Session()
        ct_mgmt_session = utils.get_ct_management_session(aft_session)
        target_account_id = event['account_info']['account']['id']
        if utils.get_ssm_parameter_value(aft_session,
                                         utils.SSM_PARAM_FEATURE_ENTERPRISE_SUPPORT_ENABLED).lower() == 'true':
            if not lookup_cases(ct_mgmt_session, target_account_id):
                generate_case(ct_mgmt_session, target_account_id)


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
