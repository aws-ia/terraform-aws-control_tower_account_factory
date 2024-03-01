# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import json
import logging
import uuid
from datetime import datetime
from functools import cached_property, partial
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, cast

import aft_common.constants
import aft_common.service_catalog
import aft_common.ssm
from aft_common import aft_utils as utils
from aft_common import ddb, sqs
from aft_common.account_provisioning_framework import ProvisionRoles
from aft_common.aft_types import AftInvokeAccountCustomizationPayload
from aft_common.auth import AuthClient
from aft_common.exceptions import (
    NoAccountFactoryPortfolioFound,
    ServiceRoleNotAssociated,
)
from aft_common.organizations import OrganizationsAgent
from boto3.session import Session

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.type_defs import PutItemOutputTypeDef
    from mypy_boto3_servicecatalog import ServiceCatalogClient
    from mypy_boto3_servicecatalog.type_defs import (
        ProvisionedProductAttributeTypeDef,
        ProvisionedProductDetailTypeDef,
        ProvisioningParameterTypeDef,
        ProvisionProductOutputTypeDef,
        UpdateProvisioningParameterTypeDef,
    )
else:
    SearchProvisionedProductsOutputTypeDef = object
    PutItemOutputTypeDef = object
    ProvisioningParameterTypeDef = object
    ProvisionedProductDetailTypeDef = object
    ProvisionProductOutputTypeDef = object
    UpdateProvisioningParameterTypeDef = object
    ProvisionedProductAttributeTypeDef = object
    ServiceCatalogClient = object


logger = logging.getLogger("aft")


def insert_msg_into_acc_req_queue(
    event_record: Dict[Any, Any], new_account: bool, session: Session
) -> None:
    sqs_queue = aft_common.ssm.get_ssm_parameter_value(
        session, aft_common.constants.SSM_PARAM_ACCOUNT_REQUEST_QUEUE
    )
    sqs_queue = sqs.build_sqs_url(session=session, queue_name=sqs_queue)
    message = build_sqs_message(record=event_record, new_account=new_account)
    sqs.send_sqs_message(session=session, sqs_url=sqs_queue, message=message)


def control_tower_param_changed(record: Dict[str, Any]) -> bool:
    if record["eventName"] == "MODIFY":
        old_image = ddb.unmarshal_ddb_item(record["dynamodb"]["OldImage"])[
            "control_tower_parameters"
        ]
        new_image = ddb.unmarshal_ddb_item(record["dynamodb"]["NewImage"])[
            "control_tower_parameters"
        ]

        if old_image != new_image:
            return True
    return False


def build_sqs_message(record: Dict[str, Any], new_account: bool) -> Dict[str, Any]:
    logger.info("Building SQS Message - ")
    message = {}
    operation = "ADD" if new_account else "UPDATE"

    new_image = ddb.unmarshal_ddb_item(record["dynamodb"]["NewImage"])
    message["operation"] = operation
    message["control_tower_parameters"] = new_image["control_tower_parameters"]

    if record["eventName"] == "MODIFY":
        old_image = ddb.unmarshal_ddb_item(record["dynamodb"]["OldImage"])
        message["old_control_tower_parameters"] = old_image["control_tower_parameters"]

    logger.info(message)
    return message


def build_aft_account_provisioning_framework_event(
    record: Dict[str, Any]
) -> Dict[str, Any]:
    account_request = ddb.unmarshal_ddb_item(record["dynamodb"]["NewImage"])
    aft_account_provisioning_framework_event = {
        "account_request": account_request,
        "control_tower_event": {},
    }
    logger.info(aft_account_provisioning_framework_event)
    return aft_account_provisioning_framework_event


def put_audit_record(
    session: Session, table: str, image: Dict[str, Any], event_name: str
) -> PutItemOutputTypeDef:
    dynamodb = session.client("dynamodb")
    item = image
    datetime_format = "%Y-%m-%dT%H:%M:%S.%f"
    current_time = datetime.now().strftime(datetime_format)
    item["timestamp"] = {"S": current_time}
    item["ddb_event_name"] = {"S": event_name}
    logger.info("Inserting item into " + table + " table: " + str(item))
    response = dynamodb.put_item(TableName=table, Item=item)
    logger.info(response)
    return response


def account_name_or_email_in_use(
    ct_management_session: Session, account_name: str, account_email: str
) -> bool:
    orgs = ct_management_session.client(
        "organizations", config=utils.get_high_retry_botoconfig()
    )
    paginator = orgs.get_paginator("list_accounts")
    for page in paginator.paginate():
        for account in page["Accounts"]:
            if account_name == account["Name"]:
                logger.error(
                    f"Account Name: {account_name} already used in Organizations"
                )
                return True
            if utils.emails_are_equal(account_email, account["Email"]):
                logger.error(
                    f"Account Email: {account_email} already used in Organizations"
                )
                return True

    return False


def new_ct_request_is_valid(session: Session, request: Dict[str, Any]) -> bool:
    ct_parameters = request["control_tower_parameters"]
    return not account_name_or_email_in_use(
        ct_management_session=session,
        account_name=ct_parameters["AccountName"],
        account_email=ct_parameters["AccountEmail"],
    )


def modify_ct_request_is_valid(request: Dict[str, Any]) -> bool:

    old_ct_parameters = request.get("old_control_tower_parameters", {})
    new_ct_parameters = request["control_tower_parameters"]

    for i in old_ct_parameters.keys():
        if i != "ManagedOrganizationalUnit":
            if old_ct_parameters[i] != new_ct_parameters[i]:
                logger.error(f"Control Tower parameter {i} cannot be modified")
                return False
    return True


def add_header(request: Any, **kwargs: Any) -> None:
    request.headers.add_header(
        "User-Agent", "account-factory-terraform-" + kwargs["version"]
    )


def create_provisioned_product_name(account_name: str) -> str:
    """
    Replaces all space characters in an Account Name with hyphens,
    also removes all trailing and leading whitespace
    """
    return account_name.strip().replace(" ", "-")


def create_new_account(
    session: Session, ct_management_session: Session, request: Dict[str, Any]
) -> ProvisionProductOutputTypeDef:
    client = ct_management_session.client("servicecatalog")
    event_system = client.meta.events

    aft_version = aft_common.ssm.get_ssm_parameter_value(
        session, aft_common.constants.SSM_PARAM_ACCOUNT_AFT_VERSION
    )
    header_with_aft_version = partial(add_header, version=aft_version)
    event_system.register_first("before-sign.*.*", header_with_aft_version)

    provisioning_parameters = []

    for k, v in request["control_tower_parameters"].items():
        provisioning_parameters.append({"Key": k, "Value": v})

    logger.info(
        "Creating new account leveraging parameters: " + str(provisioning_parameters)
    )
    provisioned_product_name = create_provisioned_product_name(
        account_name=request["control_tower_parameters"]["AccountName"]
    )
    response = client.provision_product(
        ProductId=aft_common.service_catalog.get_ct_product_id(
            session, ct_management_session
        ),
        ProvisioningArtifactId=aft_common.service_catalog.get_ct_provisioning_artifact_id(
            session, ct_management_session
        ),
        ProvisionedProductName=provisioned_product_name,
        ProvisioningParameters=cast(
            Sequence[ProvisioningParameterTypeDef], provisioning_parameters
        ),
        ProvisionToken=str(uuid.uuid1()),
    )
    logger.info(response)
    return response


def update_existing_account(
    session: Session, ct_management_session: Session, request: Dict[str, Any]
) -> None:
    client = ct_management_session.client("servicecatalog")
    event_system = client.meta.events

    aft_version = aft_common.ssm.get_ssm_parameter_value(
        session, aft_common.constants.SSM_PARAM_ACCOUNT_AFT_VERSION
    )
    header_with_aft_version = partial(add_header, version=aft_version)
    event_system.register_first("before-sign.*.*", header_with_aft_version)

    provisioning_parameters: List[UpdateProvisioningParameterTypeDef] = []
    for k, v in request["control_tower_parameters"].items():
        provisioning_parameters.append({"Key": k, "Value": v})

    control_tower_email_parameter = request["control_tower_parameters"]["AccountEmail"]
    target_product: Optional[ProvisionedProductAttributeTypeDef] = None
    for batch in aft_common.service_catalog.get_healthy_ct_product_batch(
        ct_management_session=ct_management_session
    ):
        for product in batch:
            product_outputs_response = client.get_provisioned_product_outputs(
                ProvisionedProductId=product["Id"],
                OutputKeys=[
                    "AccountEmail",
                ],
            )
            provisioned_product_email = product_outputs_response["Outputs"][0][
                "OutputValue"
            ]

            if utils.emails_are_equal(
                provisioned_product_email, control_tower_email_parameter
            ):
                target_product = product
                break

    if target_product is None:
        raise Exception(
            f"No healthy provisioned product found for {control_tower_email_parameter}"
        )

    # check to see if the product still exists and is still active
    if aft_common.service_catalog.ct_provisioning_artifact_is_active(
        session=session,
        ct_management_session=ct_management_session,
        artifact_id=target_product["ProvisioningArtifactId"],
    ):
        target_provisioning_artifact_id = target_product["ProvisioningArtifactId"]
    else:
        target_provisioning_artifact_id = (
            aft_common.service_catalog.get_ct_provisioning_artifact_id(
                session, ct_management_session
            )
        )

    logger.info(
        "Modifying existing account leveraging parameters: "
        + str(provisioning_parameters)
        + " with provisioned product ID "
        + target_product["Id"]
    )
    update_response = client.update_provisioned_product(
        ProvisionedProductId=target_product["Id"],
        ProductId=aft_common.service_catalog.get_ct_product_id(
            session, ct_management_session
        ),
        ProvisioningArtifactId=target_provisioning_artifact_id,
        ProvisioningParameters=provisioning_parameters,
        UpdateToken=str(uuid.uuid1()),
    )
    logger.info(update_response)


def get_account_request_record(
    aft_management_session: Session, request_table_id: str
) -> Dict[str, Any]:
    table_name = aft_common.ssm.get_ssm_parameter_value(
        aft_management_session, aft_common.constants.SSM_PARAM_AFT_DDB_REQ_TABLE
    )
    logger.info(
        "Getting record for id " + request_table_id + " in DDB table " + table_name
    )
    item = ddb.get_ddb_item(
        session=aft_management_session,
        table_name=table_name,
        primary_key={"id": request_table_id},
    )
    if item:
        logger.info("Record found")
        logger.info(item)
        return item
    else:
        raise Exception(f"Account {request_table_id}  not found in {table_name}")


def build_account_customization_payload(
    ct_management_session: Session,
    account_id: str,
    account_request: Dict[str, Any],
    control_tower_event: Optional[Dict[str, Any]],
) -> AftInvokeAccountCustomizationPayload:

    orgs_agent = OrganizationsAgent(ct_management_session)

    # convert ddb strings into proper data type
    account_request["account_tags"] = json.loads(account_request["account_tags"])
    account_info = orgs_agent.get_aft_account_info(account_id=account_id)

    if control_tower_event is None:
        control_tower_event = {}

    account_customization_payload: AftInvokeAccountCustomizationPayload = {
        "account_info": {"account": account_info},
        # Unused by AFT but kept for aft-account-provisioning-customizations backwards compatibility
        "control_tower_event": control_tower_event,
        "account_request": account_request,
        "account_provisioning": {"run_create_pipeline": "true"},
        "customization_request_id": str(uuid.uuid4()),
    }

    return account_customization_payload


class AccountRequest:
    ACCOUNT_FACTORY_PORTFOLIO_NAME = "AWS Control Tower Account Factory Portfolio"

    def __init__(self, auth: AuthClient) -> None:
        self.ct_management_session = auth.get_ct_management_session(
            role_name=ProvisionRoles.SERVICE_ROLE_NAME
        )
        self.ct_management_account_id = auth.get_account_id_from_session(
            session=self.ct_management_session
        )
        self.aft_management_session = auth.get_aft_management_session()
        self.account_factory_product_id = aft_common.service_catalog.get_ct_product_id(
            session=self.aft_management_session,
            ct_management_session=self.ct_management_session,
        )

        self.partition = utils.get_aws_partition(self.ct_management_session)

    @property
    def service_role_arn(self) -> str:
        return f"arn:{self.partition}:iam::{self.ct_management_account_id}:role/{ProvisionRoles.SERVICE_ROLE_NAME}"

    @cached_property
    def account_factory_portfolio_id(self) -> str:
        """
        Paginates through all portfolios and returns the ID of the CT Account Factory Portfolio
        if it exists, raises exception if not found
        """
        client: ServiceCatalogClient = self.ct_management_session.client(
            "servicecatalog", config=utils.get_high_retry_botoconfig()
        )
        paginator = client.get_paginator("list_portfolios")
        for response in paginator.paginate():
            for portfolio in response["PortfolioDetails"]:
                if (
                    portfolio["DisplayName"]
                    == AccountRequest.ACCOUNT_FACTORY_PORTFOLIO_NAME
                ):
                    return portfolio["Id"]

        raise NoAccountFactoryPortfolioFound(
            f"No Portfolio ID found for {AccountRequest.ACCOUNT_FACTORY_PORTFOLIO_NAME}"
        )

    def associate_aft_service_role_with_account_factory(self) -> None:
        """
        Associates the AWSAFTService role with the Control Tower Account Factory Service Catalog portfolio
        """
        client = self.ct_management_session.client("servicecatalog")
        aft_service_role_arn = f"arn:{self.partition}:iam::{self.ct_management_account_id}:role/{ProvisionRoles.SERVICE_ROLE_NAME}"
        client.associate_principal_with_portfolio(
            PortfolioId=self.account_factory_portfolio_id,
            PrincipalARN=aft_service_role_arn,
            PrincipalType="IAM",
        )

    def validate_service_role_associated_with_account_factory(self) -> None:
        if not self.service_role_associated_with_account_factory():
            raise ServiceRoleNotAssociated(
                f"{ProvisionRoles.SERVICE_ROLE_NAME} Role not associated with portfolio {self.account_factory_portfolio_id}"
            )

    def service_role_associated_with_account_factory(self) -> bool:
        client = self.ct_management_session.client(
            "servicecatalog", config=utils.get_high_retry_botoconfig()
        )
        paginator = client.get_paginator("list_principals_for_portfolio")
        for response in paginator.paginate(
            PortfolioId=self.account_factory_portfolio_id
        ):
            if self.service_role_arn in [
                principal["PrincipalARN"] for principal in response["Principals"]
            ]:
                return True
        return False

    def provisioning_threshold_reached(self, threshold: int) -> bool:
        client: ServiceCatalogClient = self.ct_management_session.client(
            "servicecatalog", config=utils.get_high_retry_botoconfig()
        )
        logger.info("Checking for account provisioning in progress")

        response = client.scan_provisioned_products(
            AccessLevelFilter={"Key": "Account", "Value": "self"},
        )
        pps = response["ProvisionedProducts"]
        while "NextPageToken" in response:
            response = client.scan_provisioned_products(
                AccessLevelFilter={"Key": "Account", "Value": "self"},
                PageToken=response["NextPageToken"],
            )
            pps.extend(response["ProvisionedProducts"])

        return self.products_in_progress_at_threshold(
            threshold=threshold, provisioned_products=pps
        )

    def products_in_progress_at_threshold(
        self,
        threshold: int,
        provisioned_products: List[ProvisionedProductDetailTypeDef],
    ) -> bool:
        in_progress_count = 0

        for product in provisioned_products:
            if product["ProductId"] != self.account_factory_product_id:
                continue
            logger.info("Identified CT Product - " + product["Id"])
            if product["Status"] in ["UNDER_CHANGE", "PLAN_IN_PROGRESS"]:
                in_progress_count += 1

        return in_progress_count >= threshold
