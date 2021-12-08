import inspect
import json
import os
import uuid
from .logger import Logger
import boto3
import botocore
from boto3.dynamodb.types import TypeDeserializer
from botocore.exceptions import ClientError

SSM_PARAM_AFT_DDB_META_TABLE = "/aft/resources/ddb/aft-request-metadata-table-name"
SSM_PARAM_AFT_SESSION_NAME = "/aft/resources/iam/aft-session-name"
SSM_PARAM_AFT_ADMIN_ROLE = "/aft/resources/iam/aft-administrator-role-name"
SSM_PARAM_AFT_EXEC_ROLE = "/aft/resources/iam/aft-execution-role-name"
SSM_PARAM_SC_PRODUCT_NAME = "/aft/resources/sc/account-factory-product-name"
SSM_PARAM_SNS_TOPIC_ARN = "/aft/account/aft-management/sns/topic-arn"
SSM_PARAM_SNS_FAILURE_TOPIC_ARN = "/aft/account/aft-management/sns/failure-topic-arn"
SSM_PARAM_ACCOUNT_REQUEST_QUEUE = "/aft/resources/sqs/aft-request-queue-name"
SSM_PARAM_AFT_ACCOUNT_PROVISIONING_FRAMEWORK_LAMBDA = "/aft/resources/lambda/aft-invoke-aft-account-provisioning-framework"
SSM_PARAM_AFT_EVENTS_TABLE = "/aft/resources/ddb/aft-controltower-events-table-name"
SSM_PARAM_AFT_SFN_NAME = "/aft/account/aft-management/sfn/aft-account-provisioning-framework-sfn-name"
SSM_PARAM_AFT_DDB_REQ_TABLE = "/aft/resources/ddb/aft-request-table-name"
SSM_PARAM_AFT_DDB_AUDIT_TABLE = "/aft/resources/ddb/aft-request-audit-table-name"
SSM_PARAM_AFT_REQUEST_ACTION_TRIGGER_FUNCTION_ARN = "/aft/resources/lambda/aft-account-request-action-trigger-function-arn"
SSM_PARAM_AFT_ACCOUNT_REQUEST_AUDIT_TRIGGER_FUNCTION_ARN = "/aft/resources/lambda/aft-account-request-audit-trigger-function-arn"
SSM_PARAM_AFT_ACCOUNT_REQUEST_PROCESSOR_FUNCTION_ARN = "/aft/resources/lambda/aft-account-request-processor-function-arn"
SSM_PARAM_AFT_CONTROLTOWER_EVENT_LOGGER_FUNCTION_ARN = "/aft/resources/lambda/aft-controltower-event-logger-function-arn"
SSM_PARAM_AFT_INVOKE_AFT_ACCOUNT_PROVISIONING_FRAMEWORK_FUNCTION_ARN = "/aft/resources/lambda/aft-invoke-aft-account-provisioning-framework-function-arn"
SSM_PARAM_AFT_ACCOUNT_PROVISIONING_FRAMEWORK_VALIDATE_REQUEST_FUNCTION_ARN = "/aft/resources/lambda/aft-account-provisioning-framework-validate-request-function-arn"
SSM_PARAM_AFT_ACCOUNT_PROVISIONING_FRAMEWORK_GET_ACCOUNT_INFO_FUNCTION_ARN = "/aft/resources/lambda/aft-account-provisioning-framework-get-account-info-function-arn"
SSM_PARAM_AFT_ACCOUNT_PROVISIONING_FRAMEWORK_CREATE_ROLE_FUNCTION_ARN = "/aft/resources/lambda/aft-account-provisioning-framework-create-role-function-arn"
SSM_PARAM_AFT_ACCOUNT_PROVISIONING_FRAMEWORK_TAG_ACCOUNT_FUNCTION_ARN = "/aft/resources/lambda/aft-account-provisioning-framework-tag-account-function-arn"
SSM_PARAM_AFT_ACCOUNT_PROVISIONING_FRAMEWORK_PERSIST_METADATA_FUNCTION_ARN = "/aft/resources/lambda/aft-account-provisioning-framework-persist-metadata-function-arn"
SSM_PARAM_AFT_ACCOUNT_PROVISIONING_FRAMEWORK_NOTIFY_ERROR_FUNCTION_ARN = "/aft/resources/lambda/aft-account-provisioning-framework-notify-error-function-arn"
SSM_PARAM_AFT_ACCOUNT_PROVISIONING_FRAMEWORK_NOTIFY_SUCCESS_FUNCTION_ARN = "/aft/resources/lambda/aft-account-provisioning-framework-notify-success-function-arn"
SSM_PARAM_AFT_MAXIMUM_CONCURRENT_CUSTOMIZATIONS = "/aft/config/customizations/maximum_concurrent_customizations"
SSM_PARAM_FEATURE_CLOUDTRAIL_DATA_EVENTS_ENABLED = "/aft/config/feature/cloudtrail-data-events-enabled"
SSM_PARAM_FEATURE_ENTERPRISE_SUPPORT_ENABLED = "/aft/config/feature/enterprise-support-enabled"
SSM_PARAM_FEATURE_DEFAULT_VPCS_ENABLED = "/aft/config/feature/delete-default-vpcs-enabled"
SSM_PARAM_ACCOUNT_CT_MANAGEMENT_ACCOUNT_ID = "/aft/account/ct-management/account-id"
SSM_PARAM_ACCOUNT_AUDIT_ACCOUNT_ID = "/aft/account/audit/account-id"
SSM_PARAM_ACCOUNT_LOG_ARCHIVE_ACCOUNT_ID = "/aft/account/log-archive/account-id"
SSM_PARAM_ACCOUNT_AFT_MANAGEMENT_ACCOUNT_ID = "/aft/account/aft-management/account-id"

# INIT
def get_logger():
    # initialise logger
    if "log_level" in os.environ.keys():
        log_level = os.environ["log_level"]
    else:
        # presumed local debugging
        log_level = "info"
    logger = Logger(loglevel=log_level)
    logger.info("Logger started.")
    logger.info(os.environ)
    return logger


logger = get_logger()


def get_ssm_parameter_value(session, param, decrypt=False):
    try:
        client = session.client("ssm")
        logger.info("Getting SSM Parameter " + param)

        response = client.get_parameter(Name=param, WithDecryption=decrypt)
        return response["Parameter"]["Value"]

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def put_ddb_item(session, table_name, item):
    try:
        dynamodb = session.resource("dynamodb")
        table = dynamodb.Table(table_name)

        logger.info("Inserting item into " + table_name + " table: " + str(item))

        response = table.put_item(Item=item)

        logger.info(response)
        return response

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def get_account_by_email(ct_management_session, email):
    logger.info("begin get_account_by_email")
    accounts = list_accounts(ct_management_session)
    account = [a for a in accounts if a["email"] == email]
    if account is None:
        raise Exception(f"Account not found for email {email}")
    logger.info(account)
    if len(account):
        return account[0]
    else:
        return None


def list_accounts(ct_management_session):
    try:
        client = ct_management_session.client("organizations")
        paginator = client.get_paginator("list_accounts")
        marker = None
        accounts = []
        while True:
            if marker:
                response = paginator.paginate(
                    PaginationConfig={
                        "MaxItems": 123,
                        "PageSize": 20,
                        "StartingToken": marker,
                    }
                )
            else:
                response = paginator.paginate(
                    PaginationConfig={"MaxItems": 123, "PageSize": 20}
                )

            for acc_array in response:
                for acc in acc_array["Accounts"]:
                    accounts.append(get_account(ct_management_session, acc))
                try:
                    marker = acc_array["NextToken"]
                except KeyError:
                    return accounts
    except botocore.exceptions.ClientError as e:
        raise e


def get_account(ct_management_session, account):
    logger.info(f"Getting details for {account['Id']}")
    client = ct_management_session.client("organizations")
    response = client.describe_account(AccountId=account["Id"])
    account = response["Account"]
    response = client.list_parents(ChildId=account["Id"])
    parents = response["Parents"]
    parent_id = parents[0]["Id"]
    parent_type = parents[0]["Type"]
    org_name = ""
    if parent_type == "ORGANIZATIONAL_UNIT":
        org_details = client.describe_organizational_unit(
            OrganizationalUnitId=parent_id
        )
        org_name = org_details["OrganizationalUnit"]["Name"]

    # self._pp.pprint(parents)
    act = {
        "id": account["Id"],
        "type": "account",
        "email": account["Email"],
        "name": account["Name"],
        "method": account["JoinedMethod"],
        "joined_date": str(account["JoinedTimestamp"]),
        "status": account["Status"],
        "parent_id": parent_id,
        "parent_type": parent_type,
        "org_name": org_name,
        "vendor": "aws",
    }
    return act


def get_assume_role_credentials(
        session, role_arn, session_name, external_id=None, session_duration=900
):
    try:
        client = session.client("sts")

        if external_id:
            assume_role_response = client.assume_role(
                RoleArn=role_arn,
                RoleSessionName=session_name,
                DurationSeconds=session_duration,
                ExternalId=external_id,
            )
        else:
            assume_role_response = client.assume_role(
                RoleArn=role_arn,
                RoleSessionName=session_name,
                DurationSeconds=session_duration,
            )

        return assume_role_response["Credentials"]
    except botocore.exceptions.ClientError as ex:
        # Scrub error message for any internal account info leaks
        if "AccessDenied" in ex.response["Error"]["Code"]:
            ex.response["Error"][
                "Message"
            ] = "Lambda does not have permission to assume the IAM role."
        else:
            ex.response["Error"]["Message"] = "InternalError"
            ex.response["Error"]["Code"] = "InternalError"
            logger.exception(ex)
        raise ex


def build_role_arn(session, role_name, account_id=None):
    account_info = get_account_info(session)
    if not account_id:
        role_arn = "arn:aws:iam::" + account_info["account"] + ":role/" + role_name
        return role_arn
    else:
        role_arn = "arn:aws:iam::" + account_id + ":role/" + role_name
        return role_arn


def get_account_info(session):
    try:
        client = session.client("sts")
        response = client.get_caller_identity()

        account_info = {"region": session.region_name, "account": response["Account"]}

        return account_info
    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def get_boto_session(credentials):
    try:
        return boto3.session.Session(
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
        )
    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def get_ct_management_session(session):
    ct_mgmt_account = get_ssm_parameter_value(session, SSM_PARAM_ACCOUNT_CT_MANAGEMENT_ACCOUNT_ID)
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


def get_log_archive_session(session):
    log_archive_account = get_ssm_parameter_value(session, SSM_PARAM_ACCOUNT_LOG_ARCHIVE_ACCOUNT_ID)
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


def get_ct_product_id(session, ct_management_session):
    try:
        client = ct_management_session.client("servicecatalog")
        sc_product_name = get_ssm_parameter_value(session, SSM_PARAM_SC_PRODUCT_NAME)
        logger.info("Getting product ID for " + sc_product_name)

        response = client.describe_product_as_admin(Name=sc_product_name)
        product_id = response["ProductViewDetail"]["ProductViewSummary"]["ProductId"]
        logger.info(product_id)
        return product_id

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def get_ct_provisioning_artifact_id(session, ct_management_session):
    try:
        client = ct_management_session.client("servicecatalog")
        sc_product_name = get_ssm_parameter_value(session, SSM_PARAM_SC_PRODUCT_NAME)
        logger.info("Getting provisioning artifact ID for " + sc_product_name)

        response = client.describe_product_as_admin(Name=sc_product_name)
        provisioning_artifacts = response["ProvisioningArtifactSummaries"]
        for pa in provisioning_artifacts:
            if ct_provisioning_artifact_is_active(
                    session, ct_management_session, pa["Id"]
            ):
                logger.info("Using provisioning artifact ID: " + pa["Id"])
                return pa["Id"]

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def ct_provisioning_artifact_is_active(session, ct_management_session, artifact_id):
    try:
        client = ct_management_session.client("servicecatalog")
        sc_product_name = get_ssm_parameter_value(session, SSM_PARAM_SC_PRODUCT_NAME)
        logger.info("Checking provisioning artifact ID " + artifact_id)

        response = client.describe_provisioning_artifact(
            ProductName=sc_product_name, ProvisioningArtifactId=artifact_id
        )
        provisioning_artifact = response["ProvisioningArtifactDetail"]
        if provisioning_artifact["Active"]:
            logger.info(provisioning_artifact["Id"] + " is active")
            return True
        else:
            logger.info(provisioning_artifact["Id"] + " is NOT active")
            return False

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def product_provisioning_in_progress(ct_management_session, product_id):
    try:
        client = ct_management_session.client("servicecatalog")

        logger.info("Checking for product provisioning in progress")

        response = client.scan_provisioned_products(
            AccessLevelFilter={"Key": "Account", "Value": "self"}
        )

        for p in response["ProvisionedProducts"]:
            if p["ProductId"] == product_id:
                logger.info("Identified CT Product - " + p["Id"])
                if p["Status"] in ["UNDER_CHANGE", "PLAN_IN_PROGRESS"]:
                    logger.info("Product provisioning in Progress")
                    return True
        logger.info("No product provisioning in Progress")
        return False

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def build_sqs_url(session, queue_name):
    try:
        account_info = get_account_info(session)
        url = (
                "https://sqs."
                + account_info["region"]
                + ".amazonaws.com/"
                + account_info["account"]
                + "/"
                + queue_name
        )
        return url

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def receive_sqs_message(session, sqs_queue):
    try:
        client = session.client("sqs")
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

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def get_org_account_emails(session):
    try:
        client = session.client("organizations")
        logger.info("Listing accounts in the Organization")

        response = client.list_accounts()
        accounts = response["Accounts"]

        logger.info(accounts)

        account_emails = []

        for a in accounts:
            account_emails.append(a["Email"])

        logger.info("Account emails: " + str(account_emails))
        return account_emails

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def get_org_account_names(session):
    try:
        client = session.client("organizations")
        logger.info("Listing accounts in the Organization")

        response = client.list_accounts()
        accounts = response["Accounts"]

        logger.info(accounts)

        account_names = []

        for a in accounts:
            account_names.append(a["Name"])

        logger.info("Account Names: " + str(account_names))
        return account_names

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def get_org_ou_names(session):
    try:
        client = session.client("organizations")
        logger.info("Listing roots in the Organization")

        response = client.list_roots()
        root_id = response["Roots"][0]["Id"]

        logger.info(root_id)
        logger.info("Listing OUs for Root " + root_id)

        response = client.list_organizational_units_for_parent(ParentId=root_id)
        ous = response["OrganizationalUnits"]

        logger.info(ous)

        ou_names = []

        for o in ous:
            ou_names.append(o["Name"])

        logger.info("OU Names: " + str(ou_names))
        return ou_names

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def delete_sqs_message(session, message):
    try:
        client = session.client("sqs")
        sqs_queue = get_ssm_parameter_value(session, SSM_PARAM_ACCOUNT_REQUEST_QUEUE)
        receipt_handle = message["ReceiptHandle"]
        logger.info("Deleting SQS message with handle " + receipt_handle)
        response = client.delete_message(
            QueueUrl=build_sqs_url(session, sqs_queue), ReceiptHandle=receipt_handle
        )
        logger.info(response)
        return response

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def unmarshal_ddb_item(low_level_data):
    try:
        # To go from low-level format to python

        deserializer = boto3.dynamodb.types.TypeDeserializer()
        python_data = {
            k: deserializer.deserialize(v) for k, v in low_level_data.items()
        }
        return python_data

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def send_sqs_message(session, sqs_url, message):
    try:
        sqs = session.client("sqs")
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

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def invoke_lambda(session, function_name, payload):
    try:
        client = session.client("lambda")
        logger.info("Invoking AFT Account Provisioning Framework Lambda")
        response = client.invoke(
            FunctionName=function_name,
            InvocationType="Event",
            LogType="Tail",
            Payload=payload,
        )
        logger.info(response)
        return response

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def get_org_accounts(session):
    try:
        accounts = []
        client = session.client("organizations")
        logger.info("Listing accounts for the org")
        paginator = client.get_paginator('list_accounts')
        page_iterator = paginator.paginate()
        for page in page_iterator:
            accounts.extend(page['Accounts'])
        return accounts

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def get_account_email_from_id(ct_management_session, id):
    try:
        accounts = get_org_accounts(ct_management_session)
        logger.info("Getting account email for account id " + id)
        for a in accounts:
            if a["Id"] == id:
                email = a["Email"]
                logger.info("Account email: " + email)
                return email
        return None

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def build_sfn_arn(session, sfn_name):
    account_info = get_account_info(session)
    sfn_arn = (
            "arn:aws:states:"
            + account_info["region"]
            + ":"
            + account_info["account"]
            + ":stateMachine:"
            + sfn_name
    )
    return sfn_arn


def invoke_step_function(session, sfn_name, input):
    try:
        client = session.client("stepfunctions")
        sfn_arn = build_sfn_arn(session, sfn_name)
        input = json.dumps(input)
        logger.info("Starting SFN execution of " + sfn_arn)
        response = client.start_execution(stateMachineArn=sfn_arn, input=input)
        logger.info(response)
        return response

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def is_controltower_event(event):
    try:
        if "source" in event.keys():
            if event["source"] == "aws.controltower":
                logger.info("Event is Control Tower event")
                return True
            else:
                logger.info("Event is NOT Control Tower event")
                return False
        return False
    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def is_aft_supported_controltower_event(event):
    try:
        supported_events = ["CreateManagedAccount", "UpdateManagedAccount"]
        if event["detail"]["eventName"] in supported_events:
            logger.info("Control Tower Event is supported")
            return True
        else:
            logger.info("Control Tower Event is NOT supported")
            return False
    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def send_sns_message(session, topic, message, subject):
    try:
        logger.info("Sending SNS Message")
        client = session.client("sns")

        response = client.publish(TopicArn=topic, Message=message, Subject=subject)

        logger.info(response)
        return response

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def tag_org_resource(
        ct_management_session, resource, tags, rollback=False):
    try:
        client = ct_management_session.client("organizations")
        if rollback:
            current_tags = client.list_tags_for_resource(ResourceId=resource)

        response = client.tag_resource(ResourceId=resource, Tags=tags)

        if rollback:
            client.untag_resource(ResourceId=resource, TagKeys=[key for key in tags.keys()])
            client.tag_resource(ResourceId=resource, Tags=current_tags)

        logger.info(response)
        return response

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def get_all_aft_account_ids(session):
    try:
        table_name = get_ssm_parameter_value(session, SSM_PARAM_AFT_DDB_META_TABLE)
        aft_account_ids = []
        dynamodb = session.resource('dynamodb')
        table = dynamodb.Table(table_name)
        logger.info("Scanning DynamoDB table: " + table_name)
        response = table.scan(
            AttributesToGet=[
                'id',
            ]
        )
        logger.info(response)
        for i in response['Items']:
            aft_account_ids.append(i['id'])
        if len(aft_account_ids) > 0:
            return aft_account_ids
        else:
            return None

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def get_account_ids_in_ous(session, ou_names: list):
    try:
        client = session.client("organizations")
        logger.info("Getting Account IDs in the following OUs: " + str(ou_names))
        ou_ids = []
        account_ids = []
        for n in ou_names:
            ou_ids.append(get_org_ou_id(session, n))
        logger.info("OU IDs: " + str(ou_ids))
        for ou_id in ou_ids:
            if ou_id is not None:
                logger.info("Listing accounts in the OU ID " + ou_id)

                response = client.list_children(
                    ParentId=ou_id,
                    ChildType='ACCOUNT'
                )

                logger.info(response)

                for a in response['Children']:
                    account_ids.append(a["Id"])
            else:
                logger.info("OUs in " + str(ou_names) + " was not found")
        logger.info("Account IDs: " + str(account_ids))
        if len(account_ids) > 0:
            return account_ids
        else:
            return None

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def get_org_ou_id(session, ou_name):
    try:
        client = session.client("organizations")
        logger.info("Listing Org Roots")
        response = client.list_roots(MaxResults=1)
        logger.info(response)
        root_id = response['Roots'][0]['Id']
        logger.info("Root ID is " + root_id)

        logger.info("Listing OUs in the Organization")

        response = client.list_organizational_units_for_parent(
            ParentId=root_id
        )
        logger.info(response)

        for ou in response['OrganizationalUnits']:
            if ou['Name'] == ou_name:
                logger.info("OU ID for " + ou_name + " is " + ou['Id'])
                return ou['Id']

        return None

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def get_accounts_by_tags(aft_mgmt_session, ct_mgmt_session, tags: list):
    try:
        logger.info("Getting Account with tags - " + str(tags))
        # Get all AFT Managed Accounts
        all_accounts = get_all_aft_account_ids(aft_mgmt_session)
        matched_accounts = []
        client = ct_mgmt_session.client("organizations")
        # Loop through AFT accounts, requesting tags
        for a in all_accounts:
            account_tags = {}
            response = client.list_tags_for_resource(
                ResourceId=a
            )
            # Format tags as a dictionary rather than a list
            for t in response['Tags']:
                account_tags[t['Key']] = t['Value']
            logger.info("Account tags for " + a + ": " + str(account_tags))
            counter = 0
            # Loop through tag filter. Append account to matched_accounts if all tags in filter match/ are present
            for x in tags:
                for k, v in x.items():
                    if k in account_tags.keys():
                        if account_tags[k] == v:
                            counter += 1
                            if counter == len(tags):
                                logger.info("Account " + a + " MATCHED with tags " + str(tags))
                                matched_accounts.append(a)
        logger.info(matched_accounts)
        if len(matched_accounts) > 0:
            return matched_accounts
        else:
            return None

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise
