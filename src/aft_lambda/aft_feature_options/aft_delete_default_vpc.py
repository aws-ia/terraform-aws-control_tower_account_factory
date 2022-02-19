# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import inspect
from typing import TYPE_CHECKING, Any, Dict, Union

import aft_common.aft_utils as utils
import boto3
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

logger = utils.get_logger()


def lambda_handler(event: Dict[str, Any], context: Union[Dict[str, Any], None]) -> None:
    logger.info("Lambda_handler Event")
    logger.info(event)

    try:
        logger.info("Lambda_handler Event")
        logger.info(event)
        aft_session = boto3.session.Session()
        role_arn = utils.build_role_arn(
            aft_session,
            utils.get_ssm_parameter_value(aft_session, utils.SSM_PARAM_AFT_ADMIN_ROLE),
        )
        aft_admin_session = utils.get_boto_session(
            utils.get_assume_role_credentials(
                aft_session,
                role_arn,
                utils.get_ssm_parameter_value(
                    aft_session, utils.SSM_PARAM_AFT_SESSION_NAME
                ),
            )
        )
        target_account = event["account_info"]["account"]["id"]
        role_arn = utils.build_role_arn(
            aft_session,
            utils.get_ssm_parameter_value(aft_session, utils.SSM_PARAM_AFT_EXEC_ROLE),
            target_account,
        )
        session = utils.get_boto_session(
            utils.get_assume_role_credentials(
                aft_admin_session,
                role_arn,
                utils.get_ssm_parameter_value(
                    aft_session, utils.SSM_PARAM_AFT_SESSION_NAME
                ),
            )
        )
        client: EC2Client = session.client("ec2")
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

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise
