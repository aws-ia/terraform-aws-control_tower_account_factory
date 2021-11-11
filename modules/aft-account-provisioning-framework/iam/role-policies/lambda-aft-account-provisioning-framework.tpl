{
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
        "dynamodb:BatchGetItem",
        "dynamodb:BatchWriteItem",
        "dynamodb:DeleteItem",
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
        "Resource" : [
          "arn:aws:dynamodb:${data_aws_region_aft-management_name}:${data_aws_caller_identity_aft-management_account_id}:table/aft*"
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : "ssm:GetParameter",
        "Resource" : [
          "arn:aws:ssm:${data_aws_region_aft-management_name}:${data_aws_caller_identity_aft-management_account_id}:parameter/aft/*"
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "sts:AssumeRole",
          "sns:Publish"
        ],
        "Resource" : [
          "arn:aws:iam::${data_aws_caller_identity_aft-management_account_id}:role/AWSAFTAdmin"
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : "sts:GetCallerIdentity",
        "Resource" : "*"
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
      },
      {
      "Effect" : "Allow",
      "Action" : [
        "kms:GenerateDataKey",
        "kms:Encrypt",
        "kms:Decrypt"
      ],
      "Resource" : [
        "${aws_kms_key_aft_arn}",
        "arn:aws:kms:${data_aws_region_aft-management_name}:${data_aws_caller_identity_aft-management_account_id}:alias/aws/sns"
      ]
      }
    ]
}
