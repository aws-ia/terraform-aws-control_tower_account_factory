{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "sns:Publish*",
            "Resource": "arn:${data_aws_partition_current_partition}:sns:${data_aws_region_aft-management_name}:${data_aws_caller_identity_aft-management_account_id}:aft-*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "lambda:InvokeFunction"
            ],
            "Resource": [
                "arn:${data_aws_partition_current_partition}:lambda:${data_aws_region_aft-management_name}:${data_aws_caller_identity_aft-management_account_id}:function:aft-*"
            ]
        }
    ]
}
