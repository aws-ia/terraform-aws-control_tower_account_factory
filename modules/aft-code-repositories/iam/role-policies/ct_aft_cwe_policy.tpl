{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "codepipeline:StartPipelineExecution"
            ],
            "Resource": [
                "arn:${data_aws_partition_current_partition}:codepipeline:${region}:${account_id}:${provisioning_customizations_pipeline_name}"
            ]
        }
    ]
}
