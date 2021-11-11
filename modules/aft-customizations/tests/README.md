# Test cases for terraform-aws-aft-core module


## Unit tests

Unit tests are designed to validate the terraform changes to the module and its sub-modules. Plan is generated against the examples/complete and analyzed for various scenarios

### AFT-U01: Modules, Number of child-modules, resource count

In this test case you validated expected number of resources as follows:

| module                                                |   child-modules |   resources |
|-------------------------------------------------------|-----------------|-------------|
| module.aft                                            |               4 |           0 |
| module.aft.module.aws_lambda_layer                    |               0 |           1 |
| module.aft.module.ssm_outputs                         |               0 |          22 |
| module.aft.module.request_processor                   |               0 |          52 |
| module.aft.module.aft-account-provisioning-framework  |               0 |          20 |


### AFT-U02: Resources are analyzed by resource_type, action and category

In this test case you validated expected number of resources as follows:

#### By resource-type

| Type                            |   Count |
|---------------------------------|---------|
| aws_lambda_layer_version        |       1 |
| aws_cloudwatch_log_group        |      12 |
| aws_iam_role                    |       8 |
| aws_iam_role_policy             |       8 |
| aws_iam_role_policy_attachment  |       6 |
| aws_lambda_function             |      12 |
| aws_sfn_state_machine           |       1 |
| aws_cloudwatch_event_bus        |       1 |
| aws_cloudwatch_event_permission |       1 |
| aws_cloudwatch_event_rule       |       3 |
| aws_cloudwatch_event_target     |       4 |
| aws_dynamodb_table              |       4 |
| aws_kms_alias                   |       1 |
| aws_kms_key                     |       1 |
| aws_lambda_event_source_mapping |       2 |
| aws_lambda_permission           |       3 |
| aws_sns_topic                   |       2 |
| aws_sqs_queue                   |       2 |
| time_sleep                      |       1 |
| aws_ssm_parameter               |      22 |

#### By category

| Type          |   Count |
|---------------|---------|
| lambda        |      18 |
| cloudwatch    |      21 |
| iam           |      22 |
| event         |      11 |
| db            |       4 |
| ssm           |      22 |

#### By action

| Type   |   Count |
|--------|---------|
| create |      95 |

### AFT-U03: Naming std violations

We expect the naming violations are 0 for each category. The violations in the codebase are reported  as follows:

| ViolationType   |   Count |
|-----------------|---------|
| GN02            |       0 |
| RN01            |       0 |

## Integration tests

Once you apply the terraform changes we verify and test the deployed resources in this stage.
