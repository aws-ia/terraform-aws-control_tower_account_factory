# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import logging
import random
import re
import time
from functools import wraps
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from boto3.session import Session
from botocore.config import Config
from botocore.exceptions import ClientError
from botocore.response import StreamingBody

if TYPE_CHECKING:
    from mypy_boto3_lambda import LambdaClient
    from mypy_boto3_lambda.type_defs import InvocationResponseTypeDef
    from mypy_boto3_stepfunctions import SFNClient
    from mypy_boto3_stepfunctions.type_defs import StartExecutionOutputTypeDef
    from mypy_boto3_sts import STSClient
else:
    LambdaClient = object
    InvocationResponseTypeDef = object
    OrganizationsClient = object
    ServiceCatalogClient = object
    SFNClient = object
    StartExecutionOutputTypeDef = object
    STSClient = object

logger = logging.getLogger("aft")

BOTO3_CLIENT_ERROR_THROTTLING_CODES = [
    "ThrottlingException",
    "TooManyRequestsException",
    "RequestLimitExceeded",
]


def resubmit_request_on_boto_throttle(
    func: Callable[..., Any],
    max_requests: int = 3,
    max_sleep_sec: int = 16,
) -> Callable[..., Any]:
    """
    Decorator to automatically resubmit boto3-based API calls on throttling errors.

    This decorator will re-submit up to max_requests INITIAL requests, NOT
    accounting for built-in boto3 retries. Each INITIAL request is independent
    of the previous requests. This may result in duplicate work being performed.
    As such, this decorator should ONLY be used with read calls or
    write calls that are idempotent.

    For example, using the default boto3 config of 3 retries (4 attempts) with
    max_requests = 3 will result in 12 total calls made to the AWS service.
    """

    @wraps(func)
    def wrapper(*args: Optional[Tuple[Any]], **kwargs: Optional[Dict[str, Any]]) -> Any:
        jitter = float(
            f"{random.random():.3f}"  # nosec B311: Not using random numbers in a security context
        )
        retry_sleep_sec = min(2 + jitter, max_sleep_sec)

        requests = 0
        while True:
            try:
                return func(*args, **kwargs)
            except ClientError as e:
                if e.response["Error"]["Code"] in BOTO3_CLIENT_ERROR_THROTTLING_CODES:
                    sanitized_max_requests = sanitize_input_for_logging(max_requests)
                    sanitized_retry_sleep_sec = sanitize_input_for_logging(
                        retry_sleep_sec
                    )
                    if requests >= max_requests:
                        logger.info(
                            f"Exceeded max fresh-request retry attempts ({sanitized_max_requests})"
                        )
                        raise e
                    logger.info(
                        f"Exceeded max boto3 retries on previous request. Retrying with fresh request in {sanitized_retry_sleep_sec} seconds."
                    )
                    requests += 1
                    time.sleep(retry_sleep_sec)

                    # Clipped exponential backoff with 0-1sec random jitter
                    retry_sleep_sec = retry_sleep_sec * 2 + jitter
                    retry_sleep_sec = min(retry_sleep_sec, max_sleep_sec)

                else:
                    raise e

            except Exception as e:
                # Raise on all other exceptions
                raise e

    return wrapper


def get_high_retry_botoconfig() -> Config:
    # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#using-the-config-object
    return Config(
        retries={
            "total_max_attempts": 16,  # original request + 15 retries
            "mode": "adaptive",  # "Retries with additional client side throttling"
        }
    )


def emails_are_equal(first_email: str, second_email: str) -> bool:
    return first_email.lower() == second_email.lower()


def invoke_lambda(
    session: Session,
    function_name: str,
    payload: Union[bytes, IO[bytes], StreamingBody],
) -> InvocationResponseTypeDef:
    client: LambdaClient = session.client("lambda")
    sanitized_function_name = sanitize_input_for_logging(function_name)
    logger.info(f"Invoking Lambda: {sanitized_function_name}")
    response = client.invoke(
        FunctionName=function_name,
        InvocationType="Event",
        LogType="Tail",
        Payload=payload,
    )
    sanitized_response = sanitize_input_for_logging(response)
    logger.info(sanitized_response)
    return response


def build_sfn_arn(session: Session, sfn_name: str) -> str:
    account_info = get_session_info(session)
    sfn_arn = (
        f"arn:{get_aws_partition(session)}:states:"
        + account_info["region"]
        + ":"
        + account_info["account"]
        + ":stateMachine:"
        + sfn_name
    )
    return sfn_arn


def invoke_step_function(
    session: Session, sfn_name: str, input: str
) -> StartExecutionOutputTypeDef:
    client: SFNClient = session.client("stepfunctions")
    sfn_arn = build_sfn_arn(session, sfn_name)
    sanitized_sfn_arn = sanitize_input_for_logging(sfn_arn)
    logger.info("Starting SFN execution of " + sanitized_sfn_arn)
    response = client.start_execution(stateMachineArn=sfn_arn, input=input)
    logger.debug(sanitize_input_for_logging(response))
    return response


def is_aft_supported_controltower_event(event: Dict[str, Any]) -> bool:
    if event.get("source", None) == "aws.controltower":
        supported_events = ["CreateManagedAccount", "UpdateManagedAccount"]
        if event.get("detail", {}).get("eventName", None) in supported_events:
            logger.info("Received AFT supported Control Tower Event")
            return True

    return False


def get_session_info(session: Session) -> Dict[str, str]:
    client: STSClient = session.client("sts")
    response = client.get_caller_identity()

    account_info = {"region": session.region_name, "account": response["Account"]}

    return account_info


def get_aws_partition(session: Session, region: Optional[str] = None) -> str:
    if region is None:
        region = session.region_name

    partition = session.get_partition_for_region(region)
    return partition


def yield_batches_from_list(
    input: Sequence[Any], batch_size: int
) -> Iterable[Sequence[Any]]:
    if batch_size <= 0:
        return []

    idx = 0
    while idx < len(input):
        yield input[idx : idx + batch_size]
        idx += batch_size


def sanitize_input_for_logging(input: Any) -> str:
    """
    Sanitize the input string by replacing newline characters, tabs with their literal string representations.
    """
    input_str = str(input)
    return input_str.encode("unicode_escape").decode()
