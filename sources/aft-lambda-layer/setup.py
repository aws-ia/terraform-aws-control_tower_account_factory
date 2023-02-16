# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import setuptools

setuptools.setup(
    packages=setuptools.find_packages(),
    package_data={"aft_common": ["schemas/*.json"]},
)
