# Python Layer Builder

Python Layer Builder deploys a codebuild job which creates an AWS Lambda Layer version from a github repository.

This project deploys an IAM role, S3 bucket, Codebuild project, and Cloudwatch Event which triggers the codebuild project.

The codebuild project runs `pip install` using the specified version of python and installs the required packages to a virtual environment,

It then zips the python/lib/pythonx.x folder, and uploads it to S3.

Terraform then waits for approximately 3 minutes and attempts to create a lambda layer from this S3 bucket and key.

If no object is found at this location, the Terraform apply will fail. If this is an update, and something goes wrong with the buid process, the terraform apply will not record any errors. You are encouraged to impement error-handling notifications and integrate them with the python-layer-builder installation in your environment. 

# Requirements File

The build process expects a python package list at the location: `./layer/requirements.txt`

# Variables

layer_name - the name of the lambda layer
aws_region - the region to deploy the layer in
source_url - the url of the github repository which contains the ./layer/ folder, custom packages, and requirements.txt
source_branch - the branch to clone from the source repository.
source_type - Currently, only GITHUB has been tested.
lambda_layer_python_version - Major python version. Defaults to 3.12
github_token - Set $TF_VAR_github_token to securely configure this variable with a personal access token to github.

# Outputs

layer_version_arn - the ARN of the lambda layer version
