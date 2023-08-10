# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from typing import Any, Dict, Literal, TypedDict


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


class AftInvokeAccountCustomizationPayload(TypedDict):
    account_info: Dict[Literal["account"], AftAccountInfo]
    account_request: Dict[str, Any]
    control_tower_event: Dict[str, Any]
    account_provisioning: Dict[str, Any]
    customization_request_id: str
