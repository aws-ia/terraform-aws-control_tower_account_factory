# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from typing import Literal, TypedDict


class AftAccountInfo(TypedDict):
    id: str
    email: str
    name: str
    joined_method: str
    joined_date: str
    status: str
    parent_id: str
    parent_type: str
    type: Literal["account"]
    vendor: Literal["aws"]
