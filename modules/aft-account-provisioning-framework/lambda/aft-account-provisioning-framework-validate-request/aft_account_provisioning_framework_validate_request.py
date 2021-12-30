import inspect
import json
import os
from typing import Any, Dict, Union

import aft_common.aft_utils as utils
import jsonschema

logger = utils.get_logger()


def validate_request(payload: Dict[str, Any]) -> bool:
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


def lambda_handler(event: Dict[str, Any], context: Union[Dict[str, Any], None]) -> bool:
    try:
        logger.info("AFT Account Provisioning Framework Handler Start")

        payload = event["payload"]
        action = event["action"]

        if action == "validate":
            request_validated = validate_request(payload)
            return request_validated
        else:
            raise Exception(
                "Incorrect Command Passed to Lambda Function. Input: {action}. Expected: 'validate'"
            )

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
