import time

import boto3
import pytest


def execute_tests(tf_dist_type, vcs_type, account_id):

    session = boto3.Session(profile_name="default")
    ssm_client = session.client("ssm")

    param_list = [
        "/aft-account-customizations/terraform/hello-world",
        "/aft-aws-customizations/terraform/hello-world",
        "/aft-global-customizations/terraform/hello-world",
    ]

    for param in param_list:
        try:
            ssm_client.delete_parameter(Name=param)
        except:
            pass

    session = boto3.Session(profile_name="aft-management")
    cp_client = session.client("codepipeline")
    ssm_client = session.client("ssm")

    if tf_dist_type == "oss":
        ssm_client.put_parameter(
            Name="/aft/config/terraform/distribution-type",
            Value="oss",
            Type="String",
            Overwrite=True,
        )

    if tf_dist_type == "cloud":
        ssm_client.put_parameter(
            Name="/aft/config/terraform/distribution-type",
            Value="cloud",
            Type="String",
            Overwrite=True,
        )
        ssm_client.put_parameter(
            Name="/aft/config/tf-org-name",
            Value="TLZCloud",
            Type="String",
            Overwrite=True,
        )
        ssm_client.put_parameter(
            Name="/aft/config/tf-url",
            Value="https://app.terraform.io/api/v2",
            Type="String",
            Overwrite=True,
        )

    if tf_dist_type == "enterprise":
        ssm_client.put_parameter(
            Name="/aft/config/terraform/distribution-type",
            Value="enterprise",
            Type="String",
            Overwrite=True,
        )
        ssm_client.put_parameter(
            Name="/aft/config/tf-org-name",
            Value="AFT-Testing",
            Type="String",
            Overwrite=True,
        )
        ssm_client.put_parameter(
            Name="/aft/config/tf-url",
            Value="https://tfe.tlzdemo.net/api/v2",
            Type="String",
            Overwrite=True,
        )

    if vcs_type == "codecommit":
        ssm_client.put_parameter(
            Name="/aft/config/vcs/provider",
            Value="codecommit",
            Type="String",
            Overwrite=True,
        )

    if vcs_type == "github":
        ssm_client.put_parameter(
            Name="/aft/config/vcs/provider",
            Value="github",
            Type="String",
            Overwrite=True,
        )
        ssm_client.put_parameter(
            Name="/aft/config/global_customizations_module_url",
            Value="github.com",
            Type="String",
            Overwrite=True,
        )
        ssm_client.put_parameter(
            Name="/aft/config/account_customizations_module_url",
            Value="github.com",
            Type="String",
            Overwrite=True,
        )

        ssm_client.put_parameter(
            Name="/aft/config/global_customizations_module_org",
            Value="GithubMohanTestOrg",
            Type="String",
            Overwrite=True,
        )
        ssm_client.put_parameter(
            Name="/aft/config/account_customizations_module_org",
            Value="GithubMohanTestOrg",
            Type="String",
            Overwrite=True,
        )

        ssm_client.put_parameter(
            Name="/aft/config/global_customizations_module_git_ref",
            Value="master",
            Type="String",
            Overwrite=True,
        )
        ssm_client.put_parameter(
            Name="/aft/config/account_customizations_module_git_ref",
            Value="master",
            Type="String",
            Overwrite=True,
        )

        ssm_client.put_parameter(
            Name="/aft/config/git/repo/aft-global-customizations",
            Value="aft-global-customizations",
            Type="String",
            Overwrite=True,
        )
        ssm_client.put_parameter(
            Name="/aft/config/git/repo/aft-account-customizations",
            Value="aft-account-customizations",
            Type="String",
            Overwrite=True,
        )

        vcs_access_token = ssm_client.get_parameter(
            Name="/aft/config/vcs-access-token-github", WithDecryption=True
        )
        vcs_access_token_value = vcs_access_token["Parameter"]["Value"]
        ssm_client.put_parameter(
            Name="/aft/config/vcs-access-token",
            Value=vcs_access_token_value,
            Type="SecureString",
            Overwrite=True,
        )

    if vcs_type == "github-enterprise":
        ssm_client.put_parameter(
            Name="/aft/config/vcs/provider",
            Value="github-enterprise",
            Type="String",
            Overwrite=True,
        )
        ssm_client.put_parameter(
            Name="/aft/config/global_customizations_module_url",
            Value="ghe.tlzdemo.net",
            Type="String",
            Overwrite=True,
        )
        ssm_client.put_parameter(
            Name="/aft/config/account_customizations_module_url",
            Value="ghe.tlzdemo.net",
            Type="String",
            Overwrite=True,
        )

        ssm_client.put_parameter(
            Name="/aft/config/global_customizations_module_org",
            Value="aft-test",
            Type="String",
            Overwrite=True,
        )
        ssm_client.put_parameter(
            Name="/aft/config/account_customizations_module_org",
            Value="aft-test",
            Type="String",
            Overwrite=True,
        )

        ssm_client.put_parameter(
            Name="/aft/config/global_customizations_module_git_ref",
            Value="master",
            Type="String",
            Overwrite=True,
        )
        ssm_client.put_parameter(
            Name="/aft/config/account_customizations_module_git_ref",
            Value="master",
            Type="String",
            Overwrite=True,
        )

        ssm_client.put_parameter(
            Name="/aft/config/git/repo/aft-global-customizations",
            Value="aft-global-customizations",
            Type="String",
            Overwrite=True,
        )
        ssm_client.put_parameter(
            Name="/aft/config/git/repo/aft-account-customizations",
            Value="aft-account-customizations",
            Type="String",
            Overwrite=True,
        )

        vcs_access_token = ssm_client.get_parameter(
            Name="/aft/config/vcs-access-token-ghe", WithDecryption=True
        )
        vcs_access_token_value = vcs_access_token["Parameter"]["Value"]
        ssm_client.put_parameter(
            Name="/aft/config/vcs-access-token",
            Value=vcs_access_token_value,
            Type="SecureString",
            Overwrite=True,
        )

    codepipeline_name = f"{account_id}-customizations-pipeline"

    ssm_client.put_parameter(
        Name="/aft/config/vcs-protocol", Value="ssh", Type="String", Overwrite=True
    )

    response = cp_client.start_pipeline_execution(name=codepipeline_name)
    execution_id = response["pipelineExecutionId"]

    # 30s * 50 = 25 minute timeout
    MAX_RETRY = 50
    RETRY_COUNT = 0
    RETRY_DELAY = 30
    PIPELINE_COMPLETE = False
    while PIPELINE_COMPLETE == False and RETRY_COUNT < MAX_RETRY:
        RETRY_COUNT += 1
        time.sleep(RETRY_DELAY)
        execution_detail = cp_client.get_pipeline_execution(
            pipelineName=codepipeline_name, pipelineExecutionId=execution_id
        )
        pipeline_status = execution_detail["pipelineExecution"]["status"]
        if pipeline_status == "InProgress":
            pass
        elif pipeline_status == "Succeeded":
            PIPELINE_COMPLETE = True
        else:
            raise BaseException(f"Pipeline failed: {execution_detail}")

    session = boto3.Session(profile_name="default")
    ssm_client = session.client("ssm")

    for param in param_list:
        param_value = ssm_client.get_parameter(Name=param)
        assert param_value["Parameter"]["Value"] is not None

    if vcs_type != "codecommit":

        param_list = [
            "/aft-account-customizations/terraform/hello-world",
            "/aft-aws-customizations/terraform/hello-world",
            "/aft-global-customizations/terraform/hello-world",
        ]

        for param in param_list:
            try:
                ssm_client.delete_parameter(Name=param)
            except:
                pass

        session = boto3.Session(profile_name="aft-management")
        cp_client = session.client("codepipeline")
        ssm_client = session.client("ssm")

        ssm_client.put_parameter(
            Name="/aft/config/vcs-protocol",
            Value="https",
            Type="String",
            Overwrite=True,
        )

        response = cp_client.start_pipeline_execution(name=codepipeline_name)
        execution_id = response["pipelineExecutionId"]

        # 30s * 50 = 25 minute timeout
        MAX_RETRY = 50
        RETRY_COUNT = 0
        RETRY_DELAY = 30
        PIPELINE_COMPLETE = False
        while PIPELINE_COMPLETE == False and RETRY_COUNT < MAX_RETRY:
            RETRY_COUNT += 1
            time.sleep(RETRY_DELAY)
            execution_detail = cp_client.get_pipeline_execution(
                pipelineName=codepipeline_name, pipelineExecutionId=execution_id
            )
            pipeline_status = execution_detail["pipelineExecution"]["status"]
            if pipeline_status == "InProgress":
                pass
            elif pipeline_status == "Succeeded":
                PIPELINE_COMPLETE = True
            else:
                raise BaseException(f"Pipeline failed: {execution_detail}")

        session = boto3.Session(profile_name="default")
        ssm_client = session.client("ssm")

        for param in param_list:
            param_value = ssm_client.get_parameter(Name=param)
            assert param_value["Parameter"]["Value"] is not None

    return True


@pytest.mark.integration
@pytest.mark.slow
def test_pipeline_execution(account_id):

    execute_oss_tests = "false"
    execute_cloud_tests = "true"
    execute_entrprise_tests = "false"

    # Add logic to read existing ssm values and update them at the end

    if execute_oss_tests == "true":
        # Testing Terraform Open Source Distribution type Integration tests
        execute_tests("oss", "codecommit", account_id)
        execute_tests("oss", "github", account_id)
        execute_tests("oss", "github-enterprise", account_id)

    if execute_cloud_tests == "true":
        # Testing Terraform Cloud Distribution type Integration tests
        execute_tests("cloud", "codecommit", account_id)
        execute_tests("cloud", "github", account_id)
        execute_tests("cloud", "github-enterprise", account_id)

    if execute_entrprise_tests == "true":
        # Testing Terraform Enterprise Distribution type Integration tests
        execute_tests("enterprise", "codecommit", account_id)
        execute_tests("enterprise", "github", account_id)
        execute_tests("enterprise", "github-enterprise", account_id)
