# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
from typing import Any, Dict, Union

import aft_common.aft_utils as utils
from aft_common.account_provisioning_framework import get_account_info
from aft_common.types import AftAccountInfo
from boto3.session import Session

logger = utils.get_logger()


def lambda_handler(
    event: Dict[str, Any], context: Union[Dict[str, Any], None]
) -> AftAccountInfo:
    try:
        logger.info("AFT Account Provisioning Framework Get Account Info Handler Start")

        payload = event["payload"]
        action = event["action"]

        session = Session()
        ct_management_session = utils.get_ct_management_session(session)
        if action == "get_account_info":
            return get_account_info(payload, session, ct_management_session)
        else:
            raise Exception(
                "Incorrect Command Passed to Lambda Function. Input: {action}. Expected: 'get_account_info'"
            )

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise
