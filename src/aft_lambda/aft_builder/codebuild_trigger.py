# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import datetime
import inspect
import logging
import time
from typing import Any, Dict, TypedDict

from boto3.session import Session

logger = logging.getLogger()
logger.setLevel(level=logging.INFO)


class LayerBuildStatus(TypedDict):
    Status: int


# This function is directly responsible for building `aft_common` library
# Do not import  `aft_common` into this handler!
def lambda_handler(event: Dict[str, Any], context: Dict[str, Any]) -> LayerBuildStatus:
    session = Session()
    try:
        client = session.client("codebuild")

        codebuild_project_name = event["codebuild_project_name"]
        job_id = client.start_build(projectName=codebuild_project_name)["build"]["id"]

        logger.info(f"Started build project {codebuild_project_name} job {job_id}")

        # Wait at least 30 seconds for the build to initialize
        time.sleep(30)

        # 15min Lambda hard-timeout, soft-timeout at 14min
        end_time = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=14)
        while datetime.datetime.now(datetime.UTC) <= end_time:
            # We pass exactly 1 job ID, so the build list should contain exactly 1 object
            job_status = client.batch_get_builds(ids=[job_id])["builds"][0][
                "buildStatus"
            ]
            if job_status == "IN_PROGRESS":
                time.sleep(10)
                continue
            elif job_status == "SUCCEEDED":
                logger.info(f"Build job {job_id} completed successfully")
                return {"Status": 200}
            else:
                logger.info(f"Build {job_id} failed - non-success terminal status")
                raise Exception(f"Build {job_id} failed - non-success terminal status")

        logger.info(f"Build {job_id} failed - time out")
        raise Exception(f"Build {job_id} failed - time out")

    except Exception as error:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(error),
        }
        logger.exception(message)
        raise
