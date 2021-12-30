import inspect
from typing import Any, Dict, Optional

import aft_common.aft_utils as utils
import boto3
from aft_common.premium_support import account_enrollment_requested, generate_case

logger = utils.get_logger()

SUPPORT_API_REGION = "us-east-1"


def lambda_handler(event: Dict[str, Any], context: Optional[Dict[str, Any]]) -> None:

    try:
        logger.info("Lambda_handler Event")
        logger.info(event)
        aft_session = boto3.session.Session()
        ct_mgmt_session = utils.get_ct_management_session(aft_session)
        target_account_id = event["account_info"]["account"]["id"]
        if (
            utils.get_ssm_parameter_value(
                aft_session, utils.SSM_PARAM_FEATURE_ENTERPRISE_SUPPORT_ENABLED
            ).lower()
            == "true"
        ):
            if not account_enrollment_requested(ct_mgmt_session, target_account_id):
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
