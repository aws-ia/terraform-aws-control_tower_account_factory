# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import argparse

from aft_common import aft_utils as utils
from aft_common.metrics import AFTMetrics

logger = utils.get_logger()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Script called from within CodeBuild containers to report back AFT usage metrics"
    )

    parser.add_argument(
        "--codebuild-name", type=str, help="Name of the build container"
    )
    parser.add_argument(
        "--codebuild-status",
        type=int,
        help="Whether the build succeeded or not (1 or 0)",
    )

    args = parser.parse_args()

    codebuild_name = args.codebuild_name
    codebuild_status = "SUCCEEDED" if args.codebuild_status == 1 else "FAILED"

    try:
        aft_metrics = AFTMetrics()
        aft_metrics.post_event(action=args.codebuild_name, status=args.codebuild_status)
        logger.info(f"Successfully logged metrics. Action: {args.codebuild_name}")
    except Exception as e:
        logger.info(
            f"Unable to report metrics. Action: {args.codebuild_name}; Error: {e}"
        )
