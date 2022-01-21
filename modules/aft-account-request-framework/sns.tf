resource "aws_sns_topic" "aft_notifications" {
  name              = "aft-notifications"
  kms_master_key_id = "alias/aws/sns"
}

resource "aws_sns_topic" "aft_failure_notifications" {
  name              = "aft-failure-notifications"
  kms_master_key_id = "alias/aws/sns"
}
