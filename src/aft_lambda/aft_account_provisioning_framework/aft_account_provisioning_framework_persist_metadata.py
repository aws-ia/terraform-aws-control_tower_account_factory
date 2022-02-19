# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
from typing import Any, Dict, Union

import aft_common.aft_utils as utils
from aft_common.account_provisioning_framework import persist_metadata
from boto3.session import Session

logger = utils.get_logger()


def lambda_handler(
    event: Dict[str, Any], context: Union[Dict[str, Any], None]
) -> Dict[str, Any]:
    try:
        logger.info("AFT Account Provisioning Framework Handler Start")

        rollback = None

        try:
            if event["rollback"]:
                rollback = True
        except KeyError:
            pass

        payload = event["payload"]
        action = event["action"]

        session = Session()

        if action == "persist_metadata":
            account_info = payload["account_info"]["account"]
            update_metadata = persist_metadata(payload, account_info, session)
            return update_metadata
        else:
            raise Exception(
                "Incorrect Command Passed to Lambda Function. Input: {action}. Expected: 'persist_metadata'"
            )

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise
