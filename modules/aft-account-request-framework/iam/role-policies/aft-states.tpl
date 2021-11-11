{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "states:StartExecution",
            "Resource": "${aft_account_provisioning_framework_sfn_arn}"
        },
        {
            "Effect": "Allow",
            "Action": [
                "lambda:InvokeFunction"
            ],
            "Resource": [
                "arn:aws:lambda:${data_aws_region_aft-management_name}:${data_aws_caller_identity_aft-management_account_id}:function:aft_*"
            ]
        }
    ]
}