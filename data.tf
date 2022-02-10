# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
data "local_file" "version" {
  filename = "${path.module}/VERSION"
}
