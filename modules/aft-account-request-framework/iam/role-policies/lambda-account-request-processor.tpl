{
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "sqs:DeleteMessage",
          "sts:AssumeRole",
          "sns:Publish",
          "sqs:ReceiveMessage"
        ],
        "Resource" : [
          "${aws_sns_topic_aft_notifications_arn}",
          "${aws_sns_topic_aft_failure_notifications_arn}",
          "arn:${data_aws_partition_current_partition}:iam::${data_aws_caller_identity_aft-management_account_id}:role/AWSAFTAdmin",
          "${aws_sqs_queue_aft_account_request_arn}"
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
      }
    ]
}
