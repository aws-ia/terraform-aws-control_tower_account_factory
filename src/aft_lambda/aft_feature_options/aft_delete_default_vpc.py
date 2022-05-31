# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
from typing import TYPE_CHECKING, Any, Dict

import boto3
from aft_common import aft_utils as utils
from aft_common import notifications
from aft_common.account_provisioning_framework import ProvisionRoles
from aft_common.auth import AuthClient
from aft_common.feature_options import (
    delete_acls,
    delete_internet_gateways,
    delete_route_tables,
    delete_security_groups,
    delete_subnets,
    delete_vpc,
    get_aws_regions,
    get_default_vpc,
    get_vpc_acls,
    get_vpc_internet_gateways,
    get_vpc_route_tables,
    get_vpc_security_groups,
    get_vpc_subnets,
)

if TYPE_CHECKING:
    from mypy_boto3_ec2 import EC2Client, EC2ServiceResource
else:
    EC2Client = object
    EC2ServiceResource = object

if TYPE_CHECKING:
    from aws_lambda_powertools.utilities.typing import LambdaContext
else:
    LambdaContext = object

logger = utils.get_logger()


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> None:
    auth = AuthClient()
    aft_session = boto3.session.Session()
    try:
        target_account = event["account_info"]["account"]["id"]

        target_account_session = auth.get_target_account_session(
            account_id=target_account, role_name=ProvisionRoles.SERVICE_ROLE_NAME
        )
        client: EC2Client = target_account_session.client("ec2")
        regions = get_aws_regions(client)

        if (
            utils.get_ssm_parameter_value(
                aft_session, utils.SSM_PARAM_FEATURE_DEFAULT_VPCS_ENABLED
            ).lower()
            == "true"
        ):
            for region in regions:
                logger.info("Creating boto3 session in " + region)
                session = boto3.session.Session(region_name=region)
                client = session.client("ec2")
                vpc = get_default_vpc(client)
                if vpc is not None:
                    resource: EC2ServiceResource = boto3.resource(
                        "ec2", region_name=region
                    )
                    # Get Resources
                    subnets = get_vpc_subnets(resource, vpc)
                    route_tables = get_vpc_route_tables(resource, vpc)
                    acls = get_vpc_acls(resource, vpc)
                    security_groups = get_vpc_security_groups(resource, vpc)
                    internet_gateways = get_vpc_internet_gateways(resource, vpc)
                    # Delete Resources
                    delete_internet_gateways(client, internet_gateways, vpc)
                    delete_subnets(client, subnets)
                    delete_route_tables(client, route_tables)
                    delete_acls(client, acls)
                    delete_security_groups(client, security_groups)
                    delete_vpc(client, vpc)

    except Exception as error:
        notifications.send_lambda_failure_sns_message(
            session=aft_session,
            message=str(error),
            context=context,
            subject="AFT: Failed to delete default VPC",
        )
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(error),
        }
        logger.exception(message)
        raise
