import os
import logging
import pprint
import sys
import json
import jsonschema
import pytest
import boto3
import workspace_manager


@pytest.mark.unit
def test_new_resources(plan):
    with open(os.path.join(".",f"./testdata/expected_resources.json")) as json_file:
        response_schema = json.load(json_file)
        result = {}
        plan_results = plan["plan_analysis"]
        for key in plan_results.keys():
            table = [[r, len(plan_results[key][r])] for r in plan_results[key]]
            result[key] = table
        assert json.dumps(response_schema, sort_keys=True) == json.dumps(result, sort_keys=True)


@pytest.mark.unit
def test_resource_count_by_modules(plan):
    with open(os.path.join(".",f"./testdata/expected_resources_by_module.json")) as json_file:
        response_schema = json.load(json_file)
        modules = plan["modules"]
        result = {}
        for m in modules:
            print(f"******: {m} : {len(modules[m]['resources'])}")
            print(f"******: {m} : {len(modules[m]['child_modules'])}")
            print([len(modules[m]["child_modules"]),len(modules[m]["resources"])])
            result[m] = [len(modules[m]["child_modules"]),len(modules[m]["resources"])]
        #val = [{ result[m] : [len(modules[m]["child_modules"]),len(modules[m]["resources"])]} for m in modules]
        #print(json.dumps(result, sort_keeiifccneijdtclbhideckfuhvdetcrjlbnlfeighfdue
        # ys=True))
        #print(json.dumps(response_schema, sort_keys=True))
        assert json.dumps(response_schema, sort_keys=True) == json.dumps(result, sort_keys=True)

@pytest.mark.unit
def test_pipeline_execution():
    session = boto3.Session(profile_name="aft-management", region_name="us-west-2")
    ssm_client = session.client("ssm")
    tf_token = ssm_client.get_parameter(Name="/aft/config/tf-token", WithDecryption=True)
    workspace_manager.setup_and_run_workspace("TLZCloud", "dev-tfc-cc-544582079943-global", "arn:aws:iam::544582079943:role/AWSAFTExecution", tf_token["Parameter"]["Value"])
    workspace_manager.delete_workspace("TLZCloud", "dev-tfc-cc-544582079943-global", "arn:aws:iam::544582079943:role/AWSAFTExecution", tf_token["Parameter"]["Value"])
    return True 