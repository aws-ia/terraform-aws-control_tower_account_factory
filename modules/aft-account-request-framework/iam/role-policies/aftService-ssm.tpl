{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "ssm:GetParameter",
            "Resource": [
                "arn:aws:ssm:${data_aws_region_aft-management_name}:${data_aws_caller_identity_aft-management_account_id}:parameter/aft/*"
            ]
        }
    ]
}
