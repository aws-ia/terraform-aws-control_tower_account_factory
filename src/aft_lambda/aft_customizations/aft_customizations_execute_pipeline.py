# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
from typing import Any, Dict, Union

import aft_common.aft_utils as utils
from aft_common.customizations import execute_pipeline
from boto3.session import Session

logger = utils.get_logger()


def lambda_handler(
    event: Dict[str, Any], context: Union[Dict[str, Any], None]
) -> Dict[str, Any]:

    logger.info("Lambda_handler Event")
    logger.info(event)

    try:
        logger.info("Lambda_handler Event")
        logger.info(event)
        session = Session()
        maximum_concurrent_pipelines = int(
            utils.get_ssm_parameter_value(
                session, utils.SSM_PARAM_AFT_MAXIMUM_CONCURRENT_CUSTOMIZATIONS
            )
        )

        running_pipelines = int(event["running_executions"]["running_pipelines"])
        pipelines_to_run = maximum_concurrent_pipelines - running_pipelines
        accounts = event["targets"]["pending_accounts"]
        logger.info("Accounts submitted for execution: " + str(len(accounts)))
        for p in accounts[:pipelines_to_run]:
            execute_pipeline(session, str(p))
            accounts.remove(p)
        logger.info("Accounts remaining to be executed - ")
        logger.info(accounts)
        return {"number_pending_accounts": len(accounts), "pending_accounts": accounts}

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise
