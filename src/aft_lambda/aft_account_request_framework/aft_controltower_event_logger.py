# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
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
