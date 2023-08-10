# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
import logging
from typing import TYPE_CHECKING

from aft_common.constants import SSM_PARAM_SNS_FAILURE_TOPIC_ARN
from aft_common.ssm import get_ssm_parameter_value
from boto3.session import Session

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
    from mypy_boto3_sns import SNSClient
    from mypy_boto3_sns.type_defs import PublishResponseTypeDef
else:
    LambdaClient = object
    PublishResponseTypeDef = object
    SNSClient = object
    LambdaContext = object

logger = logging.getLogger("aft")


def send_sns_message(
    session: Session, topic: str, sns_message: str, subject: str
) -> PublishResponseTypeDef:
    logger.info("Sending SNS Message")
    client: SNSClient = session.client("sns")
    response = client.publish(TopicArn=topic, Message=sns_message, Subject=subject)
    logger.info(response)
    return response


def send_lambda_failure_sns_message(
    session: Session, message: str, subject: str, context: LambdaContext
) -> None:

    msg = f"""An error occurred in the '{context.function_name}' Lambda function.
For more information, search AWS Request ID '{context.aws_request_id}' in CloudWatch log group '{context.log_group_name}'
Error Message: {message}"""

    failure_sns_topic = get_ssm_parameter_value(
        session=session,
        param=SSM_PARAM_SNS_FAILURE_TOPIC_ARN,
    )
    send_sns_message(
        session=session,
        topic=failure_sns_topic,
        sns_message=msg,
        subject=subject,
    )
