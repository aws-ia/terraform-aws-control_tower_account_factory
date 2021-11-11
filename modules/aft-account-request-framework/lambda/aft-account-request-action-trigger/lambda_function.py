import inspect
import json
import os
import boto3
import aft_common.aft_utils as utils

logger = utils.get_logger()

def new_account_request(record):
    try:
        if record["eventName"] == "INSERT":
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


def modify_account_request(record):
    try:
        if record["eventName"] == "MODIFY":
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


def delete_account_request(record):
    try:
        if record["eventName"] == "REMOVE":
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


def control_tower_param_changed(record):
    try:
        if record["eventName"] == "MODIFY":
            old_image = utils.unmarshal_ddb_item(record["dynamodb"]["OldImage"])["control_tower_parameters"]
            new_image = utils.unmarshal_ddb_item(record["dynamodb"]["NewImage"])["control_tower_parameters"]

            if old_image != new_image:
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


def build_sqs_message(record):
    try:
        logger.info("Building SQS Message - ")
        message = {}
        operation = record["eventName"]

        new_image = utils.unmarshal_ddb_item(record["dynamodb"]["NewImage"])
        message["operation"] = operation
        message["control_tower_parameters"] = new_image["control_tower_parameters"]

        if operation == "MODIFY":
            old_image = utils.unmarshal_ddb_item(record["dynamodb"]["OldImage"])
            message["old_control_tower_parameters"] = old_image[
                "control_tower_parameters"
            ]

        logger.info(message)
        return message

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def build_aft_account_provisioning_framework_event(record):
    try:
        account_request = utils.unmarshal_ddb_item(record["dynamodb"]["NewImage"])
        aft_account_provisioning_framework_event = {
            "account_request": account_request,
            "control_tower_event": {},
        }
        logger.info(aft_account_provisioning_framework_event)
        return aft_account_provisioning_framework_event

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

        # validate event
        if "Records" in event:
            response = None
            event_record = event["Records"][0]
            if "eventSource" in event_record:
                if event_record["eventSource"] == "aws:dynamodb":
                    logger.info("DynamoDB Event Record Received")
                    if new_account_request(event_record):
                        logger.info("New Account Request Received")
                        sqs_queue = utils.get_ssm_parameter_value(
                            session, utils.SSM_PARAM_ACCOUNT_REQUEST_QUEUE
                        )
                        sqs_queue = utils.build_sqs_url(session, sqs_queue)
                        message = build_sqs_message(event_record)
                        response = utils.send_sqs_message(session, sqs_queue, message)
                    elif modify_account_request(event_record):
                        if control_tower_param_changed(event_record):
                            logger.info(
                                "Control Tower Parameter Update Request Received"
                            )
                            sqs_queue = utils.get_ssm_parameter_value(
                                session, utils.SSM_PARAM_ACCOUNT_REQUEST_QUEUE
                            )
                            sqs_queue = utils.build_sqs_url(session, sqs_queue)
                            message = build_sqs_message(event_record)
                            response = utils.send_sqs_message(session, sqs_queue, message)
                        else:
                            logger.info(
                                "NON-Control Tower Parameter Update Request Received"
                            )
                            payload = json.dumps(build_aft_account_provisioning_framework_event(event_record))
                            lambda_name = utils.get_ssm_parameter_value(
                                session, utils.SSM_PARAM_AFT_ACCOUNT_PROVISIONING_FRAMEWORK_LAMBDA
                            )
                            response = utils.invoke_lambda(session, lambda_name, payload)
                    elif delete_account_request(event_record):
                        logger.info("Delete account request Received")
                    else:
                        logger.info("Non Service Catalog Request Received")

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
