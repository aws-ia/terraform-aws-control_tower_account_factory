# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import json
import logging
from typing import Any, Dict

from aft_common import aft_utils as utils
from aft_common import ddb
from aft_common.account_request_framework import (
    build_account_customization_payload,
    build_aft_account_provisioning_framework_event,
    insert_msg_into_acc_req_queue,
)
from aft_common.auth import AuthClient
from aft_common.organizations import OrganizationsAgent

logger = logging.getLogger("aft")


class AccountRequestRecordHandler:
    def __init__(self, auth: AuthClient, event: Dict[str, Any]) -> None:
        AccountRequestRecordHandler._validate_event(event=event)
        self._aft_management_session = auth.get_aft_management_session()
        self._ct_management_sesion = auth.get_ct_management_session()
        self.record = event["Records"][0]
        self._old_image = self.record["dynamodb"].get("OldImage")
        self._new_image = self.record["dynamodb"].get("NewImage")
        self.control_tower_parameters_updated = self._control_tower_parameters_changed()

    @property
    def is_update_action(self) -> bool:
        return all([self._old_image, self._new_image])

    @property
    def is_create_action(self) -> bool:
        return self._old_image is None and self._new_image is not None

    def _get_account_id(self, account_request: Dict[str, Any]) -> str:
        email = account_request["id"]
        orgs = OrganizationsAgent(ct_management_session=self._ct_management_sesion)
        return orgs.get_account_id_from_email(email=email)

    @staticmethod
    def _validate_event(event: Dict[str, Any]) -> None:
        try:
            if event["Records"][0]["eventSource"] != "aws:dynamodb":
                raise Exception("Invalid event source")
        except (KeyError, IndexError):
            raise Exception("Invalid event structure")

    def handle_remove(self) -> None:
        account_request = ddb.unmarshal_ddb_item(self._old_image)
        payload = {"account_request": account_request}

        lambda_name = utils.get_ssm_parameter_value(
            self._aft_management_session,
            utils.SSM_PARAM_AFT_CLEANUP_RESOURCES_LAMBDA,
        )
        utils.invoke_lambda(
            self._aft_management_session,
            lambda_name,
            json.dumps(payload).encode(),
        )
        return None

    def handle_account_request(self, new_account: bool) -> None:
        insert_msg_into_acc_req_queue(
            event_record=self.record,
            new_account=new_account,
            session=self._aft_management_session,
        )

    def _control_tower_parameters_changed(self) -> bool:
        if self.record["eventName"] == "MODIFY" and self.is_update_action:
            old_image = ddb.unmarshal_ddb_item(self._old_image)[
                "control_tower_parameters"
            ]
            new_image = ddb.unmarshal_ddb_item(self._new_image)[
                "control_tower_parameters"
            ]
            return bool(old_image != new_image)
        return False

    def handle_customization_request(self) -> None:
        account_request = ddb.unmarshal_ddb_item(self.record["dynamodb"]["NewImage"])
        account_id = self._get_account_id(
            account_request=account_request
        )  # Fetch from metadata/orgs?

        account_provisioning_payload = build_aft_account_provisioning_framework_event(
            self.record
        )
        account_customization_payload = build_account_customization_payload(
            ct_management_session=self._ct_management_sesion,
            account_id=account_id,
            account_request=account_request,
            control_tower_event=account_provisioning_payload,
        )
        account_provisioning_stepfunction = utils.get_ssm_parameter_value(
            self._aft_management_session, utils.SSM_PARAM_AFT_SFN_NAME
        )

        utils.invoke_step_function(
            session=self._aft_management_session,
            sfn_name=account_provisioning_stepfunction,
            input=json.dumps(account_customization_payload),
        )
