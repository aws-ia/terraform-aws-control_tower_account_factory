{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "states:StartExecution",
            "Resource": "${invoke_account_provisioning_arn}"
        },
        {
          "Effect": "Allow",
          "Action": [
            "ssm:GetParameters",
            "ssm:GetParameter"
          ],
          "Resource": [
            "arn:aws:ssm:${data_aws_region_current_name}:${data_aws_caller_identity_current_account_id}:parameter/aft/*"
          ]
        },
        {
          "Effect": "Allow",
          "Action": [
            "dynamodb:GetItem"
          ],
          "Resource": [
            "arn:aws:dynamodb:${data_aws_region_current_name}:${data_aws_caller_identity_current_account_id}:table/${data_aws_dynamo_account_metadata_table}",
            "arn:aws:dynamodb:${data_aws_region_current_name}:${data_aws_caller_identity_current_account_id}:table/${data_aws_dynamo_account_request_table}"
          ]
        },
        {
          "Effect": "Allow",
          "Action": [
            "kms:Decrypt",
            "kms:Encrypt",
            "kms:GenerateDataKey"
          ],
          "Resource": "${data_aws_kms_alias_aft_key_target_key_arn}"
        }
    ]
}