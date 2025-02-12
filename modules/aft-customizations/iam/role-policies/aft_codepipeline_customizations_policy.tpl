{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:Get*",
        "s3:List*",
        "s3:Put*"
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
      "Resource": "arn:${data_aws_partition_current_partition}:codebuild:${data_aws_region_current_name}:${data_aws_caller_identity_current_account_id}:*customizations*"
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
      "Resource": "arn:${data_aws_partition_current_partition}:codecommit:${data_aws_region_current_name}:${data_aws_caller_identity_current_account_id}:*"
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
      "Action": [
        "codestar-connections:UseConnection",
        "codeconnections:UseConnection"
      ],
      "Resource": "*"
    }
  ]
}
