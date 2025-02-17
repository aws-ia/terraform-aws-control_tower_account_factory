#!/usr/bin/python
# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import os
import time
from typing import Any

import requests

LOCAL_CONFIGURATION_PATH = ""
TOFU_VERSION = ""


def init(tf_version, config_path):
    global TOFU_VERSION
    global LOCAL_CONFIGURATION_PATH

    TOFU_VERSION = tf_version
    LOCAL_CONFIGURATION_PATH = config_path


class ClientError(Exception):
    def __init__(self, status, message):
        self.status = status
        super().__init__(message)
