data "aws_iam_policy" "network_administrator_policy" {
  name = "NetworkAdministrator"
}

resource "aws_iam_role" "netops" {
  name               = "netops"
  assume_role_policy = data.aws_iam_policy.network_administrator_policy.policy_id
}