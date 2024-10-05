# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
import logging
from typing import TYPE_CHECKING, Any, Dict

from aft_common import codepipeline, ddb
from aft_common.aft_utils import sanitize_input_for_logging
from aft_common.auth import AuthClient
from aft_common.constants import (
    SSM_PARAM_ACCOUNT_AFT_MANAGEMENT_ACCOUNT_ID,
    SSM_PARAM_AFT_DDB_META_TABLE,
)
from aft_common.logger import configure_aft_logger
from aft_common.notifications import send_lambda_failure_sns_message
from aft_common.organizations import OrganizationsAgent
from aft_common.ssm import get_ssm_parameter_value
from boto3.session import Session

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object


configure_aft_logger()
logger = logging.getLogger("aft")


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> None:
    try:
        auth = AuthClient()
        aft_management_session = auth.get_aft_management_session()

        account_request = event["account_request"]
        account_email = account_request[
            "id"
        ]  # the account email is stored in "id" field

        logger.info(f"Beginnning resource cleanup for {account_email}")

        orgs_agent = OrganizationsAgent(
            ct_management_session=auth.get_ct_management_session()
        )

        # Can NOT use known-OU optimization here as request OU may be different
        # from existing OU
        account_id = orgs_agent.get_account_id_from_email(email=account_email)

        logger.info(f"Deleting account customization pipeline for {account_id}")
        codepipeline.delete_customization_pipeline(
            aft_management_session=aft_management_session, account_id=account_id
        )
        logger.info(f"Customization pipeline deleted")

        aft_request_metadata_table_name = get_ssm_parameter_value(
            aft_management_session,
            SSM_PARAM_AFT_DDB_META_TABLE,
        )

        logger.info(f"Deleting account metadata record for {account_id}")
        ddb.delete_ddb_item(
            session=aft_management_session,
            table_name=aft_request_metadata_table_name,
            primary_key={"id": account_id},
        )
        logger.info(f"Account metadata record deleted")

        aft_management_account_id = get_ssm_parameter_value(
            aft_management_session,
            SSM_PARAM_ACCOUNT_AFT_MANAGEMENT_ACCOUNT_ID,
        )

        logger.info(f"Deleting Terraform state files for {account_id}")
        s3_delete_objects(
            session=aft_management_session,
            aft_management_account_id=aft_management_account_id,
            account_id=account_id,
        )
        logger.info(f"Terraform state files deleted")

        logger.info(f"Cleanup for {account_id} complete ")

    except Exception as error:
        send_lambda_failure_sns_message(
            session=aft_management_session,
            message=str(error),
            context=context,
            subject="AFT account request failed",
        )
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(error),
        }
        logger.exception(message)
        raise


def s3_delete_objects(session: Session, aft_management_account_id: str, account_id: str) -> None:
    s3 = session.client("s3")

    dirs_to_remove = [
        (f"aft-backend-{aft_management_account_id}-primary-region", f"{account_id}-aft-account-customizations"),
        (f"aft-backend-{aft_management_account_id}-primary-region", f"{account_id}-aft-global-customizations"),
        (f"aft-backend-{aft_management_account_id}-primary-region", f"{account_id}-customizations-pipeline"),
        (f"aft-backend-{aft_management_account_id}-secondary-region", f"{account_id}-aft-account-customizations"),
        (f"aft-backend-{aft_management_account_id}-secondary-region", f"{account_id}-aft-global-customizations"),
        (f"aft-backend-{aft_management_account_id}-secondary-region", f"{account_id}-customizations-pipeline"),
        (f"aft-customizations-pipeline-{aft_management_account_id}", f"{account_id}-customi"),
    ]

    for bucket, dir in dirs_to_remove:
        logger.info(f"Deleting {bucket} {dir} (recursively)")
        list_objs_response = s3.list_objects_v2(Bucket=bucket, Prefix=dir)
        delete_objs_request_keys = [{"Key": obj["Key"]} for obj in list_objs_response["Contents"]]
        if len(delete_objs_request_keys) > 0:
            delete_objs_response = s3.delete_objects(Bucket=bucket, Delete={"Objects": delete_objs_request_keys})
            sanitized_response = sanitize_input_for_logging(delete_objs_response)
            logger.info(sanitized_response)
