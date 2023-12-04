#!/usr/bin/python
# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import os
import time

import requests

TERRAFORM_API_ENDPOINT = ""
LOCAL_CONFIGURATION_PATH = ""
TERRAFORM_VERSION = ""


def init(api_endpoint, tf_version, config_path):
    global TERRAFORM_API_ENDPOINT
    global TERRAFORM_VERSION
    global LOCAL_CONFIGURATION_PATH

    TERRAFORM_API_ENDPOINT = api_endpoint
    TERRAFORM_VERSION = tf_version
    LOCAL_CONFIGURATION_PATH = config_path


def check_workspace_exists(organization_name, workspace_name, api_token):
    endpoint = "{}/organizations/{}/workspaces/{}".format(
        TERRAFORM_API_ENDPOINT, organization_name, workspace_name
    )
    headers = __build_standard_headers(api_token)
    tf_dist = os.environ.get("TF_DISTRIBUTION")
    response = requests.get(endpoint, headers=headers, verify=tf_dist != "tfe")
    data = response.json()

    if "data" in data.keys():
        if "id" in data["data"].keys():
            return data["data"]["id"]
    return None


def create_workspace(organization_name, workspace_name, api_token):
    workspace_id = check_workspace_exists(organization_name, workspace_name, api_token)
    if workspace_id:
        return workspace_id
    else:
        endpoint = "{}/organizations/{}/workspaces".format(
            TERRAFORM_API_ENDPOINT, organization_name
        )
        headers = __build_standard_headers(api_token)
        payload = {
            "data": {
                "attributes": {
                    "name": workspace_name,
                    "terraform-version": TERRAFORM_VERSION,
                    "auto-apply": True,
                },
                "type": "workspaces",
            }
        }
        response = __post(endpoint, headers, payload)
        return response["data"]["id"]


def create_configuration_version(workspace_id, api_token):
    endpoint = "{}/workspaces/{}/configuration-versions".format(
        TERRAFORM_API_ENDPOINT, workspace_id
    )
    headers = __build_standard_headers(api_token)
    payload = {
        "data": {
            "type": "configuration-versions",
            "attributes": {"auto-queue-runs": False},
        }
    }
    response = __post(endpoint, headers, payload)
    cv_id = response["data"]["id"]
    upload_url = response["data"]["attributes"]["upload-url"]
    return cv_id, upload_url


def upload_configuration_content(data, upload_url):
    headers = {"Content-Type": "application/octet-stream", "Accept": "application/json"}
    tf_dist = os.environ.get("TF_DISTRIBUTION")
    requests.put(upload_url, data=data, headers=headers, verify=tf_dist != "tfe")


def set_environment_variable(
    key, value, description, workspace_id, sensitive, category, api_token
):
    endpoint = "{}/workspaces/{}/vars".format(TERRAFORM_API_ENDPOINT, workspace_id)
    headers = __build_standard_headers(api_token)
    payload = {
        "data": {
            "attributes": {
                "key": key,
                "value": value,
                "description": description,
                "category": category,
                "sensitive": sensitive,
            },
            "type": "vars",
        }
    }
    __post(endpoint, headers, payload)


def get_workspace_vars(workspace_id, api_token):
    endpoint = "{}/workspaces/{}/vars".format(TERRAFORM_API_ENDPOINT, workspace_id)
    headers = __build_standard_headers(api_token)
    response = __get(endpoint, headers)
    return response["data"]


def update_environment_variable(
    var_id, key, value, description, workspace_id, sensitive, category, api_token
):
    endpoint = "{}/workspaces/{}/vars/{}".format(
        TERRAFORM_API_ENDPOINT, workspace_id, var_id
    )
    headers = __build_standard_headers(api_token)
    payload = {
        "data": {
            "attributes": {
                "key": key,
                "value": value,
                "description": description,
                "category": category,
                "sensitive": sensitive,
            },
            "type": "vars",
        }
    }
    __patch(endpoint, headers, payload)


def create_run(workspace_id, cv_id, api_token):
    endpoint = "{}/runs".format(TERRAFORM_API_ENDPOINT)
    headers = __build_standard_headers(api_token)
    payload = {
        "data": {
            "attributes": {"is-destroy": False, "message": "Run created by AFT"},
            "type": "runs",
            "relationships": {
                "workspace": {"data": {"type": "workspaces", "id": workspace_id}},
                "configuration-version": {
                    "data": {"type": "configuration-versions", "id": cv_id}
                },
            },
        }
    }
    response = __post(endpoint, headers, payload)
    return response["data"]["id"]


def create_destroy_run(workspace_id, api_token):
    endpoint = "{}/runs".format(TERRAFORM_API_ENDPOINT)
    headers = __build_standard_headers(api_token)
    payload = {
        "data": {
            "attributes": {"is-destroy": True, "message": "Destroy run created by AFT"},
            "type": "runs",
            "relationships": {
                "workspace": {"data": {"type": "workspaces", "id": workspace_id}}
            },
        }
    }
    response = __post(endpoint, headers, payload)
    return response["data"]["id"]


def delete_workspace(workspace_id, api_token):
    endpoint = "{}/workspaces/{}".format(TERRAFORM_API_ENDPOINT, workspace_id)
    headers = __build_standard_headers(api_token)
    response = __delete(endpoint, headers)
    if response is not None:
        errors = response["errors"]
        if len(errors) == 0:
            print("Successfully deleted workspace {}".format(workspace_id))
        else:
            print("Error occured deleting workspace {}".format(workspace_id))
            print(str(errors))
    else:
        print("Successfully deleted workspace {}".format(workspace_id))


def wait_to_stabilize(entity_type, entity_id, target_states, api_token):
    while True:
        status = get_action_status(entity_type, entity_id, api_token)
        if status in target_states:
            break
        print("{} not yet ready. In status {}".format(entity_type, status))
        time.sleep(10)
    return status


def get_action_status(object_type, object_id, api_token):
    endpoint = "{}/{}/{}".format(TERRAFORM_API_ENDPOINT, object_type, object_id)
    print(endpoint)
    headers = __build_standard_headers(api_token)
    response = __get(endpoint, headers)
    return response["data"]["attributes"]["status"]


def __build_standard_headers(api_token):
    return {
        "Authorization": "Bearer {}".format(api_token),
        "Content-type": "application/vnd.api+json",
    }


def __post(endpoint, headers, payload):
    tf_dist = os.environ.get("TF_DISTRIBUTION")
    response = requests.post(
        endpoint, headers=headers, json=payload, verify=tf_dist != "tfe"
    )
    __handle_errors(response)
    return response.json()


def __patch(endpoint, headers, payload):
    tf_dist = os.environ.get("TF_DISTRIBUTION")
    response = requests.patch(
        endpoint, headers=headers, json=payload, verify=tf_dist != "tfe"
    )
    __handle_errors(response)
    return response.json()


def __get(endpoint, headers):
    tf_dist = os.environ.get("TF_DISTRIBUTION")
    response = requests.get(endpoint, headers=headers, verify=tf_dist != "tfe")
    __handle_errors(response)
    return response.json()


def __delete(endpoint, headers):
    tf_dist = os.environ.get("TF_DISTRIBUTION")
    response = requests.delete(endpoint, headers=headers, verify=tf_dist != "tfe")
    # __handle_errors(response)
    return response.json()


def __handle_errors(response):
    if response is None or response.json() is None or "errors" not in response.json():
        return

    errors = response.json()["errors"]
    if len(errors) == 0:
        print("Empty set of errors returned by client; raising internal failure")
        raise ClientError(status="500", message="Internal failure")
    elif len(errors) == 1:
        error = errors[0]
        raise ClientError(status=error["status"], message=error["title"])
    else:
        print(
            "More than one error returned by client; raising internal failure and placing all errors in the message"
        )
        raise ClientError(status="500", message=str(errors))


class ClientError(Exception):
    def __init__(self, status, message):
        self.status = status
        super().__init__(message)
