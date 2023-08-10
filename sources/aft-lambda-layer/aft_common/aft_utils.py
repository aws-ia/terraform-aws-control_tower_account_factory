# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import logging
import os
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Union,
    cast,
)

from boto3.session import Session
from botocore.response import StreamingBody

if TYPE_CHECKING:
    from mypy_boto3_lambda import LambdaClient
    from mypy_boto3_lambda.type_defs import InvocationResponseTypeDef
    from mypy_boto3_organizations import OrganizationsClient
    from mypy_boto3_servicecatalog import ServiceCatalogClient
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

SSM_PARAM_AFT_DDB_META_TABLE = "/aft/resources/ddb/aft-request-metadata-table-name"
SSM_PARAM_AFT_SESSION_NAME = "/aft/resources/iam/aft-session-name"
SSM_PARAM_AFT_ADMIN_ROLE = "/aft/resources/iam/aft-administrator-role-name"
SSM_PARAM_AFT_EXEC_ROLE = "/aft/resources/iam/aft-execution-role-name"
SSM_PARAM_SC_PRODUCT_NAME = "/aft/resources/sc/account-factory-product-name"
SSM_PARAM_SNS_TOPIC_ARN = "/aft/account/aft-management/sns/topic-arn"
SSM_PARAM_SNS_FAILURE_TOPIC_ARN = "/aft/account/aft-management/sns/failure-topic-arn"
SSM_PARAM_ACCOUNT_REQUEST_QUEUE = "/aft/resources/sqs/aft-request-queue-name"
SSM_PARAM_AFT_ACCOUNT_PROVISIONING_FRAMEWORK_LAMBDA = (
    "/aft/resources/lambda/aft-invoke-aft-account-provisioning-framework"
)
SSM_PARAM_AFT_CLEANUP_RESOURCES_LAMBDA = "/aft/resources/lambda/aft-cleanup-resources"
SSM_PARAM_AFT_EVENTS_TABLE = "/aft/resources/ddb/aft-controltower-events-table-name"
SSM_PARAM_AFT_SFN_NAME = (
    "/aft/account/aft-management/sfn/aft-account-provisioning-framework-sfn-name"
)
SSM_PARAM_AFT_DDB_REQ_TABLE = "/aft/resources/ddb/aft-request-table-name"
SSM_PARAM_AFT_DDB_AUDIT_TABLE = "/aft/resources/ddb/aft-request-audit-table-name"
SSM_PARAM_AFT_REQUEST_ACTION_TRIGGER_FUNCTION_ARN = (
    "/aft/resources/lambda/aft-account-request-action-trigger-function-arn"
)
SSM_PARAM_AFT_ACCOUNT_REQUEST_AUDIT_TRIGGER_FUNCTION_ARN = (
    "/aft/resources/lambda/aft-account-request-audit-trigger-function-arn"
)
SSM_PARAM_AFT_ACCOUNT_REQUEST_PROCESSOR_FUNCTION_ARN = (
    "/aft/resources/lambda/aft-account-request-processor-function-arn"
)
SSM_PARAM_AFT_CONTROLTOWER_EVENT_LOGGER_FUNCTION_ARN = (
    "/aft/resources/lambda/aft-controltower-event-logger-function-arn"
)
SSM_PARAM_AFT_INVOKE_AFT_ACCOUNT_PROVISIONING_FRAMEWORK_FUNCTION_ARN = (
    "/aft/resources/lambda/aft-invoke-aft-account-provisioning-framework-function-arn"
)
SSM_PARAM_AFT_ACCOUNT_PROVISIONING_FRAMEWORK_CREATE_ROLE_FUNCTION_ARN = (
    "/aft/resources/lambda/aft-account-provisioning-framework-create-role-function-arn"
)
SSM_PARAM_AFT_ACCOUNT_PROVISIONING_FRAMEWORK_TAG_ACCOUNT_FUNCTION_ARN = (
    "/aft/resources/lambda/aft-account-provisioning-framework-tag-account-function-arn"
)
SSM_PARAM_AFT_ACCOUNT_PROVISIONING_FRAMEWORK_PERSIST_METADATA_FUNCTION_ARN = "/aft/resources/lambda/aft-account-provisioning-framework-persist-metadata-function-arn"
SSM_PARAM_AFT_ACCOUNT_PROVISIONING_FRAMEWORK_NOTIFY_ERROR_FUNCTION_ARN = (
    "/aft/resources/lambda/aft-account-provisioning-framework-notify-error-function-arn"
)
SSM_PARAM_AFT_ACCOUNT_PROVISIONING_FRAMEWORK_NOTIFY_SUCCESS_FUNCTION_ARN = "/aft/resources/lambda/aft-account-provisioning-framework-notify-success-function-arn"
SSM_PARAM_AFT_MAXIMUM_CONCURRENT_CUSTOMIZATIONS = (
    "/aft/config/customizations/maximum_concurrent_customizations"
)
SSM_PARAM_FEATURE_CLOUDTRAIL_DATA_EVENTS_ENABLED = (
    "/aft/config/feature/cloudtrail-data-events-enabled"
)
SSM_PARAM_FEATURE_ENTERPRISE_SUPPORT_ENABLED = (
    "/aft/config/feature/enterprise-support-enabled"
)
SSM_PARAM_FEATURE_DEFAULT_VPCS_ENABLED = (
    "/aft/config/feature/delete-default-vpcs-enabled"
)
SSM_PARAM_ACCOUNT_CT_MANAGEMENT_ACCOUNT_ID = "/aft/account/ct-management/account-id"
SSM_PARAM_ACCOUNT_AUDIT_ACCOUNT_ID = "/aft/account/audit/account-id"
SSM_PARAM_ACCOUNT_LOG_ARCHIVE_ACCOUNT_ID = "/aft/account/log-archive/account-id"
SSM_PARAM_ACCOUNT_AFT_MANAGEMENT_ACCOUNT_ID = "/aft/account/aft-management/account-id"

SSM_PARAM_ACCOUNT_AFT_VERSION = "/aft/config/aft/version"
SSM_PARAM_ACCOUNT_TERRAFORM_VERSION = "/aft/config/terraform/version"

SSM_PARAM_AFT_METRICS_REPORTING = "/aft/config/metrics-reporting"
SSM_PARAM_AFT_METRICS_REPORTING_UUID = "/aft/config/metrics-reporting-uuid"

logger = logging.getLogger("aft")


def emails_are_equal(first_email: str, second_email: str) -> bool:
    return first_email.lower() == second_email.lower()


def get_ssm_parameter_value(session: Session, param: str, decrypt: bool = False) -> str:
    client = session.client("ssm")
    logger.info("Getting SSM Parameter " + param)

    response = client.get_parameter(Name=param, WithDecryption=decrypt)

    param_value: str = response["Parameter"]["Value"]
    return param_value


def get_ct_product_id(session: Session, ct_management_session: Session) -> str:
    client: ServiceCatalogClient = ct_management_session.client("servicecatalog")
    sc_product_name = get_ssm_parameter_value(session, SSM_PARAM_SC_PRODUCT_NAME)
    logger.info("Getting product ID for " + sc_product_name)

    response = client.describe_product_as_admin(Name=sc_product_name)
    product_id: str = response["ProductViewDetail"]["ProductViewSummary"]["ProductId"]
    logger.info(product_id)
    return product_id


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


def ct_provisioning_artifact_is_active(
    session: Session, ct_management_session: Session, artifact_id: str
) -> bool:
    client: ServiceCatalogClient = ct_management_session.client("servicecatalog")
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


def invoke_lambda(
    session: Session,
    function_name: str,
    payload: Union[bytes, IO[bytes], StreamingBody],
) -> InvocationResponseTypeDef:
    client: LambdaClient = session.client("lambda")
    logger.info(f"Invoking Lambda: {function_name}")
    response = client.invoke(
        FunctionName=function_name,
        InvocationType="Event",
        LogType="Tail",
        Payload=payload,
    )
    logger.info(response)
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
    logger.info("Starting SFN execution of " + sfn_arn)
    response = client.start_execution(stateMachineArn=sfn_arn, input=input)
    logger.debug(response)
    return response


def is_aft_supported_controltower_event(event: Dict[str, Any]) -> bool:
    if event.get("source", None) == "aws.controltower":
        supported_events = ["CreateManagedAccount", "UpdateManagedAccount"]
        if event.get("detail", {}).get("eventName", None) in supported_events:
            logger.info("Received AFT supported Control Tower Event")
            return True

    return False


def get_all_aft_account_ids(aft_management_session: Session) -> List[str]:
    table_name = get_ssm_parameter_value(
        aft_management_session, SSM_PARAM_AFT_DDB_META_TABLE
    )
    dynamodb = aft_management_session.resource("dynamodb")
    table = dynamodb.Table(table_name)
    logger.info("Scanning DynamoDB table: " + table_name)

    items: List[Dict[str, Any]] = []
    response = table.scan(ProjectionExpression="id", ConsistentRead=True)
    items.extend(response["Items"])
    while "LastEvaluatedKey" in response:
        logger.debug(
            "Paginated response found, continuing at {}".format(
                response["LastEvaluatedKey"]
            )
        )
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response["Items"])

    aft_account_ids = [item["id"] for item in items]

    if not aft_account_ids:
        raise Exception("No accounts found in the Account Metadata table")

    return aft_account_ids


def get_accounts_by_tags(
    aft_mgmt_session: Session, ct_mgmt_session: Session, tags: List[Dict[str, str]]
) -> Optional[List[str]]:
    logger.info("Getting Account with tags - " + str(tags))
    # Get all AFT Managed Accounts
    all_accounts = get_all_aft_account_ids(aft_mgmt_session)
    matched_accounts = []
    client: OrganizationsClient = ct_mgmt_session.client("organizations")
    # Loop through AFT accounts, requesting tags
    if all_accounts is None:
        return None

    for a in all_accounts:
        account_tags = {}
        response = client.list_tags_for_resource(ResourceId=a)
        # Format tags as a dictionary rather than a list
        for t in response["Tags"]:
            account_tags[t["Key"]] = t["Value"]
        logger.info("Account tags for " + a + ": " + str(account_tags))
        counter = 0
        # Loop through tag filter. Append account to matched_accounts if all tags in filter match/ are present
        for x in tags:
            for k, v in x.items():
                if k in account_tags.keys():
                    if account_tags[k] == v:
                        counter += 1
                        if counter == len(tags):
                            logger.info(
                                "Account " + a + " MATCHED with tags " + str(tags)
                            )
                            matched_accounts.append(a)
    logger.info(matched_accounts)
    if len(matched_accounts) > 0:
        return matched_accounts
    else:
        return None


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
