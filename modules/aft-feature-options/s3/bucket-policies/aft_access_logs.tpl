{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Allow PutObject",
            "Effect": "Allow",
            "Principal": {
                "Service": [
                    "logging.s3.amazonaws.com"
                ]
            },
            "Action": "s3:PutObject",
            "Resource": [
                "${aws_s3_bucket_aft_access_logs_arn}/*"
            ],
            "Condition": {
                "ArnLike": {
                    "aws:SourceArn": "${aws_s3_bucket_aft_logging_bucket_arn}"
                },
                "StringEquals": {
                    "aws:SourceAccount": "${log_archive_account_id}"
                }
            }
        }
    ]
}
