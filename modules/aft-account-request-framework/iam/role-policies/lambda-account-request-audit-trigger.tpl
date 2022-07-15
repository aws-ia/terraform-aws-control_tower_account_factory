{
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "dynamodb:GetShardIterator",
          "dynamodb:DescribeStream",
          "dynamodb:GetRecords",
          "dynamodb:ListShards",
				  "dynamodb:ListStreams"
        ],
        "Resource" : [
          "arn:${data_aws_partition_current_partition}:dynamodb:${data_aws_region_aft-management_name}:${data_aws_caller_identity_aft-management_account_id}:table/${aws_dynamodb_table_aft-request_name}/stream/*"
        ]
      },
    {
        "Effect": "Allow",
        "Action": [
            "dynamodb:Query",
            "dynamodb:PutItem"
        ],
        "Resource": "arn:${data_aws_partition_current_partition}:dynamodb:${data_aws_region_aft-management_name}:${data_aws_caller_identity_aft-management_account_id}:table/${aws_dynamodb_table_aft-request-audit_name}"
    },
      {
        "Effect" : "Allow",
        "Action" : "dynamodb:ListStreams",
        "Resource" : "*"
      },
      {
        "Effect" : "Allow",
        "Action" : "sqs:SendMessage",
        "Resource" : "${aws_sqs_queue_aft_account_request_arn}"
      },
      {
        "Effect" : "Allow",
        "Action" : "ssm:GetParameter",
        "Resource" : [
          "arn:${data_aws_partition_current_partition}:ssm:${data_aws_region_aft-management_name}:${data_aws_caller_identity_aft-management_account_id}:parameter/aft/*"
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
          "arn:${data_aws_partition_current_partition}:kms:${data_aws_region_aft-management_name}:${data_aws_caller_identity_aft-management_account_id}:alias/aws/sns"
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "sns:Publish"
        ],
        "Resource" : [
          "${aws_sns_topic_aft_notifications_arn}",
          "${aws_sns_topic_aft_failure_notifications_arn}"
        ]
      }
    ]
}
