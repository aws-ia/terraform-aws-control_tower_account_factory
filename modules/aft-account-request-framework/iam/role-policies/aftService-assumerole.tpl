{
    "Version": "2012-10-17",
    "Statement": {
        "Effect": "Allow",
        "Action": "sts:AssumeRole",
        "Resource": "arn:${data_aws_partition_current_partition}:iam::${data_aws_caller_identity_aft-management_account_id}:role${var_aft_role_admin_path}${var_aft_role_admin_name}"
    }
}
