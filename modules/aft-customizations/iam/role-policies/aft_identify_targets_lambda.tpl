{
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "sts:AssumeRole"
        ],
        "Resource" : [
          "arn:aws:iam::${data_aws_caller_identity_current_account_id}:role/AWSAFTAdmin"
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : "sts:GetCallerIdentity",
        "Resource" : "*"
      },
      {
        "Effect" : "Allow",
        "Action" : "ssm:GetParameter",
        "Resource" : [
            "arn:aws:ssm:${data_aws_region_current_name}:${data_aws_caller_identity_current_account_id}:parameter/aft/*"
        ]
      },
    {
      "Effect" : "Allow",
      "Action" : [
      "dynamodb:Scan"
    ],
      "Resource" : [
        "arn:aws:dynamodb:${data_aws_region_current_name}:${data_aws_caller_identity_current_account_id}:table/${request_metadata_table_name}"
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
