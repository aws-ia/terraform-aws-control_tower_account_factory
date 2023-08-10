# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
import logging
from typing import Dict, List, Sequence

from aft_common.aft_utils import (
    get_high_retry_botoconfig,
    resubmit_request_on_boto_throttle,
    yield_batches_from_list,
)
from aft_common.constants import SSM_PARAMETER_PATH
from boto3.session import Session

logger = logging.getLogger("aft")


@resubmit_request_on_boto_throttle
def put_ssm_parameters(session: Session, parameters: Dict[str, str]) -> None:

    client = session.client("ssm", config=get_high_retry_botoconfig())

    for key, value in parameters.items():
        response = client.put_parameter(
            Name=SSM_PARAMETER_PATH + key, Value=value, Type="String", Overwrite=True
        )


@resubmit_request_on_boto_throttle
def get_ssm_parameters_names_by_path(session: Session, path: str) -> List[str]:

    client = session.client("ssm", config=get_high_retry_botoconfig())
    paginator = client.get_paginator("get_parameters_by_path")
    pages = paginator.paginate(Path=path, Recursive=True)

    parameter_names = []
    for page in pages:
        parameter_names.extend([param["Name"] for param in page["Parameters"]])

    return parameter_names


@resubmit_request_on_boto_throttle
def delete_ssm_parameters(session: Session, parameters: Sequence[str]) -> None:
    batches = yield_batches_from_list(
        parameters, batch_size=10
    )  # Max batch size for API
    client = session.client("ssm", config=get_high_retry_botoconfig())
    for batched_names in batches:
        response = client.delete_parameters(Names=batched_names)


def get_ssm_parameter_value(session: Session, param: str, decrypt: bool = False) -> str:
    client = session.client("ssm")
    logger.info("Getting SSM Parameter " + param)

    response = client.get_parameter(Name=param, WithDecryption=decrypt)

    param_value: str = response["Parameter"]["Value"]
    return param_value
