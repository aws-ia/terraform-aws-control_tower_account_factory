# AWS AFT CORE - aft_common python module & Lambda Layer

## Description

Common framework consumed by python modules across AFT.

## Location 

The aft_common source codes is located here:

```modules/lambda_layer/aft_common_layer/python/lib/python3.8/site-packages/aft_common```

## Contents

* AWS Logger
* utils

## Logger

AWS-provided logger which replaces the standard python logging library.

Logs objects as json which is friendlier to read in CloudWatch logs.

## Utils

Utils contains the shared functions for common tasks across AFT.

Additionally, configuration elements stored in SSM are accessible through get_ssm_parameter and a number of constants at the top of the module.

Function list:

* build_role_arn
* build_sfn_arn
* build_sqs_url
* ct_provisioning_artifact_is_active
* delete_sqs_message
* get_account
* get_account_by_email
* get_account_email_from_id
* get_account_info
* get_assume_role_credentials
* get_boto_session
* get_ct_execution_session
* get_ct_management_session
* get_ct_product_id
* get_ct_provisioning_artifact_id
* get_org_account_emails
* get_org_account_names
* get_org_accounts
* get_org_ou_names
* get_ssm_parameter_value
* invoke_lambda
* invoke_step_function
* is_controltower_event
* is_aft_supported_controltower_event
* list_accounts
* product_provisioning_in_progress
* put_ddb_item
* receive_sqs_message
* send_sns_message
* send_sqs_message
* tag_org_resource
* unmarshal_ddb_item

For more information on the implementation of each of these functions, see the source here:

```modules/lambda_layer/aft_common_layer/python/lib/python3.8/site-packages/aft_common/utils.py```
