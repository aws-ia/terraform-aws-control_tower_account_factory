# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
import json
from typing import TYPE_CHECKING, Any, Dict

from aft_common import aft_utils as utils
from aft_common import notifications
from aft_common.customizations import (
    build_invoke_event,
    get_account_metadata_record,
    get_account_request_record,
    invoke_account_provisioning_sfn,
)
from boto3.session import Session

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object

logger = utils.get_logger()


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> None:
    session = Session()
    try:
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

    except Exception as error:
        notifications.send_lambda_failure_sns_message(
            session=session,
            message=str(error),
            context=context,
            subject="Failed to invoke account provisioning framework",
        )
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(error),
        }
        logger.exception(message)
        raise
