# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
import json
import uuid
from typing import TYPE_CHECKING, Any, Dict, Optional

from aft_common import aft_utils as utils
from boto3.session import Session

if TYPE_CHECKING:
    from mypy_boto3_sqs import SQSClient
    from mypy_boto3_sqs.type_defs import MessageTypeDef, SendMessageResultTypeDef
else:
    SQSClient = object
    MessageTypeDef = object
    SendMessageResultTypeDef = object

logger = utils.get_logger()


def build_sqs_url(session: Session, queue_name: str) -> str:
    account_info = utils.get_session_info(session)
    return f'https://sqs.{account_info["region"]}.amazonaws.com/{account_info["account"]}/{queue_name}'


def receive_sqs_message(session: Session, sqs_queue: str) -> Optional[MessageTypeDef]:
    client: SQSClient = session.client("sqs")
    sqs_url = build_sqs_url(session, sqs_queue)
    logger.info(f"Fetching SQS Messages from {sqs_url}")

    response = client.receive_message(
        QueueUrl=sqs_url,
        MaxNumberOfMessages=1,
        ReceiveRequestAttemptId=str(uuid.uuid1()),
    )
    if "Messages" in response.keys():
        logger.info("There are messages pending processing")
        message = response["Messages"][0]
        logger.info("Message retrieved")
        logger.info(message)
        return message
    else:
        logger.info("There are no messages pending processing")
        return None


def delete_sqs_message(session: Session, message: MessageTypeDef) -> None:
    client: SQSClient = session.client("sqs")
    sqs_queue = utils.get_ssm_parameter_value(
        session, utils.SSM_PARAM_ACCOUNT_REQUEST_QUEUE
    )
    receipt_handle = message["ReceiptHandle"]
    logger.info("Deleting SQS message with handle " + receipt_handle)
    client.delete_message(
        QueueUrl=build_sqs_url(session, sqs_queue), ReceiptHandle=receipt_handle
    )


def send_sqs_message(
    session: Session, sqs_url: str, message: Dict[str, Any]
) -> SendMessageResultTypeDef:
    sqs: SQSClient = session.client("sqs")
    logger.info("Sending SQS message to " + sqs_url)
    logger.info(message)

    unique_id = str(uuid.uuid1())

    response = sqs.send_message(
        QueueUrl=sqs_url,
        MessageBody=json.dumps(message),
        MessageDeduplicationId=unique_id,
        MessageGroupId=unique_id,
    )

    logger.info(response)

    return response
