import inspect
from typing import Any, Dict, Union

import aft_common.aft_utils as utils
import boto3

logger = utils.get_logger()


def lambda_handler(
    event: Dict[str, Any], context: Union[Dict[str, Any], None]
) -> Dict[str, Any]:
    try:
        logger.info("Lambda_handler Event")
        logger.info(event)

        try:
            session = boto3.session.Session()

            response: Dict[str, Any] = utils.put_ddb_item(
                session,
                utils.get_ssm_parameter_value(
                    session, utils.SSM_PARAM_AFT_EVENTS_TABLE
                ),
                event,
            )
            return response

        except Exception as e:
            message = {
                "FILE": __file__.split("/")[-1],
                "METHOD": inspect.stack()[0][3],
                "EXCEPTION": str(e),
            }
            logger.exception(message)
            raise

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
