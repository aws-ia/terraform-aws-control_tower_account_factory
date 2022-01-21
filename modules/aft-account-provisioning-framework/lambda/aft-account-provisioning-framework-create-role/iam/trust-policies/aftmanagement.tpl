{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "AWS": "arn:aws:iam::{AftManagementAccount}:assumed-role/AWSAFTAdmin/AWSAFT-Session"
        },
        "Action": "sts:AssumeRole"
      }
    ]
}
