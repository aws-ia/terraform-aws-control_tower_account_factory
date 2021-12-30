import inspect
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import aft_common.aft_utils as utils
import boto3
from botocore.exceptions import ClientError

if TYPE_CHECKING:
    from mypy_boto3_ec2 import EC2Client, EC2ServiceResource
else:
    EC2Client = object
    EC2ServiceResource = object

logger = utils.get_logger()


def get_aws_regions(client: EC2Client) -> List[str]:
    logger.info("Describing Regions")
    response = client.describe_regions(AllRegions=False)
    region_list = []
    for r in response["Regions"]:
        region_list.append(r["RegionName"])

    logger.info("Found " + str(len(region_list)) + " regions: " + str(region_list))
    return region_list


def get_default_vpc(client: EC2Client) -> Optional[str]:
    logger.info("Getting default VPC")
    try:
        response = client.describe_vpcs(
            Filters=[
                {
                    "Name": "isDefault",
                    "Values": [
                        "true",
                    ],
                },
            ]
        )
        for v in response["Vpcs"]:
            vpc_id: str = v["VpcId"]
            logger.info(vpc_id)
            return vpc_id
        return None
    except ClientError as e:
        region = client.meta.region_name
        error_code = e.response["Error"]["Code"]
        if error_code == "UnauthorizedOperation":
            logger.info(
                "UnauthorizedOperation encountered getting default VPC for " + region
            )
        return None


def delete_vpc(client: EC2Client, vpc: str) -> None:
    logger.info("Deleting VPC " + vpc)
    client.delete_vpc(
        VpcId=vpc,
    )


def get_vpc_internet_gateways(resource: EC2ServiceResource, vpc: str) -> List[str]:
    logger.info("Getting IGWs for VPC: " + vpc)
    vpc_resource = resource.Vpc(vpc)
    igws = []
    for i in vpc_resource.internet_gateways.all():
        igws.append(i.id)
    logger.info("SGs: " + str(igws))
    return igws


def delete_internet_gateways(client: EC2Client, igws: List[str], vpc: str) -> None:
    for i in igws:
        logger.info("Detaching IGW " + i + " from " + vpc)
        client.detach_internet_gateway(InternetGatewayId=i, VpcId=vpc)
        logger.info("Deleting IGW " + i)
        client.delete_internet_gateway(InternetGatewayId=i)


def get_vpc_subnets(resource: EC2ServiceResource, vpc: str) -> List[str]:
    logger.info("Getting subnets for VPC: " + vpc)
    vpc_resource = resource.Vpc(vpc)
    subnets = []
    for s in vpc_resource.subnets.all():
        subnets.append(s.id)
    logger.info("Subnets: " + str(subnets))
    return subnets


def delete_subnets(client: EC2Client, subnets: List[str]) -> None:
    for s in subnets:
        logger.info("Deleting subnet " + s)
        client.delete_subnet(
            SubnetId=s,
        )


def get_vpc_route_tables(resource: EC2ServiceResource, vpc: str) -> List[str]:
    logger.info("Getting route tables for VPC: " + vpc)
    vpc_resource = resource.Vpc(vpc)
    route_tables = []
    for rt in vpc_resource.route_tables.all():
        route_tables.append(rt.id)
    logger.info("Route tables: " + str(route_tables))
    return route_tables


def delete_route_tables(client: EC2Client, route_tables: List[str]) -> None:
    for r in route_tables:
        logger.info("Describing route table " + r)
        response = client.describe_route_tables(
            RouteTableIds=[
                r,
            ]
        )
        if response["RouteTables"][0]["Associations"][0]["Main"]:
            continue
        else:
            logger.info("Deleting route table " + r)
            client.delete_route_table(
                RouteTableId=r,
            )


def get_vpc_acls(resource: EC2ServiceResource, vpc: str) -> List[str]:
    logger.info("Getting ACLs for VPC: " + vpc)
    vpc_resource = resource.Vpc(vpc)
    acls = []
    for a in vpc_resource.network_acls.all():
        acls.append(a.id)
    logger.info("ACLs: " + str(acls))
    return acls


def delete_acls(client: EC2Client, acls: List[str]) -> None:
    for a in acls:
        logger.info("Describing ACL " + a)
        response = client.describe_network_acls(NetworkAclIds=[a])
        if response["NetworkAcls"][0]["IsDefault"]:
            continue
        else:
            logger.info("Deleting ACL " + a)
            client.delete_network_acl(
                NetworkAclId=a,
            )


def get_vpc_security_groups(resource: EC2ServiceResource, vpc: str) -> List[str]:
    logger.info("Getting SGs for VPC: " + vpc)
    vpc_resource = resource.Vpc(vpc)
    sgs = []
    for s in vpc_resource.security_groups.all():
        sgs.append(s.id)
    logger.info("SGs: " + str(sgs))
    return sgs


def delete_security_groups(client: EC2Client, security_groups: List[str]) -> None:
    for s in security_groups:
        logger.info("Describing security group " + s)
        response = client.describe_security_groups(
            GroupIds=[
                s,
            ]
        )
        if response["SecurityGroups"][0]["GroupName"] == "default":
            continue
        else:
            logger.info("Deleting SG " + s)
            client.delete_security_group(
                GroupId=s,
            )


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
        client = session.client("ec2")
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
                    resource = boto3.resource("ec2", region_name=region)
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


if __name__ == "__main__":
    import json
    import sys
    from optparse import OptionParser

    logger.info("Local Execution")
    parser = OptionParser()
    parser.add_option(
        "-f", "--event-file", dest="event_file", help="Event file to be processed"
    )
    (options, args) = parser.parse_args(sys.argv)
    if options.event_file is not None:
        with open(options.event_file) as json_data:
            event = json.load(json_data)
            lambda_handler(event, None)
    else:
        lambda_handler({}, None)
