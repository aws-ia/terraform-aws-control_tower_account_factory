{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:${data_aws_partition_current_partition}:iam::${aft_account_id}:root"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
