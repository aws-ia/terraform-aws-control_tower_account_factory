# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
from typing import Any, Dict, Union

import aft_common.aft_utils as utils
from aft_common.customizations import (
    build_invoke_event,
    get_account_metadata_record,
    get_account_request_record,
    invoke_account_provisioning_sfn,
)
from boto3.session import Session

logger = utils.get_logger()


def lambda_handler(event: Dict[str, Any], context: Union[Dict[str, Any], None]) -> None:
    try:
        logger.info("Lambda_handler Event")
        logger.info(event)
        session = Session()

        pending_account_ids = event["targets"]["pending_accounts"]
        account_metadata_table = utils.get_ssm_parameter_value(
            session, utils.SSM_PARAM_AFT_DDB_META_TABLE
        )
        account_request_table = utils.get_ssm_parameter_value(
            session, utils.SSM_PARAM_AFT_DDB_REQ_TABLE
        )
        provisioning_framework_sfn = utils.get_ssm_parameter_value(
            session, utils.SSM_PARAM_AFT_SFN_NAME
        )

        for a in pending_account_ids:
            account_metadata_record = get_account_metadata_record(
                session, account_metadata_table, a
            )
            account_request_email = account_metadata_record["email"]
            account_request_record = get_account_request_record(
                session, account_request_table, account_request_email
            )
            sfn_event = build_invoke_event(account_request_record)
            invoke_account_provisioning_sfn(
                session, provisioning_framework_sfn, sfn_event
            )

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise
