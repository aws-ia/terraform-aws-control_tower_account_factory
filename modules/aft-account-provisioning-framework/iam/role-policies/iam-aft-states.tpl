{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "events:*"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": "states:StartExecution",
            "Resource": "arn:${data_aws_partition_current_partition}:states:${data_aws_region_aft-management_name}:${data_aws_caller_identity_aft-management_account_id}:stateMachine:aft-*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "lambda:InvokeFunction"
            ],
            "Resource": [
                "arn:${data_aws_partition_current_partition}:lambda:${data_aws_region_aft-management_name}:${data_aws_caller_identity_aft-management_account_id}:function:aft-*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "sns:Publish"
            ],
            "Resource": [
                "arn:${data_aws_partition_current_partition}:sns:${data_aws_region_aft-management_name}:${data_aws_caller_identity_aft-management_account_id}:aft-*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "codebuild:StartBuild",
                "codebuild:StopBuild",
                "codebuild:BatchGetBuilds"
            ],
            "Resource": [
                "arn:${data_aws_partition_current_partition}:codebuild:${data_aws_region_aft-management_name}:${data_aws_caller_identity_aft-management_account_id}:project/aft-*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "events:PutTargets",
                "events:PutRule",
                "events:DescribeRule"
            ],
            "Resource": [
                "arn:${data_aws_partition_current_partition}:events:${data_aws_region_aft-management_name}:${data_aws_caller_identity_aft-management_account_id}:rule/StepFunctionsGetEventForCodeBuildStartBuildRule"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "states:DescribeExecution"
            ],
            "Resource": [
                "arn:${data_aws_partition_current_partition}:states:${data_aws_region_aft-management_name}:${data_aws_caller_identity_aft-management_account_id}:execution:aft-*"
            ]
        }

    ]
}
