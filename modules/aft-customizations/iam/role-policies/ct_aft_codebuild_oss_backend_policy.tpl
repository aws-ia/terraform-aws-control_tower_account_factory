{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:*Item"
      ],
      "Resource": [
        "arn:aws:dynamodb:${data_aws_region_current_name}:${data_aws_caller_identity_current_account_id}:table/${data_aws_dynamo_terraform_oss_backend_table}"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:GetObjectVersion",
        "s3:GetBucketVersioning",
        "s3:List*",
        "s3:PutObjectAcl",
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::${aws_s3_bucket_aft_terraform_oss_backend_bucket_id}",
        "arn:aws:s3:::${aws_s3_bucket_aft_terraform_oss_backend_bucket_id}/*"
      ]
    },
     {
       "Effect": "Allow",
       "Action": [
         "kms:Decrypt",
         "kms:Encrypt",
         "kms:GenerateDataKey"
       ],
       "Resource": "arn:aws:kms:${data_aws_region_current_name}:${data_aws_caller_identity_current_account_id}:key/${aws_s3_bucket_aft_terraform_oss_kms_key_id}"
     }
  ]
}