{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "codepipeline:StartPipelineExecution",
                "codepipeline:ListPipelineExecutions",
                "codepipeline:ListPipelines",
                "ssm:GetParameter",
                "codepipeline:ListTagsForResource"
            ],
            "Resource": [
                "arn:${data_aws_partition_current_partition}:codepipeline:${data_aws_region_current_name}:${data_aws_caller_identity_current_account_id}:*",
                "arn:${data_aws_partition_current_partition}:ssm:${data_aws_region_current_name}:${data_aws_caller_identity_current_account_id}:parameter/aft/*"
            ]
        },
      {
        "Effect" : "Allow",
        "Action" : [
            "kms:GenerateDataKey",
            "kms:Encrypt",
            "kms:Decrypt"
        ],
        "Resource" : [
            "${aws_kms_key_aft_arn}"
        ]
      },
      {
          "Effect": "Allow",
          "Action": "sts:GetCallerIdentity",
          "Resource": "*"
      },
      {
        "Effect" : "Allow",
        "Action" : [
            "sns:Publish"
        ],
        "Resource" : [
            "${aft_sns_topic_arn}",
            "${aft_failure_sns_topic_arn}"
        ]
      }
    ]
}
