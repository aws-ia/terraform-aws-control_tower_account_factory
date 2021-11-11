{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect":"Allow",
      "Action": [
        "s3:GetObject",
        "s3:GetObjectVersion",
        "s3:GetBucketVersioning",
        "s3:List*",
        "s3:PutObjectAcl",
        "s3:PutObject"
      ],
      "Resource": [
        "${aws_s3_bucket_aft_codepipeline_customizations_bucket_arn}",
        "${aws_s3_bucket_aft_codepipeline_customizations_bucket_arn}/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "codebuild:BatchGetBuilds",
        "codebuild:StartBuild"
      ],
        "Resource": "arn:aws:codebuild:${data_aws_region_current_name}:${data_aws_caller_identity_current_account_id}:*account-request*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "codecommit:GetBranch",
        "codecommit:GetRepository",
        "codecommit:GetCommit",
        "codecommit:GitPull",
        "codecommit:UploadArchive",
        "codecommit:GetUploadArchiveStatus",
        "codecommit:CancelUploadArchive"
      ],
      "Resource": "arn:aws:codecommit:${data_aws_region_current_name}:${data_aws_caller_identity_current_account_id}:*account-request*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "kms:Decrypt",
        "kms:Encrypt",
        "kms:GenerateDataKey"
      ],
      "Resource": "${data_aws_kms_alias_aft_key_target_key_arn}"
    },
    {
        "Effect": "Allow",
        "Action": "codestar-connections:UseConnection",
        "Resource": "*"
    }
  ]
}
