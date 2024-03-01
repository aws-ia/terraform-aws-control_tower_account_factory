# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
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
SSM_PARAMETER_PATH = "/aft/account-request/custom-fields/"
