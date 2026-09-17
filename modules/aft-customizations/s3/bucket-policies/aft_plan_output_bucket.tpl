{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowSSLRequestsOnly",
            "Action": "s3:*",
            "Effect": "Deny",
            "Resource": [
                "${aft_plan_output_bucket_arn}",
                "${aft_plan_output_bucket_arn}/*"
            ],
            "Condition": {
                "Bool": {
                     "aws:SecureTransport": "false"
                }
            },
           "Principal": "*"
        },
        {
            "Sid": "DenyWritesExceptCustomizationsCodeBuild",
            "Action": [
                "s3:PutObject",
                "s3:PutObjectAcl"
            ],
            "Effect": "Deny",
            "Resource": [
                "${aft_plan_output_bucket_arn}/*"
            ],
            "Condition": {
                "StringNotLike": {
                    "aws:PrincipalArn": "${aft_codebuild_customizations_role_arn}"
                }
            },
            "Principal": "*"
        }
    ]
}
