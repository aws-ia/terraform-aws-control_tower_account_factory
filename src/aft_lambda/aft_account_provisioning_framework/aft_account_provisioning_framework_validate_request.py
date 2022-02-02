import inspect
from typing import Any, Dict, Union

import aft_common.aft_utils as utils
from aft_common.account_provisioning_framework import validate_request

logger = utils.get_logger()


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
