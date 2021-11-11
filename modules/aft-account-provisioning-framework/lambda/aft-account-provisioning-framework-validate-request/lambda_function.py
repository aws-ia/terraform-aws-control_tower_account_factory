import json
import os

import boto3
import jsonschema
import aft_common.aft_utils as utils
from boto3.dynamodb.conditions import Key


logger = utils.get_logger()


def validate_request(payload, logger):
    logger.info("Function Start - validate_request")
    schema_path = os.path.join(os.path.dirname(__file__), "schema/request_schema.json")
    with open(schema_path) as schema_file:
        schema_object = json.load(schema_file)
    logger.info("Schema Loaded:" + json.dumps(schema_object))
    validated = jsonschema.validate(payload, schema_object)
    if validated is None:
        logger.info("Request Validated")
        return True
    else:
        raise Exception("Failure validating request.\n{validated}")


def lambda_handler(event, context):
    logger.info("AFT Account Provisioning Framework Handler Start")

    payload = event['payload']
    action = event['action']

    if action == "validate":
        request_validated = validate_request(payload, logger)
        return request_validated
    else:
        raise BaseException(
            "Incorrect Command Passed to Lambda Function. Input: {action}. Expected: 'validate'"
        )


if __name__ == "__main__":
    event = {}
    example_file = os.path.join(os.path.dirname(__file__), "schema/example_event.json")
    with open(example_file) as json_data:
        event = json.load(json_data)
    lambda_handler(event, None)
