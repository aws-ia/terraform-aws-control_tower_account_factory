{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::${aft_account_id}:root"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
