{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "codecommit:AssociateApprovalRuleTemplateWithRepository",
                "codecommit:BatchAssociateApprovalRuleTemplateWithRepositories",
                "codecommit:BatchDisassociateApprovalRuleTemplateFromRepositories",
                "codecommit:BatchGet*",
                "codecommit:BatchDescribe*",
                "codecommit:Create*",
                "codecommit:DeleteBranch",
                "codecommit:DeleteFile",
                "codecommit:Describe*",
                "codecommit:DisassociateApprovalRuleTemplateFromRepository",
                "codecommit:EvaluatePullRequestApprovalRules",
                "codecommit:Get*",
                "codecommit:List*",
                "codecommit:Merge*",
                "codecommit:OverridePullRequestApprovalRules",
                "codecommit:Put*",
                "codecommit:Post*",
                "codecommit:TagResource",
                "codecommit:Test*",
                "codecommit:UntagResource",
                "codecommit:Update*",
                "codecommit:GitPull",
                "codecommit:GitPush"
            ],
            "Resource": "*"
        },
        {
            "Sid": "CloudWatchEventsCodeCommitRulesAccess",
            "Effect": "Allow",
            "Action": [
                "events:DeleteRule",
                "events:DescribeRule",
                "events:DisableRule",
                "events:EnableRule",
                "events:PutRule",
                "events:PutTargets",
                "events:RemoveTargets",
                "events:ListTargetsByRule"
            ],
            "Resource": "arn:${data_aws_partition_current_partition}:events:*:*:rule/codecommit*"
        },
        {
            "Sid": "SNSTopicAndSubscriptionAccess",
            "Effect": "Allow",
            "Action": [
                "sns:Subscribe",
                "sns:Unsubscribe"
            ],
            "Resource": "arn:${data_aws_partition_current_partition}:sns:*:*:codecommit*"
        },
        {
            "Sid": "SNSTopicAndSubscriptionReadAccess",
            "Effect": "Allow",
            "Action": [
                "sns:ListTopics",
                "sns:ListSubscriptionsByTopic",
                "sns:GetTopicAttributes"
            ],
            "Resource": "*"
        },
        {
            "Sid": "LambdaReadOnlyListAccess",
            "Effect": "Allow",
            "Action": [
                "lambda:ListFunctions"
            ],
            "Resource": "*"
        },
        {
            "Sid": "IAMReadOnlyListAccess",
            "Effect": "Allow",
            "Action": [
                "iam:ListUsers"
            ],
            "Resource": "*"
        },
        {
            "Sid": "IAMReadOnlyConsoleAccess",
            "Effect": "Allow",
            "Action": [
                "iam:ListAccessKeys",
                "iam:ListSSHPublicKeys",
                "iam:ListServiceSpecificCredentials"
            ],
            "Resource": "arn:${data_aws_partition_current_partition}:iam::*:user/${data_aws_caller_identity_aft-management_user_id}"
        },
        {
            "Sid": "IAMUserSSHKeys",
            "Effect": "Allow",
            "Action": [
                "iam:DeleteSSHPublicKey",
                "iam:GetSSHPublicKey",
                "iam:ListSSHPublicKeys",
                "iam:UpdateSSHPublicKey",
                "iam:UploadSSHPublicKey"
            ],
            "Resource": "arn:${data_aws_partition_current_partition}:iam::*:user/${data_aws_caller_identity_aft-management_user_id}"
        },
        {
            "Sid": "IAMSelfManageServiceSpecificCredentials",
            "Effect": "Allow",
            "Action": [
                "iam:CreateServiceSpecificCredential",
                "iam:UpdateServiceSpecificCredential",
                "iam:DeleteServiceSpecificCredential",
                "iam:ResetServiceSpecificCredential"
            ],
            "Resource": "arn:${data_aws_partition_current_partition}:iam::*:user/${data_aws_caller_identity_aft-management_user_id}"
        },
        {
            "Sid": "CodeStarNotificationsReadWriteAccess",
            "Effect": "Allow",
            "Action": [
                "codestar-notifications:CreateNotificationRule",
                "codestar-notifications:DescribeNotificationRule",
                "codestar-notifications:UpdateNotificationRule",
                "codestar-notifications:Subscribe",
                "codestar-notifications:Unsubscribe"
            ],
            "Resource": "*",
            "Condition": {
                "StringLike": {
                    "codestar-notifications:NotificationsForResource": "arn:${data_aws_partition_current_partition}:codecommit:*"
                }
            }
        },
        {
            "Sid": "CodeStarNotificationsListAccess",
            "Effect": "Allow",
            "Action": [
                "codestar-notifications:ListNotificationRules",
                "codestar-notifications:ListTargets",
                "codestar-notifications:ListTagsforResource",
                "codestar-notifications:ListEventTypes"
            ],
            "Resource": "*"
        },
        {
            "Sid": "AmazonCodeGuruReviewerFullAccess",
            "Effect": "Allow",
            "Action": [
                "codeguru-reviewer:AssociateRepository",
                "codeguru-reviewer:DescribeRepositoryAssociation",
                "codeguru-reviewer:ListRepositoryAssociations",
                "codeguru-reviewer:DisassociateRepository",
                "codeguru-reviewer:DescribeCodeReview",
                "codeguru-reviewer:ListCodeReviews"
            ],
            "Resource": "*"
        },
        {
            "Sid": "AmazonCodeGuruReviewerSLRCreation",
            "Action": "iam:CreateServiceLinkedRole",
            "Effect": "Allow",
            "Resource": "arn:${data_aws_partition_current_partition}:iam::*:role/aws-service-role/codeguru-reviewer.amazonaws.com/AWSServiceRoleForAmazonCodeGuruReviewer",
            "Condition": {
                "StringLike": {
                    "iam:AWSServiceName": "codeguru-reviewer.amazonaws.com"
                }
            }
        },
        {
            "Sid": "CloudWatchEventsManagedRules",
            "Effect": "Allow",
            "Action": [
                "events:PutRule",
                "events:PutTargets",
                "events:DeleteRule",
                "events:RemoveTargets"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "events:ManagedBy": "codeguru-reviewer.amazonaws.com"
                }
            }
        },
        {
            "Sid": "CodeStarNotificationsChatbotAccess",
            "Effect": "Allow",
            "Action": [
                "chatbot:DescribeSlackChannelConfigurations"
            ],
            "Resource": "*"
        },
        {
            "Sid": "CodeStarConnectionsReadOnlyAccess",
            "Effect": "Allow",
            "Action": [
                "codestar-connections:ListConnections",
                "codestar-connections:GetConnection"
            ],
            "Resource": "arn:${data_aws_partition_current_partition}:codestar-connections:*:*:connection/*"
        }
    ]
}
