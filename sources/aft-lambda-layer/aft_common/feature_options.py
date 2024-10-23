# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

import aft_common.aft_utils as utils
from boto3.session import Session
from botocore.exceptions import ClientError

if TYPE_CHECKING:
    from mypy_boto3_cloudtrail import CloudTrailClient
    from mypy_boto3_ec2 import EC2Client, EC2ServiceResource
else:
    EC2Client = object
    EC2ServiceResource = object
    CloudTrailClient = object

SUPPORT_API_REGION = "us-east-1"
CLOUDTRAIL_TRAIL_NAME = "aws-aft-CustomizationsCloudTrail"

logger = logging.getLogger("aft")


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
        describe_vpcs = client.get_paginator("describe_vpcs")
        for page in describe_vpcs.paginate(
            Filters=[
                {
                    "Name": "isDefault",
                    "Values": [
                        "true",
                    ],
                },
            ]
        ):
            for v in page["Vpcs"]:
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


def trail_exists(session: Session) -> bool:
    client: CloudTrailClient = session.client("cloudtrail")
    logger.info("Checking for trail " + CLOUDTRAIL_TRAIL_NAME)
    try:
        client.get_trail(Name=CLOUDTRAIL_TRAIL_NAME)
        logger.info("Trail already exists")
        return True
    except client.exceptions.TrailNotFoundException:
        logger.info("Trail does not exist")
        return False


def event_selectors_exists(session: Session) -> bool:
    client = session.client("cloudtrail")
    logger.info("Getting event selectors for " + CLOUDTRAIL_TRAIL_NAME)
    response = client.get_event_selectors(TrailName=CLOUDTRAIL_TRAIL_NAME)
    if "AdvancedEventSelectors" not in response:
        logger.info("No Advanced Event Selectors Found")
        return False
    else:
        logger.info("Advanced Events Selectors Found: ")
        logger.info(response["AdvancedEventSelectors"])
        return True


def trail_is_logging(session: Session) -> bool:
    client = session.client("cloudtrail")
    logger.info("Getting logging status for " + CLOUDTRAIL_TRAIL_NAME)
    response = client.get_trail_status(Name=CLOUDTRAIL_TRAIL_NAME)
    is_logging: bool = response["IsLogging"]
    return is_logging


def start_logging(session: Session) -> None:
    client = session.client("cloudtrail")
    logger.info("Starting Logging for " + CLOUDTRAIL_TRAIL_NAME)
    client.start_logging(Name=CLOUDTRAIL_TRAIL_NAME)


def create_trail(session: Session, s3_bucket: str, kms_key: str) -> None:
    client = session.client("cloudtrail")
    logger.info(
        "Creating trail "
        + CLOUDTRAIL_TRAIL_NAME
        + " leveraging S3 bucket "
        + s3_bucket
        + " and KMS key "
        + kms_key
    )
    client.create_trail(
        Name=CLOUDTRAIL_TRAIL_NAME,
        S3BucketName=s3_bucket,
        IncludeGlobalServiceEvents=True,
        IsMultiRegionTrail=True,
        EnableLogFileValidation=True,
        KmsKeyId=kms_key,
        IsOrganizationTrail=True,
    )


def put_event_selectors(session: Session, log_bucket_arns: List[str]) -> None:
    client = session.client("cloudtrail")
    logger.info("Putting Event Selectors")
    client.put_event_selectors(
        TrailName=CLOUDTRAIL_TRAIL_NAME,
        AdvancedEventSelectors=[
            {
                "Name": "No Log Archive Buckets",
                "FieldSelectors": [
                    {"Field": "eventCategory", "Equals": ["Data"]},
                    {"Field": "resources.type", "Equals": ["AWS::S3::Object"]},
                    {"Field": "resources.ARN", "NotEquals": log_bucket_arns},
                ],
            },
            {
                "Name": "Lamdba Functions",
                "FieldSelectors": [
                    {"Field": "eventCategory", "Equals": ["Data"]},
                    {
                        "Field": "resources.type",
                        "Equals": ["AWS::Lambda::Function"],
                    },
                ],
            },
        ],
    )


def get_log_bucket_arns(session: Session) -> List[str]:
    client = session.client("s3")
    logger.info("Building ARNs for buckets in log archive account: ")
    response = client.list_buckets()
    bucket_arns = []
    for b in response["Buckets"]:
        bucket_arns.append(
            f"arn:{utils.get_aws_partition(session)}:s3:::" + b["Name"] + "/*"
        )
    logger.info(str(bucket_arns))
    return bucket_arns


def get_target_account_and_customization_id_from_event(
    event: Dict[str, Any]
) -> Tuple[str, str]:
    request_id = event["customization_request_id"]
    target_account_id = event.get("account_info", {}).get("account", {}).get("id", "")
    if not target_account_id or not is_valid_account_id(target_account_id):
        raise ValueError(
            f"Event does not contain a valid target account ID: {target_account_id}"
        )
    return request_id, target_account_id


def is_valid_account_id(account_id: str) -> bool:
    return account_id.isdigit() and len(account_id) == 12
