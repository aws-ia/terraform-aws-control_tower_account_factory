import json
import os
import uuid
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Sequence,
    Union,
    cast,
)

import attr
import boto3
from boto3.dynamodb.types import TypeDeserializer
from boto3.session import Session
from botocore.response import StreamingBody

if TYPE_CHECKING:
    from mypy_boto3_lambda import LambdaClient
    from mypy_boto3_lambda.type_defs import InvocationResponseTypeDef
    from mypy_boto3_organizations import OrganizationsClient
    from mypy_boto3_organizations.type_defs import TagTypeDef
    from mypy_boto3_servicecatalog import ServiceCatalogClient
    from mypy_boto3_sns import SNSClient
    from mypy_boto3_sns.type_defs import PublishResponseTypeDef
    from mypy_boto3_sqs import SQSClient
    from mypy_boto3_sqs.type_defs import MessageTypeDef, SendMessageResultTypeDef
    from mypy_boto3_stepfunctions import SFNClient
    from mypy_boto3_stepfunctions.type_defs import StartExecutionOutputTypeDef
    from mypy_boto3_sts import STSClient
    from mypy_boto3_sts.type_defs import (
        AssumeRoleRequestRequestTypeDef,
        CredentialsTypeDef,
    )
else:
    LambdaClient = object
    InvocationResponseTypeDef = object
    OrganizationsClient = object
    TagTypeDef = object
    ServiceCatalogClient = object
    SNSClient = object
    PublishResponseTypeDef = object
    SQSClient = object
    MessageTypeDef = object
    SendMessageResultTypeDef = object
    SFNClient = object
    StartExecutionOutputTypeDef = object
    STSClient = object
    CredentialsTypeDef = object

from aft_common.account import AftAccountInfo

from .logger import Logger

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
SSM_PARAM_AFT_ACCOUNT_PROVISIONING_FRAMEWORK_VALIDATE_REQUEST_FUNCTION_ARN = "/aft/resources/lambda/aft-account-provisioning-framework-validate-request-function-arn"
SSM_PARAM_AFT_ACCOUNT_PROVISIONING_FRAMEWORK_GET_ACCOUNT_INFO_FUNCTION_ARN = "/aft/resources/lambda/aft-account-provisioning-framework-get-account-info-function-arn"
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


# INIT
def get_logger() -> Logger:
    # initialise logger
    if "log_level" in os.environ.keys():
        log_level = os.environ["log_level"]
    else:
        # presumed local debugging
        log_level = "info"
    logger = Logger(loglevel=log_level)
    logger.info("Logger started.")
    logger.info(str(os.environ))
    return logger


logger = get_logger()


def get_ssm_parameter_value(session: Session, param: str, decrypt: bool = False) -> str:
    client = session.client("ssm")
    logger.info("Getting SSM Parameter " + param)

    response = client.get_parameter(Name=param, WithDecryption=decrypt)

    param_value: str = response["Parameter"]["Value"]
    return param_value


def put_ddb_item(
    session: Session, table_name: str, item: Dict[str, str]
) -> Dict[str, Any]:
    dynamodb = session.resource("dynamodb")
    table = dynamodb.Table(table_name)

    logger.info("Inserting item into " + table_name + " table: " + str(item))

    response: Dict[str, Any] = table.put_item(Item=item)

    logger.info(response)

    return response


def get_account_id_from_email(ct_management_session: Session, email: str) -> str:
    logger.info("begin get_account_by_email")
    accounts = list_accounts(ct_management_session)
    account = [a for a in accounts if a["email"] == email]
    logger.info(account)
    if len(account):
        return account[0]["id"]
    else:
        raise Exception("Account not found for email")


def list_accounts(ct_management_session: Session) -> List[AftAccountInfo]:
    client: OrganizationsClient = ct_management_session.client("organizations")
    response = client.list_accounts()
    accounts = response["Accounts"]
    account_info: List[AftAccountInfo] = []
    while "NextToken" in response:
        response = client.list_accounts(NextToken=response["NextToken"])
        accounts.extend(response["Accounts"])

    for a in accounts:
        account_info.append(get_account_info(ct_management_session, a["Id"]))

    return account_info


def get_account_info(ct_management_session: Session, account_id: str) -> AftAccountInfo:
    logger.info(f"Getting details for {account_id}")

    client: OrganizationsClient = ct_management_session.client("organizations")
    describe_response = client.describe_account(AccountId=account_id)

    account = describe_response["Account"]
    list_response = client.list_parents(ChildId=account["Id"])
    parents = list_response["Parents"]
    parent_id = parents[0]["Id"]
    parent_type = parents[0]["Type"]
    org_name = ""

    if parent_type == "ORGANIZATIONAL_UNIT":
        org_details = client.describe_organizational_unit(
            OrganizationalUnitId=parent_id
        )
        org_name = org_details["OrganizationalUnit"]["Name"]

    return AftAccountInfo(
        id=account["Id"],
        email=account["Email"],
        name=account["Name"],
        joined_method=account["JoinedMethod"],
        joined_date=str(account["JoinedTimestamp"]),
        status=account["Status"],
        parent_id=parent_id,
        parent_type=parent_type,
        org_name=org_name,
        type="account",
        vendor="aws",
    )


def get_assume_role_credentials(
    session: Session,
    role_arn: str,
    session_name: str,
    external_id: Optional[str] = None,
    session_duration: int = 900,
    session_policy: Optional[str] = None,
) -> CredentialsTypeDef:
    client: STSClient = session.client("sts")

    assume_role_params: AssumeRoleRequestRequestTypeDef = {
        "RoleArn": role_arn,
        "RoleSessionName": session_name,
        "DurationSeconds": session_duration,
    }

    if external_id:
        assume_role_params.update({"ExternalId": external_id})

    if session_policy:
        assume_role_params.update({"Policy": session_policy})

    assume_role_response = client.assume_role(**assume_role_params)

    credentials = assume_role_response["Credentials"]
    return credentials


def build_role_arn(
    session: Session, role_name: str, account_id: Optional[str] = None
) -> str:
    account_info = get_session_info(session)
    role_arn: str
    if not account_id:
        role_arn = "arn:aws:iam::" + account_info["account"] + ":role/" + role_name
        return role_arn
    else:
        role_arn = "arn:aws:iam::" + account_id + ":role/" + role_name
        return role_arn


def get_session_info(session: Session) -> Dict[str, str]:
    client: STSClient = session.client("sts")
    response = client.get_caller_identity()

    account_info = {"region": session.region_name, "account": response["Account"]}

    return account_info


def get_boto_session(credentials: CredentialsTypeDef) -> Session:
    return boto3.session.Session(
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
    )


def get_ct_management_session(session: Session) -> Session:
    ct_mgmt_account = get_ssm_parameter_value(
        session, SSM_PARAM_ACCOUNT_CT_MANAGEMENT_ACCOUNT_ID
    )
    administrator_role = get_ssm_parameter_value(session, SSM_PARAM_AFT_ADMIN_ROLE)
    execution_role = get_ssm_parameter_value(session, SSM_PARAM_AFT_EXEC_ROLE)
    session_name = get_ssm_parameter_value(session, SSM_PARAM_AFT_SESSION_NAME)

    # Assume aws-aft-AdministratorRole locally
    local_creds = get_assume_role_credentials(
        session, build_role_arn(session, administrator_role), session_name
    )
    local_assumed_session = get_boto_session(local_creds)
    # Assume AWSAFTExecutionRole in CT management
    ct_mgmt_creds = get_assume_role_credentials(
        local_assumed_session,
        build_role_arn(session, execution_role, ct_mgmt_account),
        session_name,
    )
    return get_boto_session(ct_mgmt_creds)


def get_aft_admin_role_session(session: Session) -> Session:
    administrator_role = get_ssm_parameter_value(session, SSM_PARAM_AFT_ADMIN_ROLE)
    execution_role = get_ssm_parameter_value(session, SSM_PARAM_AFT_EXEC_ROLE)
    session_name = get_ssm_parameter_value(session, SSM_PARAM_AFT_SESSION_NAME)

    # Assume aws-aft-AdministratorRole locally
    local_creds = get_assume_role_credentials(
        session, build_role_arn(session, administrator_role), session_name
    )

    return get_boto_session(local_creds)


def get_log_archive_session(session: Session) -> Session:
    log_archive_account = get_ssm_parameter_value(
        session, SSM_PARAM_ACCOUNT_LOG_ARCHIVE_ACCOUNT_ID
    )
    administrator_role = get_ssm_parameter_value(session, SSM_PARAM_AFT_ADMIN_ROLE)
    execution_role = get_ssm_parameter_value(session, SSM_PARAM_AFT_EXEC_ROLE)
    session_name = get_ssm_parameter_value(session, SSM_PARAM_AFT_SESSION_NAME)

    # Assume aws-aft-AdministratorRole locally
    local_creds = get_assume_role_credentials(
        session, build_role_arn(session, administrator_role), session_name
    )
    local_assumed_session = get_boto_session(local_creds)
    # Assume AWSAFTExecutionRole in CT management
    log_archive_creds = get_assume_role_credentials(
        local_assumed_session,
        build_role_arn(session, execution_role, log_archive_account),
        session_name,
    )
    return get_boto_session(log_archive_creds)


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


def product_provisioning_in_progress(
    ct_management_session: Session, product_id: str
) -> bool:
    client: ServiceCatalogClient = ct_management_session.client("servicecatalog")

    logger.info("Checking for product provisioning in progress")

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

    for p in pps:
        if p["ProductId"] == product_id:
            logger.info("Identified CT Product - " + p["Id"])
            if p["Status"] in ["UNDER_CHANGE", "PLAN_IN_PROGRESS"]:
                logger.info("Product provisioning in Progress")
                return True

    logger.info("No product provisioning in Progress")
    return False


def build_sqs_url(session: Session, queue_name: str) -> str:
    account_info = get_session_info(session)
    url = (
        "https://sqs."
        + account_info["region"]
        + ".amazonaws.com/"
        + account_info["account"]
        + "/"
        + queue_name
    )
    return url


def receive_sqs_message(session: Session, sqs_queue: str) -> Optional[MessageTypeDef]:
    client: SQSClient = session.client("sqs")
    logger.info("Fetching SQS Messages from " + build_sqs_url(session, sqs_queue))

    response = client.receive_message(
        QueueUrl=build_sqs_url(session, sqs_queue),
        MaxNumberOfMessages=1,
        ReceiveRequestAttemptId=str(uuid.uuid1()),
    )
    if "Messages" in response.keys():
        logger.info("There are messages pending processing")
        message = response["Messages"][0]
        logger.info("Message retrieved")
        logger.info(message)
        return message
    else:
        logger.info("There are no messages pending processing")
        return None


def get_org_account_emails(ct_management_session: Session) -> List[str]:
    accounts = list_accounts(ct_management_session)

    return [a["email"] for a in accounts]


def get_org_account_names(ct_management_session: Session) -> List[str]:
    accounts = list_accounts(ct_management_session)

    return [a["name"] for a in accounts]


def get_org_ou_names(session: Session) -> List[str]:
    client: OrganizationsClient = session.client("organizations")
    logger.info("Listing roots in the Organization")
    root_id: str = ""
    list_roots_response = client.list_roots()
    roots = list_roots_response["Roots"]
    while "NextToken" in list_roots_response:
        list_roots_response = client.list_roots(
            NextToken=list_roots_response["NextToken"]
        )
        roots.extend(list_roots_response["Roots"])

    for r in roots:
        if r["Name"] == "Root":
            root_id = r["Id"]
        else:
            raise Exception("Root called 'Root' was not found")

    logger.info("Listing OUs for Root " + root_id)

    list_ou_response = client.list_organizational_units_for_parent(ParentId=root_id)
    ous = list_ou_response["OrganizationalUnits"]

    logger.info(ous)

    ou_names = []

    for o in ous:
        ou_names.append(o["Name"])

    logger.info("OU Names: " + str(ou_names))
    return ou_names


def delete_sqs_message(session: Session, message: MessageTypeDef) -> None:
    client: SQSClient = session.client("sqs")
    sqs_queue = get_ssm_parameter_value(session, SSM_PARAM_ACCOUNT_REQUEST_QUEUE)
    receipt_handle = message["ReceiptHandle"]
    logger.info("Deleting SQS message with handle " + receipt_handle)
    client.delete_message(
        QueueUrl=build_sqs_url(session, sqs_queue), ReceiptHandle=receipt_handle
    )


def unmarshal_ddb_item(
    low_level_data: Dict[
        str,
        Dict[Literal["S", "N", "B", "SS", "NS", "BS", "NULL", "BOOL", "M", "L"], Any],
    ]
) -> Dict[str, Any]:
    # To go from low-level format to python

    deserializer = boto3.dynamodb.types.TypeDeserializer()
    python_data = {k: deserializer.deserialize(v) for k, v in low_level_data.items()}
    return python_data


def send_sqs_message(
    session: Session, sqs_url: str, message: Dict[str, Any]
) -> SendMessageResultTypeDef:
    sqs: SQSClient = session.client("sqs")
    logger.info("Sending SQS message to " + sqs_url)
    logger.info(message)

    unique_id = str(uuid.uuid1())

    response = sqs.send_message(
        QueueUrl=sqs_url,
        MessageBody=json.dumps(message),
        MessageDeduplicationId=unique_id,
        MessageGroupId=unique_id,
    )

    logger.info(response)

    return response


def invoke_lambda(
    session: Session,
    function_name: str,
    payload: Union[bytes, IO[bytes], StreamingBody],
) -> InvocationResponseTypeDef:
    client: LambdaClient = session.client("lambda")
    logger.info("Invoking AFT Account Provisioning Framework Lambda")
    response = client.invoke(
        FunctionName=function_name,
        InvocationType="Event",
        LogType="Tail",
        Payload=payload,
    )
    logger.info(response)
    return response


def get_account_email_from_id(ct_management_session: Session, id: str) -> str:
    accounts = list_accounts(ct_management_session)
    logger.info("Getting account email for account id " + id)
    for a in accounts:
        if a["id"] == id:
            email = a["email"]
            logger.info("Account email: " + email)
            return email
    raise Exception("Account ID " + id + " was not found in the Organization")


def build_sfn_arn(session: Session, sfn_name: str) -> str:
    account_info = get_session_info(session)
    sfn_arn = (
        "arn:aws:states:"
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
    logger.info(response)
    return response


def is_controltower_event(event: Dict[str, Any]) -> bool:
    if "source" in event.keys():
        if event["source"] == "aws.controltower":
            logger.info("Event is Control Tower event")
            return True
        else:
            logger.info("Event is NOT Control Tower event")
            return False
    return False


def is_aft_supported_controltower_event(event: Dict[str, Any]) -> bool:
    supported_events = ["CreateManagedAccount", "UpdateManagedAccount"]
    if event["detail"]["eventName"] in supported_events:
        logger.info("Control Tower Event is supported")
        return True
    else:
        logger.info("Control Tower Event is NOT supported")
        return False


def send_sns_message(
    session: Session, topic: str, sns_message: str, subject: str
) -> PublishResponseTypeDef:
    logger.info("Sending SNS Message")
    client: SNSClient = session.client("sns")

    response = client.publish(TopicArn=topic, Message=sns_message, Subject=subject)

    logger.info(response)

    return response


def tag_org_resource(
    ct_management_session: Session,
    resource: str,
    tags: Sequence[TagTypeDef],
    rollback: bool = False,
) -> None:
    client: OrganizationsClient = ct_management_session.client("organizations")
    if rollback:
        current_tags = client.list_tags_for_resource(ResourceId=resource)
        client.untag_resource(ResourceId=resource, TagKeys=[tag["Key"] for tag in tags])
        client.tag_resource(
            ResourceId=resource, Tags=cast(Sequence[TagTypeDef], current_tags)
        )

    else:
        client.tag_resource(ResourceId=resource, Tags=tags)


def get_all_aft_account_ids(session: Session) -> List[str]:
    table_name = get_ssm_parameter_value(session, SSM_PARAM_AFT_DDB_META_TABLE)
    dynamodb = session.resource("dynamodb")
    table = dynamodb.Table(table_name)
    logger.info("Scanning DynamoDB table: " + table_name)

    items: List[Dict[str, str]] = []
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


def get_account_ids_in_ous(
    session: Session, ou_names: List[str]
) -> Optional[List[str]]:
    client: OrganizationsClient = session.client("organizations")
    logger.info("Getting Account IDs in the following OUs: " + str(ou_names))
    ou_ids = []
    account_ids = []
    for n in ou_names:
        ou_ids.append(get_org_ou_id(session, n))
    logger.info("OU IDs: " + str(ou_ids))
    for ou_id in ou_ids:
        if ou_id is not None:
            logger.info("Listing accounts in the OU ID " + ou_id)

            response = client.list_children(ParentId=ou_id, ChildType="ACCOUNT")
            children = response["Children"]
            while "NextToken" in response:
                response = client.list_children(
                    ParentId=ou_id,
                    ChildType="ACCOUNT",
                    NextToken=response["NextToken"],
                )
                children.extend(response["Children"])

            logger.info(str(children))

            for a in children:
                account_ids.append(a["Id"])
        else:
            logger.info("OUs in " + str(ou_names) + " was not found")
    logger.info("Account IDs: " + str(account_ids))
    if len(account_ids) > 0:
        return account_ids
    else:
        return None


def get_org_ou_id(session: Session, ou_name: str) -> Optional[str]:
    client: OrganizationsClient = session.client("organizations")
    logger.info("Listing Org Roots")
    list_roots_response = client.list_roots(MaxResults=1)
    logger.info(list_roots_response)
    root_id = list_roots_response["Roots"][0]["Id"]
    logger.info("Root ID is " + root_id)

    logger.info("Listing OUs in the Organization")

    list_ou_response = client.list_organizational_units_for_parent(ParentId=root_id)
    ous = list_ou_response["OrganizationalUnits"]
    while "NextToken" in list_ou_response:
        list_ou_response = client.list_organizational_units_for_parent(
            ParentId=root_id, NextToken=list_ou_response["NextToken"]
        )
        ous.extend(list_ou_response["OrganizationalUnits"])

    logger.info(ous)

    for ou in ous:
        if ou["Name"] == ou_name:
            ou_id: str = ou["Id"]
            logger.info("OU ID for " + ou_name + " is " + ou_id)
            return ou_id

    return None


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
