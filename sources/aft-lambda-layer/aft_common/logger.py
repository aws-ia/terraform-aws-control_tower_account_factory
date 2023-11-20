# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
######################################################################################################################
#  Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.                                           #
#                                                                                                                    #
#  Licensed under the Apache License Version 2.0 (the "License"). You may not use this file except in compliance     #
#  with the License. A copy of the License is located at                                                             #
#                                                                                                                    #
#      http://www.apache.org/licenses/                                                                               #
#                                                                                                                    #
#  or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES #
#  OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions    #
#  and limitations under the License.                                                                                #
######################################################################################################################

import json
import logging
import os
from datetime import date, datetime
from json import JSONEncoder
from typing import TYPE_CHECKING, Any, MutableMapping, Tuple

from botocore.response import StreamingBody

if TYPE_CHECKING:
    LoggerAdapter = logging.LoggerAdapter[logging.Logger]
else:
    from logging import LoggerAdapter


_ORIGINAL_LOG_FACTORY = logging.getLogRecordFactory()


ACCOUNT_ID_FIELD_NAME = "account_id"
CUSTOMIZATION_REQUEST_ID_FIELD_NAME = "customization_request_id"


def _already_json_encoded(blob: str) -> bool:
    try:
        json.loads(blob)
        return True
    except (json.JSONDecodeError, TypeError):
        # TypeErrors are generated when attempting to loads an array/dict/obj
        return False


class _AFTEncoder(JSONEncoder):
    def default(self, obj: object) -> object:
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, StreamingBody):
            return obj.read().decode()
        else:
            return JSONEncoder.default(self, obj)


class _AccountCustomizationAdapter(LoggerAdapter):
    def process(
        self, message: str, kwargs: MutableMapping[str, Any]
    ) -> Tuple[str, MutableMapping[str, Any]]:
        # Handle optionality
        if self.extra is None:
            self.extra = {}
        log_tracing = {
            ACCOUNT_ID_FIELD_NAME: self.extra.get(ACCOUNT_ID_FIELD_NAME),
            CUSTOMIZATION_REQUEST_ID_FIELD_NAME: self.extra.get(
                CUSTOMIZATION_REQUEST_ID_FIELD_NAME
            ),
            "detail": message,
        }
        return (
            json.dumps(log_tracing, cls=_AFTEncoder),
            kwargs,
        )


def _aft_record_factory(*args: Any, **kwargs: Any) -> logging.LogRecord:
    record = _ORIGINAL_LOG_FACTORY(*args, **kwargs)
    if isinstance(record.msg, dict) or not _already_json_encoded(record.msg):
        record.msg = json.dumps(record.msg, cls=_AFTEncoder)
    return record


def _get_log_level() -> str:
    # Maintaining backwards compatibility, the old implementation defaults to INFO
    log_level = os.environ.get("log_level", "info")
    return log_level.upper()


def configure_aft_logger() -> None:
    fmt = '{"time_stamp": "%(asctime)s", "module": "%(module)s", "log_level": "%(levelname)s", "log_message": %(message)s}'
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        console = root_logger.handlers[0]
    else:
        console = logging.StreamHandler()
        root_logger.addHandler(console)
    console.setFormatter(logging.Formatter(fmt))

    aft_logger = logging.getLogger("aft")
    aft_logger.setLevel(_get_log_level())

    logging.setLogRecordFactory(_aft_record_factory)


def customization_request_logger(
    aws_account_id: str,
    customization_request_id: str,
) -> LoggerAdapter:
    configure_aft_logger()
    logger = logging.getLogger("aft.customization")
    return _AccountCustomizationAdapter(
        logger,
        extra={
            ACCOUNT_ID_FIELD_NAME: aws_account_id,
            CUSTOMIZATION_REQUEST_ID_FIELD_NAME: customization_request_id,
        },
    )
