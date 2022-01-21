{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AWSBucketPermissionsCheck",
            "Effect": "Allow",
            "Principal": {
                "Service": [
                    "cloudtrail.amazonaws.com",
                    "vpc-flow-logs.amazonaws.com",
                    "delivery.logs.amazonaws.com"
                ]
            },
            "Action": [
                "s3:ListBucket",
                "s3:GetBucketLocation",
                "s3:GetBucketAcl"
            ],
            "Resource": "${aws_s3_bucket_aft_logging_bucket_arn}"
        },
        {
            "Sid": "AWSBucketPermissionsCheck-AuditAcct",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:ListBucket",
                "s3:GetBucketLocation",
                "s3:GetBucketAcl"
            ],
            "Resource": "${aws_s3_bucket_aft_logging_bucket_arn}",
            "Condition": {
                "StringEquals": {
                    "aws:PrincipalOrgID": "${data_aws_organizations_organization_aft_organization_id}"
                }
            }
        },
        {
            "Sid": "Allow PutObject",
            "Effect": "Allow",
            "Principal": {
                "Service": [
                    "cloudtrail.amazonaws.com",
                    "delivery.logs.amazonaws.com",
                    "vpc-flow-logs.amazonaws.com"
                ]
            },
            "Action": "s3:PutObject",
            "Resource": [
                "${aws_s3_bucket_aft_logging_bucket_arn}/AWSLogs*",
                "${aws_s3_bucket_aft_logging_bucket_arn}/*",
                "${aws_s3_bucket_aft_logging_bucket_arn}"
            ]
        },
        {
            "Sid": "Deny non-HTTPS access",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:*",
            "Resource": "${aws_s3_bucket_aft_logging_bucket_arn}/*",
            "Condition": {
                "Bool": {
                    "aws:SecureTransport": "false"
                }
            }
        }
    ]
}
