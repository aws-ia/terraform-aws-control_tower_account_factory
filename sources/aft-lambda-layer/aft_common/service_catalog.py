# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
import logging
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    Iterator,
    List,
    Literal,
    Mapping,
    Sequence,
)

from aft_common import aft_utils as utils
from aft_common import ddb
from aft_common.account_provisioning_framework import ProvisionRoles
from aft_common.auth import AuthClient
from aft_common.constants import SSM_PARAM_SC_PRODUCT_NAME
from aft_common.ssm import get_ssm_parameter_value
from boto3.session import Session

if TYPE_CHECKING:
    from mypy_boto3_servicecatalog import ServiceCatalogClient
    from mypy_boto3_servicecatalog.type_defs import (
        ProvisionedProductAttributeTypeDef,
        SearchProvisionedProductsOutputTypeDef,
    )
else:
    ServiceCatalogClient = object
    SearchProvisionedProductsOutputTypeDef = object
    ProvisionedProductAttributeTypeDef = object

logger = logging.getLogger("aft")


def get_ct_product_id(session: Session, ct_management_session: Session) -> str:
    client: ServiceCatalogClient = ct_management_session.client("servicecatalog")
    sc_product_name = get_ssm_parameter_value(session, SSM_PARAM_SC_PRODUCT_NAME)
    logger.info("Getting product ID for " + sc_product_name)

    response = client.describe_product_as_admin(Name=sc_product_name)
    product_id: str = response["ProductViewDetail"]["ProductViewSummary"]["ProductId"]
    logger.info(product_id)
    return product_id


def ct_provisioning_artifact_is_active(
    session: Session, ct_management_session: Session, artifact_id: str
) -> bool:
    client: ServiceCatalogClient = ct_management_session.client(
        "servicecatalog", config=utils.get_high_retry_botoconfig()
    )
    sc_product_name = get_ssm_parameter_value(session, SSM_PARAM_SC_PRODUCT_NAME)
    logger.info("Checking provisioning artifact ID " + artifact_id)
    try:
        response = client.describe_provisioning_artifact(
            ProductName=sc_product_name, ProvisioningArtifactId=artifact_id
        )
        provisioning_artifact = response["ProvisioningArtifactDetail"]
    except client.exceptions.ResourceNotFoundException:
        logger.info("Provisioning artifact id: " + artifact_id + " does not exist")
        return False

    if provisioning_artifact["Active"]:
        logger.info(provisioning_artifact["Id"] + " is active")
        return True
    else:
        logger.info(provisioning_artifact["Id"] + " is NOT active")
        return False


def get_ct_provisioning_artifact_id(
    session: Session, ct_management_session: Session
) -> str:
    client: ServiceCatalogClient = ct_management_session.client("servicecatalog")
    sc_product_name = get_ssm_parameter_value(session, SSM_PARAM_SC_PRODUCT_NAME)
    logger.info("Getting provisioning artifact ID for " + sc_product_name)

    response = client.describe_product_as_admin(Name=sc_product_name)
    provisioning_artifacts = response["ProvisioningArtifactSummaries"]
    for pa in provisioning_artifacts:
        if ct_provisioning_artifact_is_active(session, ct_management_session, pa["Id"]):
            pa_id: str = pa["Id"]
            logger.info("Using provisioning artifact ID: " + pa_id)
            return pa_id

    raise Exception("No Provisioning Artifact ID found")


def get_healthy_ct_product_batch(
    ct_management_session: Session,
) -> Iterator[Iterable[ProvisionedProductAttributeTypeDef]]:
    sc_product_search_filter: Mapping[Literal["SearchQuery"], Sequence[str]] = {
        "SearchQuery": [
            "type:CONTROL_TOWER_ACCOUNT",
        ]
    }
    sc_client = ct_management_session.client(
        "servicecatalog", config=utils.get_high_retry_botoconfig()
    )
    logger.info(
        "Searching Account Factory for account with matching email in healthy status"
    )
    # Get products with the required type
    response: SearchProvisionedProductsOutputTypeDef = (
        sc_client.search_provisioned_products(
            Filters=sc_product_search_filter, PageSize=100
        )
    )
    provisioned_products = response["ProvisionedProducts"]
    healthy_products: Iterable[ProvisionedProductAttributeTypeDef] = filter(
        ct_account_product_is_healthy, provisioned_products
    )

    yield healthy_products

    while response.get("NextPageToken") is not None:
        response = sc_client.search_provisioned_products(
            Filters=sc_product_search_filter,
            PageSize=100,
            PageToken=response["NextPageToken"],
        )
        provisioned_products = response["ProvisionedProducts"]
        healthy_products = filter(ct_account_product_is_healthy, provisioned_products)

        yield healthy_products

    return


def email_exists_in_batch(
    target_email: str, pps: List[str], ct_management_session: Session
) -> bool:
    sc_client = ct_management_session.client(
        "servicecatalog", config=utils.get_high_retry_botoconfig()
    )
    for pp in pps:
        pp_email = sc_client.get_provisioned_product_outputs(
            ProvisionedProductId=pp, OutputKeys=["AccountEmail"]
        )["Outputs"][0]["OutputValue"]
        if utils.emails_are_equal(target_email, pp_email):
            logger.info("Account email match found; provisioned product exists.")
            return True
    return False


def provisioned_product_exists(record: Dict[str, Any]) -> bool:
    # Go get all my accounts from SC (Not all PPs)
    auth = AuthClient()
    ct_management_session = auth.get_ct_management_session(
        role_name=ProvisionRoles.SERVICE_ROLE_NAME
    )
    account_email = ddb.unmarshal_ddb_item(record["dynamodb"]["NewImage"])[
        "control_tower_parameters"
    ]["AccountEmail"]

    for batch in get_healthy_ct_product_batch(
        ct_management_session=ct_management_session
    ):
        pp_ids = [product["Id"] for product in batch]

        if email_exists_in_batch(account_email, pp_ids, ct_management_session):
            return True

    # We processed all batches of accounts with healthy statuses, and did not find a match
    # It is possible that the account exists, but does not have a healthy status
    logger.info(
        "Did not find account with matching email in healthy status in Account Factory"
    )

    return False


def ct_account_product_is_healthy(product: ProvisionedProductAttributeTypeDef) -> bool:
    aft_sc_product_allowed_status = ["AVAILABLE", "TAINTED"]
    # If LastSuccessfulProvisioningRecordId does not exist, the account was never successfully provisioned
    return product["Status"] in aft_sc_product_allowed_status and bool(
        product.get("LastSuccessfulProvisioningRecordId")
    )
