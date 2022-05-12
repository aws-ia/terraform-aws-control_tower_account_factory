{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "codepipeline:ListPipelineExecutions",
            "Resource": "arn:aws:codepipeline:${data_aws_region_current_name}:${data_aws_caller_identity_current_account_id}:*"
        },
        {
            "Effect": "Allow",
            "Action": "codepipeline:ListPipelines",
            "Resource": "*"
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
