import inspect
import os
import boto3
import aft_common.aft_utils as utils
from datetime import datetime

logger = utils.get_logger()


def put_audit_record(session, table, image, event_name):
    try:
        dynamodb = session.client("dynamodb")
        item = image

        datetime_format = "%Y-%m-%dT%H:%M:%S.%f"
        current_time = datetime.now().strftime(datetime_format)
        item["timestamp"] = {"S": current_time}

        item["ddb_event_name"] = {"S": event_name}

        logger.info("Inserting item into " + table + " table: " + str(item))

        response = dynamodb.put_item(TableName=table, Item=item)

        logger.info(response)

        return response

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
        print(event)
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
                    table_name = utils.get_ssm_parameter_value(
                        session, utils.SSM_PARAM_AFT_DDB_AUDIT_TABLE
                    )
                    event_name = event_record["eventName"]

                    supported_events = {"INSERT", "MODIFY", "REMOVE"}

                    image_key_name = "OldImage" if event_name == "REMOVE" else "NewImage"
                    image_to_record = event_record["dynamodb"][image_key_name]

                    if event_name in supported_events:
                        logger.info("Event Name: " + event_name)
                        response = put_audit_record(
                            session, table_name, image_to_record, event_name
                        )
                    else:
                        logger.info(f"Event Name: {event_name} is unsupported.")
                else:
                    logger.info("Non DynamoDB Event Received")
                    sys.exit(1)
            return response
        else:
            logger.info("Unexpected Event Received")

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
