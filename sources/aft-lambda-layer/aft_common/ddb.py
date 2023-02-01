# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
from typing import TYPE_CHECKING, Any, Dict, Optional

from aft_common import aft_utils as utils
from boto3.dynamodb.types import TypeDeserializer
from boto3.session import Session

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.type_defs import (
        AttributeValueTypeDef,
        DeleteItemOutputTableTypeDef,
        GetItemOutputTableTypeDef,
        PutItemOutputTableTypeDef,
    )
else:
    AttributeValueTypeDef = object
    GetItemOutputTableTypeDef = object
    PutItemOutputTableTypeDef = object
    DeleteItemOutputTableTypeDef = object

logger = utils.get_logger()


def get_ddb_item(
    session: Session, table_name: str, primary_key: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    dynamodb = session.resource("dynamodb")
    table = dynamodb.Table(table_name)

    logger.info(f"Getting item with key: {primary_key} from table: {table_name}")
    response = table.get_item(Key=primary_key)
    return response.get("Item", None)


def put_ddb_item(
    session: Session, table_name: str, item: Dict[str, str]
) -> PutItemOutputTableTypeDef:
    dynamodb = session.resource("dynamodb")
    table = dynamodb.Table(table_name)

    logger.info(f"Inserting item into {table_name} table: {str(item)}")
    response = table.put_item(Item=item)
    logger.info(response)
    return response


def delete_ddb_item(
    session: Session, table_name: str, primary_key: Dict[str, Any]
) -> DeleteItemOutputTableTypeDef:
    dynamodb = session.resource("dynamodb")
    table = dynamodb.Table(table_name)

    logger.info(f"Deleting item with key: {primary_key} from: {table_name} table")
    response = table.delete_item(Key=primary_key)
    logger.info(response)
    return response


def unmarshal_ddb_item(
    low_level_data: Dict[str, AttributeValueTypeDef]
) -> Dict[str, Any]:
    # To go from low-level format to python

    deserializer = TypeDeserializer()
    python_data = {k: deserializer.deserialize(v) for k, v in low_level_data.items()}
    return python_data
