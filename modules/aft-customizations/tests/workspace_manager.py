#!/usr/bin/python

import boto3
import time
import argparse
import io
import os

import terraform_client as terraform

TERRAFORM_API_ENDPOINT = ""
LOCAL_CONFIGURATION_PATH = ""
TERRAFORM_VERSION = ""

if os.getenv("terraform_version") is None:
    TERRAFORM_VERSION = "0.15.5"
else:
    TERRAFORM_VERSION = os.getenv("terraform_version")

if os.getenv("terraform_api_endpoint") is None:
    TERRAFORM_API_ENDPOINT = "https://app.terraform.io/api/v2"
else:
    TERRAFORM_API_ENDPOINT = os.getenv("terraform_api_endpoint")
    
if os.getenv("local_configuration_path") is None:
    LOCAL_CONFIGURATION_PATH = "./temp_configuration_file.tar.gz"
else:
    LOCAL_CONFIGURATION_PATH = os.getenv("local_configuration_path")

terraform.init(TERRAFORM_API_ENDPOINT, TERRAFORM_VERSION, LOCAL_CONFIGURATION_PATH)

def setup_and_run_workspace(organization_name, workspace_name, assume_role_arn, api_token):

    workspace_id = setup_workspace(organization_name, workspace_name, assume_role_arn, api_token)
    run_id = stage_run(workspace_id,assume_role_arn, api_token)
    return run_id

def setup_workspace(organization_name, workspace_name, assume_role_arn, api_token):
    workspace_id = terraform.create_workspace(organization_name, workspace_name, api_token)
    print("Successfully created workspace {} with ID {}".format(workspace_name, workspace_id))
    set_aws_credentials(workspace_id, assume_role_arn, api_token)
    print("Successfully placed AWS credentials on workspace for {}".format(assume_role_arn))
    return workspace_id


# def stage_run(workspace_id, s3_uri, assume_role_arn, api_token):
def stage_run(workspace_id, assume_role_arn, api_token):
    cv_id, upload_url = terraform.create_configuration_version(workspace_id, api_token)
    print("Successfully created a new configuration version: {}".format(cv_id))
    data = open(LOCAL_CONFIGURATION_PATH, "rb")
    terraform.upload_configuration_content(data, upload_url)
    print("Successfully uploaded configuration content to upload URL: {}".format(upload_url))
    terraform.wait_to_stabilize('configuration-versions', cv_id, ['uploaded'], api_token)
    set_aws_credentials(workspace_id, assume_role_arn, api_token)
    print("Successfully placed AWS credentials on workspace for {}".format(assume_role_arn))
    run_id = terraform.create_run(workspace_id, cv_id, api_token)
    print("Successfully created run: {}".format(run_id))
    terraform.wait_to_stabilize('runs',
                                run_id,
                                ['planned','applied', 'cost_estimated', 'planned_and_finished', 'errored', 'policy_checked'],
                                api_token)
    return run_id

def set_aws_credentials(workspace_id, assume_role_arn, api_token):
    role_credentials = __assume_role(assume_role_arn)
    current_vars = terraform.get_workspace_vars(workspace_id, api_token)
    transformed_current_vars_dict = __transform_workspace_vars(current_vars)

    if 'AWS_ACCESS_KEY_ID' in transformed_current_vars_dict:
        terraform.update_environment_variable(transformed_current_vars_dict['AWS_ACCESS_KEY_ID'], 'AWS_ACCESS_KEY_ID', role_credentials['AccessKeyId'], "AWS access key", workspace_id, False, "env", api_token)
    else:
        terraform.set_environment_variable('AWS_ACCESS_KEY_ID', role_credentials['AccessKeyId'], "AWS access key", workspace_id, False, "env", api_token)

    if 'AWS_SECRET_ACCESS_KEY' in transformed_current_vars_dict:
        terraform.update_environment_variable(transformed_current_vars_dict['AWS_SECRET_ACCESS_KEY'], 'AWS_SECRET_ACCESS_KEY', role_credentials['SecretAccessKey'], "AWS secret access key", workspace_id, True, "env", api_token)
    else:
        terraform.set_environment_variable('AWS_SECRET_ACCESS_KEY', role_credentials['SecretAccessKey'], "AWS secret access key", workspace_id, True, "env", api_token)

    if 'AWS_SESSION_TOKEN' in transformed_current_vars_dict:
        terraform.update_environment_variable(transformed_current_vars_dict['AWS_SESSION_TOKEN'], 'AWS_SESSION_TOKEN', role_credentials['SessionToken'], "AWS session token", workspace_id, True, "env", api_token)
    else:
        terraform.set_environment_variable('AWS_SESSION_TOKEN', role_credentials['SessionToken'], "AWS session token", workspace_id, True, "env", api_token)


def set_terraform_variables(workspace_id, input_variables, api_token):
    if input_variables is None:
        return
    current_vars = terraform.get_workspace_vars(workspace_id, api_token)
    transformed_current_vars_dict = __transform_workspace_vars(current_vars)
    print(input_variables)
    for key in input_variables:
        value = input_variables[key]
        print("Processing terraform variable {} with value {}".format(key, value))
        if key not in transformed_current_vars_dict:
            terraform.set_environment_variable(key, value, "Terraform input variable set by AFT", workspace_id, False, "terraform", api_token)
        else:
            terraform.update_environment_variable(transformed_current_vars_dict[key], key, value, "Terraform input variable set by AFT", workspace_id, False, "terraform", api_token)


def stage_destroy(workspace_id, assume_role_arn, api_token):
    set_aws_credentials(workspace_id, assume_role_arn, api_token)
    run_id = terraform.create_destroy_run(workspace_id, api_token)
    # If in a Run there is no resource change, after execution it will be 'planned_and_finished', which can be a stabilized state
    terraform.wait_to_stabilize('runs', run_id, ['planned', 'applied', 'planned_and_finished', 'policy_checked'], api_token)
    return run_id


def delete_workspace(organization_name, workspace_name, assume_role_arn, api_token):
    workspace_id = terraform.check_workspace_exists(organization_name, workspace_name, api_token)
    if workspace_id:
        stage_destroy(workspace_id,assume_role_arn, api_token)
        terraform.delete_workspace(workspace_id, api_token)
    else:
        print("Selected workspace {} doesnot exist. Deletion of workspace not completed".format(workspace_name))

def __assume_role(assume_role_arn):
    sts = boto3.client('sts')
    response = sts.assume_role(RoleArn=assume_role_arn, RoleSessionName='AFTTerraformCloud')
    return response['Credentials']

def __transform_workspace_vars(workspace_vars):
    vars_dict = {}
    for var in workspace_vars:
        vars_dict[var['attributes']['key']] = var['id']
    return vars_dict

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to create a new workspace with valid AWS credentials in the specified organization")
    parser.add_argument('operation', type=str, help="Name of the method to call")
    parser.add_argument('organization_name', type=str, help="Name of the organization in which the workspace should be created")
    parser.add_argument('workspace_name', type=str, help="Name of the workspace to be created")
    parser.add_argument('assume_role_arn', type=str, help="IAM Role ARN to be used by the workspace")
    parser.add_argument('api_token', type=str, help="Terraform Cloud API token")

    args = parser.parse_args()
    if args.operation == "delete":
        delete_workspace(args.organization_name, args.workspace_name, args.assume_role_arn, args.api_token)
    elif args.operation == "deploy":
        setup_and_run_workspace(args.organization_name, args.workspace_name, args.assume_role_arn, args.api_token)
