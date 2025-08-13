# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
import logging
from functools import cached_property
from typing import TYPE_CHECKING, Optional

from aft_common.aft_utils import get_aws_partition
from aft_common.constants import (
    SSM_PARAM_ACCOUNT_AFT_MANAGEMENT_ACCOUNT_ID,
    SSM_PARAM_ACCOUNT_CT_MANAGEMENT_ACCOUNT_ID,
    SSM_PARAM_ACCOUNT_LOG_ARCHIVE_ACCOUNT_ID,
)
from aft_common.ssm import get_ssm_parameter_value
from boto3 import Session
from botocore.exceptions import ClientError

if TYPE_CHECKING:
    from mypy_boto3_sts import STSClient
    from mypy_boto3_sts.type_defs import AssumeRoleRequestTypeDef
else:
    STSClient = object
    AssumeRoleRequestTypeDef = object

logger = logging.getLogger("aft")


class AuthClient:
    SSM_PARAM_AFT_SESSION_NAME = "/aft/resources/iam/aft-session-name"
    SSM_PARAM_AFT_ADMIN_ROLE_NAME = "/aft/resources/iam/aft-administrator-role-name"
    SSM_PARAM_AFT_EXEC_ROLE_NAME = "/aft/resources/iam/aft-execution-role-name"
    CONTROL_TOWER_EXECUTION_ROLE_NAME = "AWSControlTowerExecution"

    def __init__(self, aft_management_session: Optional[Session] = None) -> None:
        if aft_management_session is None:
            aft_management_session = Session()
        if self._is_aft_management_session(session=aft_management_session):
            self.aft_management_account_id = aft_management_session.client(
                "sts"
            ).get_caller_identity()["Account"]
            self.aft_management_session = aft_management_session
        else:
            raise Exception("Unable to federate into AFT Management Account")

    @cached_property
    def _assume_role_session_name(self) -> str:
        return get_ssm_parameter_value(
            session=self.aft_management_session,
            param=AuthClient.SSM_PARAM_AFT_SESSION_NAME,
        )

    @staticmethod
    def _is_aft_management_session(session: Session) -> bool:
        try:
            aft_management_account_id = get_ssm_parameter_value(
                session=session, param=SSM_PARAM_ACCOUNT_AFT_MANAGEMENT_ACCOUNT_ID
            )
            caller_account_id = session.client("sts").get_caller_identity()["Account"]
            return caller_account_id == aft_management_account_id

        except ClientError as error:
            if error.response["Error"]["Code"] == "ParameterNotFound":
                return False
            else:
                raise error

    @staticmethod
    def _build_role_arn(partition: str, account_id: str, role_name: str) -> str:
        return f"arn:{partition}:iam::{account_id}:role/{role_name}"

    @staticmethod
    def _get_session(
        session: Session,
        role_arn: str,
        assume_role_session_name: str,
        assume_role_session_duration: int = 900,
        region: Optional[str] = None,
        session_policy: Optional[str] = None,
        external_id: Optional[str] = None,
    ) -> Session:
        sts: STSClient = session.client("sts")
        params: AssumeRoleRequestTypeDef = dict(
            RoleArn=role_arn,
            RoleSessionName=assume_role_session_name,
            DurationSeconds=assume_role_session_duration,
        )

        if external_id:
            params.update(dict(ExternalId=external_id))
        if session_policy:
            params.update(dict(Policy=session_policy))

        response = sts.assume_role(**params)
        credentials = response["Credentials"]
        return Session(
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
            region_name=region if region is not None else session.region_name,
        )

    @staticmethod
    def get_account_id_from_session(session: Session) -> str:
        return session.client("sts").get_caller_identity()["Account"]

    def _get_hub_session(self, session_duration: int = 900) -> Session:
        """
        Assumes a hub role, "AWSAFTAdmin" in the AFT Management account
        which is trusted by all "AWSAFTExecution" roles in all managed accounts
        """
        role_name = get_ssm_parameter_value(
            session=self.aft_management_session,
            param=AuthClient.SSM_PARAM_AFT_ADMIN_ROLE_NAME,
        )
        role_arn = AuthClient._build_role_arn(
            partition=get_aws_partition(session=self.aft_management_session),
            account_id=self.aft_management_account_id,
            role_name=role_name,
        )
        return AuthClient._get_session(
            session=self.aft_management_session,
            role_arn=role_arn,
            assume_role_session_name=self._assume_role_session_name,
            assume_role_session_duration=session_duration,
        )

    def get_aft_management_session(self) -> Session:
        return self.aft_management_session

    def get_target_account_session(
        self,
        account_id: str,
        hub_session: Optional[Session] = None,
        role_name: Optional[str] = None,
        region: Optional[str] = None,
        session_duration: int = 900,
        session_policy: Optional[str] = None,
    ) -> Session:
        """
        Leverages a hub session from AFT Management, and federates to a spoke IAM role within a target account
        """
        if hub_session is None:
            logger.info(
                "No hub session provided, creating default hub session using AWSAFTAdmin role"
            )
            hub_session = self._get_hub_session(session_duration=session_duration)

        hub_caller_identity = hub_session.client("sts").get_caller_identity()

        # Preserve behavior
        if role_name is None:
            logger.info("No role provided, using default AWSAFTExecution role")
            role_name = get_ssm_parameter_value(
                session=self.aft_management_session,
                param=AuthClient.SSM_PARAM_AFT_EXEC_ROLE_NAME,
            )

        spoke_role_arn = AuthClient._build_role_arn(
            partition=get_aws_partition(session=self.aft_management_session),
            account_id=account_id,
            role_name=role_name,
        )

        logger.info(
            f"Generating session using {hub_caller_identity['Arn']} for {spoke_role_arn}"
        )
        return AuthClient._get_session(
            session=hub_session,
            role_arn=spoke_role_arn,
            assume_role_session_name=self._assume_role_session_name,
            assume_role_session_duration=session_duration,
            region=region,
            session_policy=session_policy,
        )

    def get_ct_management_session(
        self,
        role_name: Optional[str] = None,
        region: Optional[str] = None,
        session_policy: Optional[str] = None,
        session_duration: int = 900,
    ) -> Session:
        account_id = get_ssm_parameter_value(
            session=self.aft_management_session,
            param=SSM_PARAM_ACCOUNT_CT_MANAGEMENT_ACCOUNT_ID,
        )
        return self.get_target_account_session(
            account_id=account_id,
            role_name=role_name,
            region=region,
            session_policy=session_policy,
            session_duration=session_duration,
        )

    def get_log_archive_session(
        self,
        role_name: Optional[str] = None,
        region: Optional[str] = None,
        session_policy: Optional[str] = None,
        session_duration: int = 900,
    ) -> Session:
        account_id = get_ssm_parameter_value(
            session=self.aft_management_session,
            param=SSM_PARAM_ACCOUNT_LOG_ARCHIVE_ACCOUNT_ID,
        )
        return self.get_target_account_session(
            account_id=account_id,
            role_name=role_name,
            region=region,
            session_policy=session_policy,
            session_duration=session_duration,
        )
