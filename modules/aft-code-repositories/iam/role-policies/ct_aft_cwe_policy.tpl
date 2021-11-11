{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "codepipeline:StartPipelineExecution"
            ],
            "Resource": [
                "arn:aws:codepipeline:${region}:${account_id}:${account_request_pipeline_name}",
                "arn:aws:codepipeline:${region}:${account_id}:${provisioning_customizations_pipeline_name}"
            ]
        }
    ]
}