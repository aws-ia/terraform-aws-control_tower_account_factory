{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "MinimumGitLabPushMirroringPermissions",
            "Effect": "Allow",
            "Action": [
                "codecommit:GitPull",
                "codecommit:GitPush"
            ],
            "Resource": [
                "arn:${data_aws_partition_current_partition}:codecommit:${data_aws_region_aft-management_name}:${data_aws_caller_identity_aft-management_account_id}:terraform-aws-aft-pipeline-framework",
                "arn:${data_aws_partition_current_partition}:codecommit:${data_aws_region_aft-management_name}:${data_aws_caller_identity_aft-management_account_id}:terraform-aws-aft-pipeline-*"
            ]
        }
    ]
}
