# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from typing import TYPE_CHECKING, Optional

from aft_common.aft_utils import get_logger
from boto3.session import Session

if TYPE_CHECKING:
    from mypy_boto3_servicecatalog import ServiceCatalogClient
    from mypy_boto3_servicecatalog.type_defs import (
        DescribeProvisionedProductOutputTypeDef,
        ProvisionedProductDetailTypeDef,
    )
else:
    ServiceCatalogClient = object
    DescribeProvisionedProductOutputTypeDef = object
    ProvisionedProductDetailTypeDef = object

logger = get_logger()


class Account:
    def __init__(self, ct_management_session: Session, account_name: str) -> None:
        self.ct_management_session = ct_management_session
        self.account_name = account_name

    @property
    def provisioned_product(self) -> Optional[ProvisionedProductDetailTypeDef]:
        client: ServiceCatalogClient = self.ct_management_session.client(
            "servicecatalog"
        )
        try:
            response: DescribeProvisionedProductOutputTypeDef = (
                client.describe_provisioned_product(Name=self.account_name)
            )
            return response["ProvisionedProductDetail"]
        except client.exceptions.ResourceNotFoundException:
            logger.debug(f"Account with name {self.account_name} does not exists")
            return None
