# AWS AFT CORE - prebaseline Pipeline


## Description

The prebaseline pipeline (referred to canonically as the 'prebaseline module') deploys an AWS Step Function which orchestrates the prebaselining of a newly vended account, or the update of an existing account.

## prebaseline Tasks

* Validate Request
* Get Account Info
* Persist Account Metadata
* Create / Ensure AFT Execution Role exists
* Apply Account-Level Tags
* Notify Prebaseline Success / Error

## Validate Request

The Validate Request function uses a JSON schema to check the incoming event has at least the minimum required fields.

For example:

```json
{
    "account_request": { #account_request_object }, <-- must be present
    "contol_tower_event": { }, <-- must be present, allow null
}
```

For more detailed information to the request schema, view the full schema here: ```modules/prebaseline/lambda/prebaseline/schema/request_schema.json```

## Get Account Info

Each request which reaches the prebaseline pipeline will require the pipeline populate account information.

AFT Account Requests are keyed by email id, while account operations using the Organizations api are keyed by account id.

The least expensive way to find this data would be in the payload, in the ```control_tower_event``` object if it is present.

The next option would be to find the data in the ```aft-account-metadata``` table, where the ```persist-metadata``` prebaseline step populates account metadata.

The most expensive option, if none of these other sources contains account information, is to query the Organizations api and search for the account by email -- this involves listing all accounts in the organization, performing a describe_account for each, and then mapping to the correct email address.

View the implementation for this task here: ```modules/prebaseline/lambda/prebaseline/lambda.py#get_account_info()```

## Create AFT Execution Role

For a newly vended account, we must create a role in the vended account which can be assumed by the AFT solution.

We are piggybacking off of Control Tower's cross-account roles to do this.

The authentication chain to create the AWSAFTExecutionRole is as follows:

```
Prebaseline Lambda Execution Role -> 
AWSAFTExecutionRole in Control Tower Management Account (created by initial AFT Deployment) -> 
AWSControlTowerExecution in Vended Account
```

Each time the pipeline runs, we will perform this assume role chain in order to verify the role exists.

If it cannot be found, we attempt to re-create the role.

View the implementation for this task here: ```modules/prebaseline/lambda/prebaseline/lambda.py#create_aft_execution_role()```

## Apply Account-Level Tags

To apply account-level tags using the organizations API, we first assume the AWSAFTExecutionRole in the Control Tower Management account.

We then run organizations.tag_resource on the account ID given the list of tags from the request.

View the implementation for this task here: ```modules/prebaseline/lambda/prebaseline/lambda.py#tag_account()```

## Notify Prebaseline Success / Error

If all steps succeed, we send a success notification to the AFT Notifications SNS topic.

If any step encounters an uncaught exception, we send a notification to the AFT Failure Notifications SNS topic, and then fail the state machine.