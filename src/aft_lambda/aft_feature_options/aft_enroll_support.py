import inspect
from typing import Any, Dict, Optional

import aft_common.aft_utils as utils
from aft_common.premium_support import account_enrollment_requested, generate_case
from boto3.session import Session

logger = utils.get_logger()


def lambda_handler(event: Dict[str, Any], context: Optional[Dict[str, Any]]) -> None:

    try:
        logger.info("Lambda_handler Event")
        logger.info(event)
        aft_session = Session()
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
