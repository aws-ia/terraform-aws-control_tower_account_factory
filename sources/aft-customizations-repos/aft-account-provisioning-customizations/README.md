# AFT Account Provisioning Customizations Customizations

## Problem Statement

AFT provides flexibility to customize the provisioning process for new accounts and integrate with systems prior to the account customization stage.

While the customization stage does include integrations for pre- and post- customization steps, the Account Provisioning standard allows for further integration by using an AWS Step Functions State Machine to integrate with additional environments.

Using this state machine integration, customers may define Account Provisioning Customizations steps as:

* Lambda functions in the language of their choice
* ECS or Fargate Tasks using docker containers
* AWS Step Functions Activities using custom workers, hosted either in AWS or on-prem
* Amazon SNS or SQS integrations to decoupled consumer-based applications

## Example Payload

```
{
  "account_request": {
    "supported_regions": "",
    "account_tags": {
      "Key": "Value",
    },
    "custom_fields": "{}",
    "id": "Account Email",
    "control_tower_parameters": {
      "AccountEmail": "",
      "ManagedOrganizationalUnit": "Sandbox",
      "AccountName": "sandbox03"
    },
    "customer_baselines": [],
    "operation": "create"
  },
  "control_tower_event": {},
  "account_info": {
    "account": {
      "id": "",
      "type": "account",
      "email": "",
      "name": "sandbox03",
      "method": "CREATED",
      "joined_date": "2021-06-15 13:57:35.129000+00:00",
      "status": "ACTIVE",
      "parent_id": "",
      "parent_type": "ORGANIZATIONAL_UNIT",
      "org_name": "Sandbox",
      "vendor": "aws"
    }
  },
  "persist_metadata": {
    "StatusCode": 200
  },
  "role": {
    "Arn": "arn:aws:iam:::role/AWSAFTExecution"
  },
  "account_tags": {
    "StatusCode": 200
  }
}
```
