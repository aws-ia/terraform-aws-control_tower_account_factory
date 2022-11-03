{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:*Item"
      ],
      "Resource": ${jsonencode([application_request_table_arn, network_request_table_arn])}
    }
  ]
}
