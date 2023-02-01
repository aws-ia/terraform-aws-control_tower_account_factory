{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Resource": "arn:${data_aws_partition_current_partition}:iam::*:role${var_aft_role_execution_path}${var_aft_role_execution_name}"
        },
        {
            "Effect": "Allow",
            "Action": "logs:CreateLogGroup",
            "Resource": "arn:${data_aws_partition_current_partition}:logs:${data_aws_region_aft-management_name}:${data_aws_caller_identity_aft-management_account_id}:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:${data_aws_partition_current_partition}:logs:${data_aws_region_aft-management_name}:${data_aws_caller_identity_aft-management_account_id}:log-group:/aws/lambda/*:*"
            ]
        }
    ]
}
