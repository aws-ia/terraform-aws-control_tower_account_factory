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
from typing import Any, Callable

from .datetime_encoder import DateTimeEncoder


class Logger(object):
    def __init__(self, loglevel: str = "warning") -> None:
        """Initializes logging"""
        self.config(loglevel=loglevel)
        return

    def config(self, loglevel: str = "warning") -> None:
        loglevel = logging.getLevelName(loglevel.upper())
        mainlogger = logging.getLogger()
        mainlogger.setLevel(loglevel)

        logfmt = '{"time_stamp": "%(asctime)s", "log_level": "%(levelname)s", "log_message": %(message)s}\n'
        if len(mainlogger.handlers) == 0:
            mainlogger.addHandler(logging.StreamHandler())
        mainlogger.handlers[0].setFormatter(logging.Formatter(logfmt))
        self.log = logging.LoggerAdapter(mainlogger, {})

    def _format(self, message: str) -> str:
        """formats log message in json

        Args:
        message (str): log message, can be a dict, list, string, or json blob
        """
        try:
            message = json.loads(message)
        except Exception:  # nosec try_except_pass
            pass
        try:
            return json.dumps(message, indent=4, cls=DateTimeEncoder)
        except Exception:
            return json.dumps(str(message))

    def debug(self, message: Any, **kwargs: Any) -> None:
        """wrapper for logging.debug call"""
        self.log.debug(self._format(message), **kwargs)

    def info(self, message: Any, **kwargs: Any) -> None:
        ## type: (object, object) -> object
        """wrapper for logging.info call"""
        self.log.info(self._format(message), **kwargs)

    def warning(self, message: Any, **kwargs: Any) -> None:
        """wrapper for logging.warning call"""
        self.log.warning(self._format(message), **kwargs)

    def error(self, message: Any, **kwargs: Any) -> None:
        """wrapper for logging.error call"""
        self.log.error(self._format(message), **kwargs)

    def critical(self, message: Any, **kwargs: Any) -> None:
        """wrapper for logging.critical call"""
        self.log.critical(self._format(message), **kwargs)

    def exception(self, message: Any, **kwargs: Any) -> None:
        """wrapper for logging.exception call"""
        self.log.exception(self._format(message), **kwargs)

    def log_unhandled_exception(self, message: Any) -> None:
        """log unhandled exception"""
        self.log.exception("Unhandled Exception: {}".format(message))

    def log_general_exception(
        self, file: Any, method: Callable[..., Any], exception: Exception
    ) -> None:
        """log general exception"""
        message = {"FILE": file, "METHOD": method, "EXCEPTION": str(exception)}
        self.log.exception(self._format(json.dumps(message)))
