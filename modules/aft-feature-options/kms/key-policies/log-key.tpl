{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Allow AWS Services to Encrypt data",
            "Effect": "Allow",
            "Principal": {
                "Service": [
                    "vpc-flow-logs.amazonaws.com",
                    "delivery.logs.amazonaws.com",
                    "cloudtrail.amazonaws.com"
                ]
            },
            "Action": [
                "kms:ReEncrypt*",
                "kms:GenerateDataKey*",
                "kms:Encrypt",
                "kms:DescribeKey",
                "kms:Decrypt"
            ],
            "Resource": "*"
        },
        {
            "Sid": "Enable IAM User Permissions",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:${data_aws_partition_current_partition}:iam::${log_archive_account_id}:root"
            },
            "Action": "kms:*",
            "Resource": "*"
        }
    ]
}
