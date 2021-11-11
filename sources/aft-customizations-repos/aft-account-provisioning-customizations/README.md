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
      "SSOUserEmail": "",
      "AccountEmail": "",
      "SSOUserFirstName": "",
      "SSOUserLastName": "",
      "ManagedOrganizationalUnit": "Sandbox",
      "AccountName": "sandbox03"
    },
    "customer_baselines": [],
    "operation": "create"
  },
  "control_tower_event": {},
  "validated": {
    "Success": true
  },
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


## Example Function

#### Validate Request:

Source location: `modules/Account Provisioning Customizations-customizations/lambda/Account Provisioning Customizations-customizations-validate-request/lambda_function.py`

##### Description:

Compares the incoming payload to the state machine against an expected jsonschema. Returns `True` if valid, raises an exception if not.

Demonstrates the import of `aft_common` and customers can explore the `aft_utils` module for existing AFT integrations, such as role assumption or SSM parameter retrieval.

```python
import json
import os
import boto3
import jsonschema
import aft_common.aft_utils as utils
from boto3.dynamodb.conditions import Key


logger = utils.get_logger()


def validate_request(payload, logger):
    logger.info("Function Start - validate_request")
    schema_path = os.path.join(os.path.dirname(__file__), "schema/request_schema.json")
    with open(schema_path) as schema_file:
        schema_object = json.load(schema_file)
    logger.info("Schema Loaded:" + json.dumps(schema_object))
    validated = jsonschema.validate(payload, schema_object)
    if validated is None:
        logger.info("Request Validated")
        return True
    else:
        raise Exception("Failure validating request.\n{validated}")


def lambda_handler(event, context):
    logger.info("Account Provisioning Customizations Handler Start")

    payload = event['payload']
    action = event['action']

    if action == "validate":
        request_validated = validate_request(payload, logger)
        return request_validated
    else:
        raise BaseException(
            "Incorrect Command Passed to Lambda Function. Input: {action}. Expected: 'validate'"
        )

```

