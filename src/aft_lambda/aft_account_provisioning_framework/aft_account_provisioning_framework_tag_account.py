import inspect
from typing import Any, Dict, Union

import aft_common.aft_utils as utils
from aft_common.account_provisioning_framework import tag_account
from boto3.session import Session

logger = utils.get_logger()


def lambda_handler(event: Dict[str, Any], context: Union[Dict[str, Any], None]) -> None:
    try:
        logger.info("AFT Account Provisioning Framework Handler Start")

        rollback = False
        try:
            if event["rollback"]:
                rollback = True
        except KeyError:
            pass

        payload = event["payload"]
        action = event["action"]

        session = Session()
        ct_management_session = utils.get_ct_management_session(session)

        if action == "tag_account":
            account_info = payload["account_info"]["account"]
            tag_account(payload, account_info, ct_management_session, rollback)
        else:
            raise Exception(
                "Incorrect Command Passed to Lambda Function. Input: {action}. Expected: 'tag_account'"
            )

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise
