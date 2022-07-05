#!/bin/bash
# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


function write_to_credentials {
  local profile=${1}
  local credentials=${2}
  local aws_access_key_id
  local aws_secret_access_key

  aws_access_key_id="$(echo "${credentials}" | jq --raw-output ".Credentials[\"AccessKeyId\"]")"
  aws_secret_access_key="$(echo "${credentials}" | jq --raw-output ".Credentials[\"SecretAccessKey\"]")"
  aws_session_token="$(echo "${credentials}" | jq --raw-output ".Credentials[\"SessionToken\"]")"

  aws configure set aws_access_key_id "${aws_access_key_id}" --profile "${profile}"
  aws configure set aws_secret_access_key "${aws_secret_access_key}" --profile "${profile}"
  aws configure set aws_session_token "${aws_session_token}" --profile "${profile}"
}


function main {
  local AFT_MGMT_ROLE
  local AFT_EXECUTION_ROLE
  local ROLE_SESSION_NAME
  local AFT_MGMT_ACCOUNT
  local CT_MGMT_ACCOUNT
  local AUDIT_ACCOUNT
  local LOG_ARCHIVE_ACCOUNT
  local CREDENTIALS

  #Lookup SSM Parameters
  AFT_MGMT_ROLE=$(aws ssm get-parameter --name /aft/resources/iam/aft-administrator-role-name | jq --raw-output ".Parameter.Value")
  AFT_EXECUTION_ROLE=$(aws ssm get-parameter --name /aft/resources/iam/aft-execution-role-name | jq --raw-output ".Parameter.Value")
  ROLE_SESSION_NAME=$(aws ssm get-parameter --name /aft/resources/iam/aft-session-name | jq --raw-output ".Parameter.Value")
  AFT_MGMT_ACCOUNT=$(aws ssm get-parameter --name /aft/account/aft-management/account-id | jq --raw-output ".Parameter.Value")
  CT_MGMT_ACCOUNT=$(aws ssm get-parameter --name 	/aft/account/ct-management/account-id | jq --raw-output ".Parameter.Value")
  AUDIT_ACCOUNT=$(aws ssm get-parameter --name 	/aft/account/audit/account-id | jq --raw-output ".Parameter.Value")
  LOG_ARCHIVE_ACCOUNT=$(aws ssm get-parameter --name 	/aft/account/log-archive/account-id | jq --raw-output ".Parameter.Value")

  # Assume aws-aft-Administrator Role in AFT Management account. This is a Hub role which has permissions to assume other AFT roles
  echo "Generating credentials for ${AFT_MGMT_ROLE} in aft-management account: ${AFT_MGMT_ACCOUNT}"
  CREDENTIALS=$(aws sts assume-role --role-arn "arn:aws:iam::${AFT_MGMT_ACCOUNT}:role/${AFT_MGMT_ROLE}" --role-session-name "${ROLE_SESSION_NAME}")
  write_to_credentials "aft-management-admin" "${CREDENTIALS}"

  # Assume AWSAFTExecution in User Defined account
  echo "Generating credentials for ${AFT_EXECUTION_ROLE} in vended account account: ${AFT_MGMT_ACCOUNT}"
  CREDENTIALS=$(aws sts assume-role --role-arn "arn:aws:iam::${VENDED_ACCOUNT_ID}:role/${AFT_EXECUTION_ROLE}" --role-session-name "${ROLE_SESSION_NAME}" --profile aft-management-admin)
  write_to_credentials "aft-target" "${CREDENTIALS}"

  # Assume AWSAFTExecution in AFT Management account
  echo "Generating credentials for ${AFT_EXECUTION_ROLE} in aft-management account: ${AFT_MGMT_ACCOUNT}"
  CREDENTIALS=$(aws sts assume-role --role-arn "arn:aws:iam::${AFT_MGMT_ACCOUNT}:role/${AFT_EXECUTION_ROLE}" --role-session-name "${ROLE_SESSION_NAME}" --profile aft-management-admin)
  write_to_credentials "aft-management" "${CREDENTIALS}"

  # Assume AWSAFTExecution in CT Management account
  echo "Generating credentials for ${AFT_EXECUTION_ROLE} in ct-management account: ${CT_MGMT_ACCOUNT}"
  CREDENTIALS=$(aws sts assume-role --role-arn "arn:aws:iam::${CT_MGMT_ACCOUNT}:role/${AFT_EXECUTION_ROLE}" --role-session-name "${ROLE_SESSION_NAME}" --profile aft-management-admin)
  write_to_credentials "ct-management" "${CREDENTIALS}"

  # Assume AWSAFTExecution in Audit account
  echo "Generating credentials for ${AFT_EXECUTION_ROLE} in Audit account: ${AUDIT_ACCOUNT}"
  CREDENTIALS=$(aws sts assume-role --role-arn "arn:aws:iam::${AUDIT_ACCOUNT}:role/${AFT_EXECUTION_ROLE}" --role-session-name "${ROLE_SESSION_NAME}" --profile aft-management-admin)
  # Create credentials file
  write_to_credentials "ct-audit" "${CREDENTIALS}"

  # Assume AWSAFTExecution in Log Archive account
  echo "Generating credentials for ${AFT_EXECUTION_ROLE} in Log Archive account: ${LOG_ARCHIVE_ACCOUNT}"
  CREDENTIALS=$(aws sts assume-role --role-arn "arn:aws:iam::${LOG_ARCHIVE_ACCOUNT}:role/${AFT_EXECUTION_ROLE}" --role-session-name "${ROLE_SESSION_NAME}" --profile aft-management-admin)
  # Create credentials file
  write_to_credentials "ct-log-archive" "${CREDENTIALS}"
}

set -e
main
