{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Resource": "arn:aws:logs:${data_aws_region_current_name}:${data_aws_caller_identity_current_account_id}:log-group:/aws/codebuild/aft*",
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:CreateNetworkInterface",
        "ec2:DescribeDhcpOptions",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DeleteNetworkInterface",
        "ec2:DescribeSubnets",
        "ec2:DescribeSecurityGroups",
        "ec2:DescribeVpcs"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:CreateNetworkInterfacePermission"
      ],
      "Resource": [
        "arn:aws:ec2:${data_aws_region_current_name}:${data_aws_caller_identity_current_account_id}:network-interface/*"
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
        "${aws_s3_bucket_aft_codepipeline_customizations_bucket_arn}",
        "${aws_s3_bucket_aft_codepipeline_customizations_bucket_arn}/*"
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
        "codecommit:GetBranch",
        "codecommit:GetRepository",
        "codecommit:GetCommit",
        "codecommit:GitPull",
        "codecommit:UploadArchive",
        "codecommit:GetUploadArchiveStatus",
        "codecommit:CancelUploadArchive"
      ],
      "Resource": "arn:aws:codecommit:${data_aws_region_current_name}:${data_aws_caller_identity_current_account_id}:*customizations*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:*Item"
      ],
      "Resource": [
        "arn:aws:dynamodb:${data_aws_region_current_name}:${data_aws_caller_identity_current_account_id}:table/${data_aws_dynamo_account_metadata_table}"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "sts:AssumeRole"
      ],
      "Resource": [
        "arn:aws:iam::${data_aws_caller_identity_current_account_id}:role/AWSAFTAdmin"
      ]
    },
      {
        "Effect" : "Allow",
        "Action" : [
        "dynamodb:GetItem"
      ],
        "Resource" : [
          "arn:aws:dynamodb:${data_aws_region_current_name}:${data_aws_caller_identity_current_account_id}:table/aft*"
        ]
      }
  ]
}
