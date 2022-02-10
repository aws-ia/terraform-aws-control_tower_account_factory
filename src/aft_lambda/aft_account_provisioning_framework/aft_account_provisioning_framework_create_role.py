# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
from typing import Any, Dict, Union

import aft_common.aft_utils as utils
import boto3
from aft_common.account_provisioning_framework import create_aft_execution_role

logger = utils.get_logger()


def lambda_handler(event: Dict[str, Any], context: Union[Dict[str, Any], None]) -> str:
    try:
        logger.info("AFT Account Provisioning Framework Create Role Handler Start")

        payload = event["payload"]
        action = event["action"]

        session = boto3.session.Session()
        ct_management_session = utils.get_ct_management_session(session)

        if action == "create_role":
            account_info = payload["account_info"]["account"]
            aft_role = create_aft_execution_role(
                account_info, session, ct_management_session
            )
            return_value: str = aft_role
            return return_value
        else:
            raise Exception(
                "Incorrect Command Passed to Lambda Function. Input: {action}. Expected: 'create_role'"
            )

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise
