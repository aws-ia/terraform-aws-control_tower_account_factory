# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import json
import sys
import uuid
from datetime import datetime
from functools import partial
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterator,
    List,
    Literal,
    Mapping,
    Optional,
    Sequence,
    cast,
)

from aft_common import aft_utils as utils
from boto3.session import Session

if TYPE_CHECKING:
    from mypy_boto3_servicecatalog.type_defs import (
        ProvisionedProductAttributeTypeDef,
        ProvisioningParameterTypeDef,
        ProvisionProductOutputTypeDef,
        SearchProvisionedProductsOutputTypeDef,
        UpdateProvisioningParameterTypeDef,
    )
else:
    ProvisioningParameterTypeDef = object
    ProvisionedProductDetailTypeDef = object
    ProvisionProductOutputTypeDef = object
    UpdateProvisioningParameterTypeDef = object
    ProvisionedProductAttributeTypeDef = object


logger = utils.get_logger()


def get_healthy_ct_product_batch(
    ct_management_session: Session,
) -> Iterator[List[ProvisionedProductAttributeTypeDef]]:
    sc_product_search_filter: Mapping[Literal["SearchQuery"], Sequence[str]] = {
        "SearchQuery": [
            "type:CONTROL_TOWER_ACCOUNT",
        ]
    }
    sc_client = ct_management_session.client("servicecatalog")
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
    sc_product_allowed_status = ["AVAILABLE", "TAINTED"]
    healthy_products = [
        product
        for product in provisioned_products
        if product["Status"] in sc_product_allowed_status
    ]
    yield healthy_products

    while response.get("NextPageToken") is not None:
        response = sc_client.search_provisioned_products(
            Filters=sc_product_search_filter,
            PageSize=100,
            PageToken=response["NextPageToken"],
        )

        healthy_products = [
            product
            for product in provisioned_products
            if product["Status"] in sc_product_allowed_status
        ]
        yield healthy_products


def provisioned_product_exists(record: Dict[str, Any]) -> bool:
    # Go get all my accounts from SC (Not all PPs)
    ct_management_session = utils.get_ct_management_session(aft_mgmt_session=Session())
    account_email = utils.unmarshal_ddb_item(record["dynamodb"]["NewImage"])[
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


def email_exists_in_batch(
    target_email: str, pps: List[str], ct_management_session: Session
) -> bool:
    sc_client = ct_management_session.client("servicecatalog")
    for pp in pps:
        pp_email = sc_client.get_provisioned_product_outputs(
            ProvisionedProductId=pp, OutputKeys=["AccountEmail"]
        )["Outputs"][0]["OutputValue"]
        if target_email.lower() == pp_email.lower():
            logger.info("Account email match found; provisioned product exists.")
            return True
    return False


def insert_msg_into_acc_req_queue(
    event_record: Dict[Any, Any], new_account: bool, session: Session
) -> None:
    sqs_queue = utils.get_ssm_parameter_value(
        session, utils.SSM_PARAM_ACCOUNT_REQUEST_QUEUE
    )
    sqs_queue = utils.build_sqs_url(session=session, queue_name=sqs_queue)
    message = build_sqs_message(record=event_record, new_account=new_account)
    utils.send_sqs_message(session=session, sqs_url=sqs_queue, message=message)


def delete_account_request(record: Dict[str, Any]) -> bool:
    if record["eventName"] == "REMOVE":
        return True
    return False


def control_tower_param_changed(record: Dict[str, Any]) -> bool:
    if record["eventName"] == "MODIFY":
        old_image = utils.unmarshal_ddb_item(record["dynamodb"]["OldImage"])[
            "control_tower_parameters"
        ]
        new_image = utils.unmarshal_ddb_item(record["dynamodb"]["NewImage"])[
            "control_tower_parameters"
        ]

        if old_image != new_image:
            return True
    return False


def build_sqs_message(record: Dict[str, Any], new_account: bool) -> Dict[str, Any]:
    logger.info("Building SQS Message - ")
    message = {}
    operation = "ADD" if new_account else "UPDATE"

    new_image = utils.unmarshal_ddb_item(record["dynamodb"]["NewImage"])
    message["operation"] = operation
    message["control_tower_parameters"] = new_image["control_tower_parameters"]

    if record["eventName"] == "MODIFY":
        old_image = utils.unmarshal_ddb_item(record["dynamodb"]["OldImage"])
        message["old_control_tower_parameters"] = old_image["control_tower_parameters"]

    logger.info(message)
    return message


def build_aft_account_provisioning_framework_event(
    record: Dict[str, Any]
) -> Dict[str, Any]:
    account_request = utils.unmarshal_ddb_item(record["dynamodb"]["NewImage"])
    aft_account_provisioning_framework_event = {
        "account_request": account_request,
        "control_tower_event": {},
    }
    logger.info(aft_account_provisioning_framework_event)
    return aft_account_provisioning_framework_event


def put_audit_record(
    session: Session, table: str, image: Dict[str, Any], event_name: str
) -> Dict[str, Any]:
    dynamodb = session.client("dynamodb")
    item = image

    datetime_format = "%Y-%m-%dT%H:%M:%S.%f"
    current_time = datetime.now().strftime(datetime_format)
    item["timestamp"] = {"S": current_time}

    item["ddb_event_name"] = {"S": event_name}

    logger.info("Inserting item into " + table + " table: " + str(item))

    response: Dict[str, Any] = dynamodb.put_item(TableName=table, Item=item)

    logger.info(response)

    return response


def new_ct_request_is_valid(session: Session, request: Dict[str, Any]) -> bool:
    logger.info("Validating new CT Account Request")
    org_account_emails = utils.get_org_account_emails(session)
    org_account_names = utils.get_org_account_names(session)

    ct_parameters = request["control_tower_parameters"]

    if ct_parameters["AccountEmail"] not in org_account_emails:
        logger.info("Requested AccountEmail is valid: " + ct_parameters["AccountEmail"])
        if ct_parameters["AccountName"] not in org_account_names:
            logger.info(
                "Valid request - AccountName and AccountEmail not already in use"
            )
            return True
        else:
            logger.info(
                "Invalid Request - AccountName already exists in Organization: "
                + ct_parameters["AccountName"]
            )
            return False
    else:
        logger.info(
            f"Invalid Request - AccountEmail already exists in Organization: {ct_parameters['AccountEmail']}"
        )
        return False


def modify_ct_request_is_valid(request: Dict[str, Any]) -> bool:
    logger.info("Validating modify CT Account Request")

    old_ct_parameters = request.get("old_control_tower_parameters", {})
    new_ct_parameters = request["control_tower_parameters"]

    for i in old_ct_parameters.keys():
        if i != "ManagedOrganizationalUnit":
            if old_ct_parameters[i] != new_ct_parameters[i]:
                logger.info(i + " cannot be modified")
                return False

    logger.info("Modify CT Account Request is Valid")
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

    aft_version = utils.get_ssm_parameter_value(session, "/aft/config/aft/version")
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
        ProductId=utils.get_ct_product_id(session, ct_management_session),
        ProvisioningArtifactId=utils.get_ct_provisioning_artifact_id(
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

    aft_version = utils.get_ssm_parameter_value(session, "/aft/config/aft/version")
    header_with_aft_version = partial(add_header, version=aft_version)
    event_system.register_first("before-sign.*.*", header_with_aft_version)

    provisioning_parameters: List[UpdateProvisioningParameterTypeDef] = []
    for k, v in request["control_tower_parameters"].items():
        provisioning_parameters.append({"Key": k, "Value": v})

    control_tower_email_parameter = request["control_tower_parameters"]["AccountEmail"]
    target_product: Optional[ProvisionedProductAttributeTypeDef] = None
    for batch in get_healthy_ct_product_batch(
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

            if (
                provisioned_product_email.lower()
                == control_tower_email_parameter.lower()
            ):
                target_product = product
                break

    if target_product is None:
        raise Exception(
            f"No healthy provisioned product found for {control_tower_email_parameter}"
        )

    # check to see if the product still exists and is still active
    if utils.ct_provisioning_artifact_is_active(
        session, ct_management_session, target_product["ProvisioningArtifactId"]
    ):
        target_provisioning_artifact_id = target_product["ProvisioningArtifactId"]
    else:
        target_provisioning_artifact_id = utils.get_ct_provisioning_artifact_id(
            session, ct_management_session
        )

    logger.info(
        "Modifying existing account leveraging parameters: "
        + str(provisioning_parameters)
        + " with provisioned product ID "
        + target_product["Id"]
    )
    update_response = client.update_provisioned_product(
        ProvisionedProductId=target_product["Id"],
        ProductId=utils.get_ct_product_id(session, ct_management_session),
        ProvisioningArtifactId=target_provisioning_artifact_id,
        ProvisioningParameters=provisioning_parameters,
        UpdateToken=str(uuid.uuid1()),
    )
    logger.info(update_response)


def get_account_request_record(session: Session, id: str) -> Dict[str, Any]:
    table_name = utils.get_ssm_parameter_value(
        session, utils.SSM_PARAM_AFT_DDB_REQ_TABLE
    )
    dynamodb = session.resource("dynamodb")
    table = dynamodb.Table(table_name)
    logger.info("Getting record for id " + id + " in DDB table " + table_name)
    response = table.get_item(Key={"id": id})
    logger.info(response)
    if "Item" in response:
        logger.info("Record found, returning item")
        logger.info(response["Item"])
        response_item: Dict[str, Any] = response["Item"]
        return response_item
    else:
        logger.info("Record not found in DDB table, exiting")
        sys.exit(1)


def is_customizations_event(event: Dict[str, Any]) -> bool:
    if "account_request" in event.keys():
        return True
    else:
        return False


def build_invoke_event(
    session: Session,
    ct_management_session: Session,
    event: Dict[str, Any],
    event_type: str,
) -> Dict[str, Any]:
    account_id: str = ""
    if event_type == "ControlTower":
        if event["detail"]["eventName"] == "CreateManagedAccount":
            account_id = event["detail"]["serviceEventDetails"][
                "createManagedAccountStatus"
            ]["account"]["accountId"]
        elif event["detail"]["eventName"] == "UpdateManagedAccount":
            account_id = event["detail"]["serviceEventDetails"][
                "updateManagedAccountStatus"
            ]["account"]["accountId"]
        account_email = utils.get_account_email_from_id(
            ct_management_session, account_id
        )
        ddb_record = get_account_request_record(session, account_email)
        invoke_event = {"control_tower_event": event, "account_request": ddb_record}
        # convert ddb strings into proper data type for json validation
        account_tags = json.loads(ddb_record["account_tags"])
        invoke_event["account_request"]["account_tags"] = account_tags
        invoke_event["account_provisioning"] = {}
        invoke_event["account_provisioning"]["run_create_pipeline"] = "true"
        logger.info("Invoking SFN with Event - ")
        logger.info(invoke_event)
        return invoke_event

    elif event_type == "Customizations":
        invoke_event = event
        # convert ddb strings into proper data type for json validation
        account_tags = json.loads(event["account_request"]["account_tags"])
        invoke_event["account_request"]["account_tags"] = account_tags
        invoke_event["account_provisioning"] = {}
        invoke_event["account_provisioning"]["run_create_pipeline"] = "true"
        logger.info("Invoking SFN with Event - ")
        logger.info(invoke_event)
        return invoke_event

    raise Exception("Unsupported event type")
