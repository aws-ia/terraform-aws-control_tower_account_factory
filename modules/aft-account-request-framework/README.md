# request-processor

This module deploys the components responsible for processing an account request, with either account vending method (`account_vending_method`). Functionality includes:
- Creating an audit for account requests/updates in the DynamoDB audit table
- Decision logic on whether a Service Catalog/Control Tower API call is needed, or, with the Organizations vending method, an execution of the `aft-organizations-account-provisioning` Step Function
- Queueing account create and update requests by leveraging an SQS queue. The account request processor Lambda runs every 5 minutes and takes one request per run. With `service_catalog`, it provisions or updates the account through Service Catalog. With `organizations`, it starts an execution of the `aft-organizations-account-provisioning` Step Function.
- With `organizations` only: the `aft-organizations-account-provisioning` Step Function and its Lambdas, which create the account with AWS Organizations, move it into its managed OU, wait for Control Tower to enroll it, compare its baselines and controls with its OU's, and publish an `aft.organizations` lifecycle event to the AFT event bus
- Forwarding and storing Control Tower events from the ct-management account, and the `aft.organizations` events, into a DynamoDB table
- Triggering Step Functions based on a request payload

![Request Processor](../../images/account_request.png)

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.6.1, < 2.0.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 4.9.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 4.9.0 |
| <a name="provider_aws.ct_management"></a> [aws.ct\_management](#provider\_aws.ct\_management) | >= 4.9.0 |
| <a name="provider_time"></a> [time](#provider\_time) | n/a |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_backup_plan.aft_controltower_backup_plan](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/backup_plan) | resource |
| [aws_backup_selection.aft_controltower_backup_selection](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/backup_selection) | resource |
| [aws_backup_vault.aft_controltower_backup_vault](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/backup_vault) | resource |
| [aws_cloudwatch_event_bus.aft_from_ct_management](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_bus) | resource |
| [aws_cloudwatch_event_permission.control_tower_management_account](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_permission) | resource |
| [aws_cloudwatch_event_rule.aft_account_request_processor](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_rule) | resource |
| [aws_cloudwatch_event_rule.aft_control_tower_events](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_rule) | resource |
| [aws_cloudwatch_event_rule.aft_controltower_event_trigger](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_rule) | resource |
| [aws_cloudwatch_event_rule.aft_organizations_account_provisioning_timed_out](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_rule) | resource |
| [aws_cloudwatch_event_rule.aft_organizations_lifecycle_events](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_rule) | resource |
| [aws_cloudwatch_event_target.aft_account_request_processor](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_target) | resource |
| [aws_cloudwatch_event_target.aft_controltower_event_logger](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_target) | resource |
| [aws_cloudwatch_event_target.aft_invoke_aft_account_provisioning_framework](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_target) | resource |
| [aws_cloudwatch_event_target.aft_management_event_bus](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_target) | resource |
| [aws_cloudwatch_event_target.aft_organizations_account_provisioning_timed_out](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_target) | resource |
| [aws_cloudwatch_event_target.aft_organizations_event_logger](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_target) | resource |
| [aws_cloudwatch_event_target.aft_organizations_invoke_provisioning_framework](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_target) | resource |
| [aws_cloudwatch_log_group.aft_account_request_action_trigger](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group) | resource |
| [aws_cloudwatch_log_group.aft_account_request_audit_trigger](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group) | resource |
| [aws_cloudwatch_log_group.aft_account_request_processor](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group) | resource |
| [aws_cloudwatch_log_group.aft_cleanup_resources](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group) | resource |
| [aws_cloudwatch_log_group.aft_controltower_event_logger](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group) | resource |
| [aws_cloudwatch_log_group.aft_invoke_aft_account_provisioning_framework](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group) | resource |
| [aws_cloudwatch_log_group.aft_organizations_account_provisioning](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group) | resource |
| [aws_default_security_group.aft_vpc_default_sg](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/default_security_group) | resource |
| [aws_dynamodb_table.aft_controltower_events](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table) | resource |
| [aws_dynamodb_table.aft_customizations_audit](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table) | resource |
| [aws_dynamodb_table.aft_request](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table) | resource |
| [aws_dynamodb_table.aft_request_audit](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table) | resource |
| [aws_dynamodb_table.aft_request_metadata](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table) | resource |
| [aws_eip.aft-vpc-natgw-01](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eip) | resource |
| [aws_eip.aft-vpc-natgw-02](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eip) | resource |
| [aws_iam_role.aft_account_request_action_trigger](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.aft_account_request_audit_trigger](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.aft_account_request_processor](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.aft_aws_backup](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.aft_cleanup_resources](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.aft_control_tower_events](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.aft_controltower_event_logger](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.aft_invoke_aft_account_provisioning_framework](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.aft_organizations_account_provisioning_lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.aft_organizations_account_provisioning_sfn](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role_policy.aft_account_request_action_trigger](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy.aft_account_request_audit_trigger](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy.aft_account_request_processor](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy.aft_account_request_processor_organizations](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy.aft_cleanup_resources](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy.aft_controltower_event_logger](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy.aft_invoke_aft_account_provisioning_framework](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy.aft_organizations_account_provisioning_lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy.aft_organizations_account_provisioning_sfn_invoke](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy.control_tower_events](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy_attachment.account_request_processor](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.aft_account_request_action_trigger](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.aft_account_request_audit_trigger](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.aft_aws_backup_service_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.aft_cleanup_resources](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.aft_controltower_event_logger](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.aft_invoke_aft_account_provisioning_framework](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.aft_organizations_account_provisioning_lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_internet_gateway.aft-vpc-igw](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/internet_gateway) | resource |
| [aws_kms_alias.aft](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_alias) | resource |
| [aws_kms_key.aft](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key) | resource |
| [aws_lambda_event_source_mapping.aft_account_request_action_trigger](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_event_source_mapping) | resource |
| [aws_lambda_event_source_mapping.aft_account_request_audit_trigger](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_event_source_mapping) | resource |
| [aws_lambda_function.aft_account_request_action_trigger](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function) | resource |
| [aws_lambda_function.aft_account_request_audit_trigger](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function) | resource |
| [aws_lambda_function.aft_account_request_processor](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function) | resource |
| [aws_lambda_function.aft_cleanup_resources](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function) | resource |
| [aws_lambda_function.aft_controltower_event_logger](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function) | resource |
| [aws_lambda_function.aft_invoke_aft_account_provisioning_framework](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function) | resource |
| [aws_lambda_function.aft_organizations_account_provisioning](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function) | resource |
| [aws_lambda_permission.aft_account_request_processor](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_permission) | resource |
| [aws_lambda_permission.aft_controltower_event_logger](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_permission) | resource |
| [aws_lambda_permission.aft_invoke_aft_account_provisioning_framework](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_permission) | resource |
| [aws_lambda_permission.aft_organizations_account_provisioning_timed_out](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_permission) | resource |
| [aws_lambda_permission.aft_organizations_event_logger](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_permission) | resource |
| [aws_lambda_permission.aft_organizations_invoke_provisioning_framework](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_permission) | resource |
| [aws_nat_gateway.aft-vpc-natgw-01](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/nat_gateway) | resource |
| [aws_nat_gateway.aft-vpc-natgw-02](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/nat_gateway) | resource |
| [aws_route_table.aft_vpc_private_subnet_01](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route_table) | resource |
| [aws_route_table.aft_vpc_private_subnet_02](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route_table) | resource |
| [aws_route_table.aft_vpc_public_subnet_01](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route_table) | resource |
| [aws_route_table_association.aft_vpc_private_subnet_01](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route_table_association) | resource |
| [aws_route_table_association.aft_vpc_private_subnet_02](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route_table_association) | resource |
| [aws_route_table_association.aft_vpc_public_subnet_01](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route_table_association) | resource |
| [aws_route_table_association.aft_vpc_public_subnet_02](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route_table_association) | resource |
| [aws_security_group.aft_vpc_default_sg](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group) | resource |
| [aws_security_group.aft_vpc_endpoint_sg](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group) | resource |
| [aws_sfn_state_machine.aft_organizations_account_provisioning](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sfn_state_machine) | resource |
| [aws_sns_topic.aft_failure_notifications](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic) | resource |
| [aws_sns_topic.aft_notifications](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic) | resource |
| [aws_sqs_queue.aft_account_request](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sqs_queue) | resource |
| [aws_sqs_queue.aft_account_request_dlq](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sqs_queue) | resource |
| [aws_subnet.aft_vpc_private_subnet_01](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/subnet) | resource |
| [aws_subnet.aft_vpc_private_subnet_02](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/subnet) | resource |
| [aws_subnet.aft_vpc_public_subnet_01](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/subnet) | resource |
| [aws_subnet.aft_vpc_public_subnet_02](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/subnet) | resource |
| [aws_vpc.aft_vpc](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc) | resource |
| [aws_vpc_endpoint.codebuild](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_endpoint) | resource |
| [aws_vpc_endpoint.codecommit](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_endpoint) | resource |
| [aws_vpc_endpoint.codepipeline](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_endpoint) | resource |
| [aws_vpc_endpoint.dynamodb](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_endpoint) | resource |
| [aws_vpc_endpoint.events](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_endpoint) | resource |
| [aws_vpc_endpoint.git-codecommit](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_endpoint) | resource |
| [aws_vpc_endpoint.kms](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_endpoint) | resource |
| [aws_vpc_endpoint.lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_endpoint) | resource |
| [aws_vpc_endpoint.logs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_endpoint) | resource |
| [aws_vpc_endpoint.organizations](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_endpoint) | resource |
| [aws_vpc_endpoint.s3](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_endpoint) | resource |
| [aws_vpc_endpoint.servicecatalog](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_endpoint) | resource |
| [aws_vpc_endpoint.sns](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_endpoint) | resource |
| [aws_vpc_endpoint.sqs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_endpoint) | resource |
| [aws_vpc_endpoint.ssm](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_endpoint) | resource |
| [aws_vpc_endpoint.states](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_endpoint) | resource |
| [aws_vpc_endpoint.sts](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc_endpoint) | resource |
| [time_sleep.wait_60_seconds](https://registry.terraform.io/providers/hashicorp/time/latest/docs/resources/sleep) | resource |
| [aws_availability_zones.available](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/availability_zones) | data source |
| [aws_caller_identity.aft-management](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |
| [aws_caller_identity.ct-management](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |
| [aws_iam_policy.AWSLambdaBasicExecutionRole](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy) | data source |
| [aws_iam_policy.AWSLambdaVPCAccessExecutionRole](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy) | data source |
| [aws_partition.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/partition) | data source |
| [aws_region.aft-management](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/region) | data source |
| [aws_route_tables.aft_private_route_tables](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/route_tables) | data source |
| [aws_route_tables.aft_public_route_tables](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/route_tables) | data source |
| [aws_subnets.codebuild](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/subnets) | data source |
| [aws_subnets.codecommit](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/subnets) | data source |
| [aws_subnets.codepipeline](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/subnets) | data source |
| [aws_subnets.events](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/subnets) | data source |
| [aws_subnets.git-codecommit](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/subnets) | data source |
| [aws_subnets.kms](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/subnets) | data source |
| [aws_subnets.lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/subnets) | data source |
| [aws_subnets.logs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/subnets) | data source |
| [aws_subnets.organizations](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/subnets) | data source |
| [aws_subnets.servicecatalog](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/subnets) | data source |
| [aws_subnets.sns](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/subnets) | data source |
| [aws_subnets.sqs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/subnets) | data source |
| [aws_subnets.ssm](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/subnets) | data source |
| [aws_subnets.states](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/subnets) | data source |
| [aws_subnets.sts](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/subnets) | data source |
| [aws_vpc.aft](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/vpc) | data source |
| [aws_vpc_endpoint_service.codebuild](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/vpc_endpoint_service) | data source |
| [aws_vpc_endpoint_service.codecommit](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/vpc_endpoint_service) | data source |
| [aws_vpc_endpoint_service.codepipeline](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/vpc_endpoint_service) | data source |
| [aws_vpc_endpoint_service.events](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/vpc_endpoint_service) | data source |
| [aws_vpc_endpoint_service.git-codecommit](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/vpc_endpoint_service) | data source |
| [aws_vpc_endpoint_service.kms](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/vpc_endpoint_service) | data source |
| [aws_vpc_endpoint_service.lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/vpc_endpoint_service) | data source |
| [aws_vpc_endpoint_service.logs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/vpc_endpoint_service) | data source |
| [aws_vpc_endpoint_service.organizations](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/vpc_endpoint_service) | data source |
| [aws_vpc_endpoint_service.servicecatalog](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/vpc_endpoint_service) | data source |
| [aws_vpc_endpoint_service.sns](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/vpc_endpoint_service) | data source |
| [aws_vpc_endpoint_service.sqs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/vpc_endpoint_service) | data source |
| [aws_vpc_endpoint_service.ssm](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/vpc_endpoint_service) | data source |
| [aws_vpc_endpoint_service.states](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/vpc_endpoint_service) | data source |
| [aws_vpc_endpoint_service.sts](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/vpc_endpoint_service) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_account_factory_product_name"></a> [account\_factory\_product\_name](#input\_account\_factory\_product\_name) | n/a | `string` | n/a | yes |
| <a name="input_account_vending_method"></a> [account\_vending\_method](#input\_account\_vending\_method) | Method AFT uses to vend accounts (service\_catalog or organizations). Service Catalog resources are only created for service\_catalog. | `string` | `"service_catalog"` | no |
| <a name="input_aft_account_provisioning_framework_sfn_name"></a> [aft\_account\_provisioning\_framework\_sfn\_name](#input\_aft\_account\_provisioning\_framework\_sfn\_name) | n/a | `string` | n/a | yes |
| <a name="input_aft_common_layer_arn"></a> [aft\_common\_layer\_arn](#input\_aft\_common\_layer\_arn) | n/a | `string` | n/a | yes |
| <a name="input_aft_customer_private_subnets"></a> [aft\_customer\_private\_subnets](#input\_aft\_customer\_private\_subnets) | n/a | `list(string)` | n/a | yes |
| <a name="input_aft_customer_vpc_id"></a> [aft\_customer\_vpc\_id](#input\_aft\_customer\_vpc\_id) | n/a | `string` | n/a | yes |
| <a name="input_aft_enable_vpc"></a> [aft\_enable\_vpc](#input\_aft\_enable\_vpc) | n/a | `bool` | n/a | yes |
| <a name="input_aft_organizations_account_provisioning_sfn_name"></a> [aft\_organizations\_account\_provisioning\_sfn\_name](#input\_aft\_organizations\_account\_provisioning\_sfn\_name) | Name of the Step Function that creates and updates accounts for the Organizations vending method. | `string` | n/a | yes |
| <a name="input_aft_organizations_provisioning_timeout_seconds"></a> [aft\_organizations\_provisioning\_timeout\_seconds](#input\_aft\_organizations\_provisioning\_timeout\_seconds) | TimeoutSeconds of the organizations account-provisioning Step Function; the baseline poll ends its control wait before it. | `number` | `7200` | no |
| <a name="input_aft_vpc_cidr"></a> [aft\_vpc\_cidr](#input\_aft\_vpc\_cidr) | n/a | `string` | `null` | no |
| <a name="input_aft_vpc_endpoints"></a> [aft\_vpc\_endpoints](#input\_aft\_vpc\_endpoints) | n/a | `bool` | `null` | no |
| <a name="input_aft_vpc_private_subnet_01_cidr"></a> [aft\_vpc\_private\_subnet\_01\_cidr](#input\_aft\_vpc\_private\_subnet\_01\_cidr) | n/a | `string` | `null` | no |
| <a name="input_aft_vpc_private_subnet_02_cidr"></a> [aft\_vpc\_private\_subnet\_02\_cidr](#input\_aft\_vpc\_private\_subnet\_02\_cidr) | n/a | `string` | `null` | no |
| <a name="input_aft_vpc_public_subnet_01_cidr"></a> [aft\_vpc\_public\_subnet\_01\_cidr](#input\_aft\_vpc\_public\_subnet\_01\_cidr) | n/a | `string` | `null` | no |
| <a name="input_aft_vpc_public_subnet_02_cidr"></a> [aft\_vpc\_public\_subnet\_02\_cidr](#input\_aft\_vpc\_public\_subnet\_02\_cidr) | n/a | `string` | `null` | no |
| <a name="input_backup_recovery_point_retention"></a> [backup\_recovery\_point\_retention](#input\_backup\_recovery\_point\_retention) | n/a | `number` | n/a | yes |
| <a name="input_backup_schedule"></a> [backup\_schedule](#input\_backup\_schedule) | n/a | `string` | n/a | yes |
| <a name="input_cloudwatch_log_group_enable_cmk_encryption"></a> [cloudwatch\_log\_group\_enable\_cmk\_encryption](#input\_cloudwatch\_log\_group\_enable\_cmk\_encryption) | n/a | `bool` | n/a | yes |
| <a name="input_cloudwatch_log_group_retention"></a> [cloudwatch\_log\_group\_retention](#input\_cloudwatch\_log\_group\_retention) | n/a | `string` | n/a | yes |
| <a name="input_concurrent_account_factory_actions"></a> [concurrent\_account\_factory\_actions](#input\_concurrent\_account\_factory\_actions) | n/a | `number` | n/a | yes |
| <a name="input_lambda_runtime_python_version"></a> [lambda\_runtime\_python\_version](#input\_lambda\_runtime\_python\_version) | n/a | `string` | n/a | yes |
| <a name="input_request_framework_archive_hash"></a> [request\_framework\_archive\_hash](#input\_request\_framework\_archive\_hash) | n/a | `string` | n/a | yes |
| <a name="input_request_framework_archive_path"></a> [request\_framework\_archive\_path](#input\_request\_framework\_archive\_path) | n/a | `string` | n/a | yes |
| <a name="input_sns_topic_enable_cmk_encryption"></a> [sns\_topic\_enable\_cmk\_encryption](#input\_sns\_topic\_enable\_cmk\_encryption) | n/a | `bool` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_account_factory_product_name"></a> [account\_factory\_product\_name](#output\_account\_factory\_product\_name) | n/a |
| <a name="output_aft_account_provisioning_framework_sfn_name"></a> [aft\_account\_provisioning\_framework\_sfn\_name](#output\_aft\_account\_provisioning\_framework\_sfn\_name) | n/a |
| <a name="output_aft_cleanup_resources_function_name"></a> [aft\_cleanup\_resources\_function\_name](#output\_aft\_cleanup\_resources\_function\_name) | n/a |
| <a name="output_aft_failure_sns_topic_arn"></a> [aft\_failure\_sns\_topic\_arn](#output\_aft\_failure\_sns\_topic\_arn) | n/a |
| <a name="output_aft_from_ct_management_event_bus_name"></a> [aft\_from\_ct\_management\_event\_bus\_name](#output\_aft\_from\_ct\_management\_event\_bus\_name) | n/a |
| <a name="output_aft_kms_key_alias_arn"></a> [aft\_kms\_key\_alias\_arn](#output\_aft\_kms\_key\_alias\_arn) | ARN for the AFT CMK Key alias |
| <a name="output_aft_kms_key_arn"></a> [aft\_kms\_key\_arn](#output\_aft\_kms\_key\_arn) | ARN for the AFT CMK Key |
| <a name="output_aft_kms_key_id"></a> [aft\_kms\_key\_id](#output\_aft\_kms\_key\_id) | ID for the AFT CMK Key |
| <a name="output_aft_organizations_account_provisioning_sfn_name"></a> [aft\_organizations\_account\_provisioning\_sfn\_name](#output\_aft\_organizations\_account\_provisioning\_sfn\_name) | n/a |
| <a name="output_aft_sns_topic_arn"></a> [aft\_sns\_topic\_arn](#output\_aft\_sns\_topic\_arn) | n/a |
| <a name="output_aft_vpc_default_sg"></a> [aft\_vpc\_default\_sg](#output\_aft\_vpc\_default\_sg) | n/a |
| <a name="output_aft_vpc_id"></a> [aft\_vpc\_id](#output\_aft\_vpc\_id) | n/a |
| <a name="output_aft_vpc_private_subnets"></a> [aft\_vpc\_private\_subnets](#output\_aft\_vpc\_private\_subnets) | n/a |
| <a name="output_aft_vpc_public_subnets"></a> [aft\_vpc\_public\_subnets](#output\_aft\_vpc\_public\_subnets) | n/a |
| <a name="output_control_tower_event_logger_function_arn"></a> [control\_tower\_event\_logger\_function\_arn](#output\_control\_tower\_event\_logger\_function\_arn) | n/a |
| <a name="output_controltower_events_table_name"></a> [controltower\_events\_table\_name](#output\_controltower\_events\_table\_name) | n/a |
| <a name="output_customizations_audit_table_arn"></a> [customizations\_audit\_table\_arn](#output\_customizations\_audit\_table\_arn) | ARN of the AFT customizations audit DynamoDB table |
| <a name="output_customizations_audit_table_name"></a> [customizations\_audit\_table\_name](#output\_customizations\_audit\_table\_name) | Name of the AFT customizations audit DynamoDB table |
| <a name="output_failure_sns_topic_arn"></a> [failure\_sns\_topic\_arn](#output\_failure\_sns\_topic\_arn) | ARN of failure\_notifications sns topic |
| <a name="output_invoke_aft_account_provisioning_framework_function_arn"></a> [invoke\_aft\_account\_provisioning\_framework\_function\_arn](#output\_invoke\_aft\_account\_provisioning\_framework\_function\_arn) | n/a |
| <a name="output_invoke_aft_account_provisioning_framework_lambda_function_name"></a> [invoke\_aft\_account\_provisioning\_framework\_lambda\_function\_name](#output\_invoke\_aft\_account\_provisioning\_framework\_lambda\_function\_name) | n/a |
| <a name="output_request_action_trigger_function_arn"></a> [request\_action\_trigger\_function\_arn](#output\_request\_action\_trigger\_function\_arn) | n/a |
| <a name="output_request_audit_table_name"></a> [request\_audit\_table\_name](#output\_request\_audit\_table\_name) | n/a |
| <a name="output_request_audit_trigger_function_arn"></a> [request\_audit\_trigger\_function\_arn](#output\_request\_audit\_trigger\_function\_arn) | n/a |
| <a name="output_request_metadata_table_name"></a> [request\_metadata\_table\_name](#output\_request\_metadata\_table\_name) | n/a |
| <a name="output_request_processor_function_arn"></a> [request\_processor\_function\_arn](#output\_request\_processor\_function\_arn) | n/a |
| <a name="output_request_queue_name"></a> [request\_queue\_name](#output\_request\_queue\_name) | n/a |
| <a name="output_request_table_name"></a> [request\_table\_name](#output\_request\_table\_name) | n/a |
| <a name="output_sns_topic_arn"></a> [sns\_topic\_arn](#output\_sns\_topic\_arn) | ARN of aft notifications sns topic |
| <a name="output_vpc_deployment"></a> [vpc\_deployment](#output\_vpc\_deployment) | n/a |
<!-- END_TF_DOCS -->
