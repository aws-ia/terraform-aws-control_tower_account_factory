import inspect
import sys
from typing import Any, Dict, Union

import aft_common.aft_utils as utils
from aft_common.customizations import (
    get_excluded_accounts,
    get_included_accounts,
    get_target_accounts,
    validate_request,
)
from boto3.session import Session

logger = utils.get_logger()


def lambda_handler(
    event: Dict[str, Any], context: Union[Dict[str, Any], None]
) -> Dict[str, Any]:

    logger.info("Lambda_handler Event")
    logger.info(event)

    try:
        payload = event
        if not validate_request(payload):
            sys.exit(1)
        else:
            session = Session()
            ct_mgmt_session = utils.get_ct_management_session(session)
            included_accounts = get_included_accounts(
                session, ct_mgmt_session, payload["include"]
            )
            if "exclude" in payload.keys():
                excluded_accounts = get_excluded_accounts(
                    session, ct_mgmt_session, payload["exclude"]
                )
                target_accounts = get_target_accounts(
                    included_accounts, excluded_accounts
                )
            else:
                target_accounts = included_accounts

            return {
                "number_pending_accounts": len(target_accounts),
                "pending_accounts": target_accounts,
            }

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise
