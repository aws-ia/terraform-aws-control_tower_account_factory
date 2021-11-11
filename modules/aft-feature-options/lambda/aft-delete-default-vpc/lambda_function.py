import inspect
import os
import sys
import boto3
import botocore
import aft_common.aft_utils as utils

logger = utils.get_logger()


def get_aws_regions(client):
    try:
        logger.info("Describing Regions")
        response = client.describe_regions(
            AllRegions=False
        )
        region_list = []
        for r in response['Regions']:
            region_list.append(r['RegionName'])

        logger.info("Found " + str(len(region_list)) + " regions: " + str(region_list))
        return region_list

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def get_default_vpc(client):
    try:
        logger.info("Getting default VPC")
        response = client.describe_vpcs(
            Filters=[
                {
                    'Name': 'isDefault',
                    'Values': [
                        'true',
                    ]
                },
            ]
        )

        for v in response['Vpcs']:
            logger.info(v['VpcId'])
            return v['VpcId']
        logger.info("None")
        return None

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def delete_vpc(client, vpc):
    try:

        logger.info("Deleting VPC " + vpc)
        response = client.delete_vpc(
            VpcId=vpc,
        )

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def get_vpc_internet_gateways(resource, vpc):
    try:
        logger.info("Getting IGWs for VPC: " + vpc)
        vpc = resource.Vpc(vpc)
        igws = []
        for i in vpc.internet_gateways.all():
            igws.append(i.id)
        logger.info("SGs: " + str(igws))
        return igws

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def delete_internet_gateways(client, igws: list, vpc):
    try:
        for i in igws:
            logger.info("Detaching IGW " + i + " from " + vpc)
            response = client.detach_internet_gateway(
                InternetGatewayId=i,
                VpcId=vpc
            )
            logger.info("Deleting IGW " + i)
            response = client.delete_internet_gateway(
                InternetGatewayId=i
            )

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def get_vpc_subnets(resource, vpc):
    try:
        logger.info("Getting subnets for VPC: " + vpc)
        vpc = resource.Vpc(vpc)
        subnets = []
        for s in vpc.subnets.all():
            subnets.append(s.id)
        logger.info("Subnets: " + str(subnets))
        return subnets

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def delete_subnets(client, subnets: list):
    try:
        for s in subnets:
            logger.info("Deleting subnet " + s)
            response = client.delete_subnet(
                SubnetId=s,
            )

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def get_vpc_route_tables(resource, vpc):
    try:
        logger.info("Getting route tables for VPC: " + vpc)
        vpc = resource.Vpc(vpc)
        route_tables = []
        for rt in vpc.route_tables.all():
            route_tables.append(rt.id)
        logger.info("Route tables: " + str(route_tables))
        return route_tables

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def delete_route_tables(client, route_tables: list):
    try:
        for r in route_tables:
            logger.info("Describing route table " + r)
            response = client.describe_route_tables(
                RouteTableIds=[
                    r,
                ]
            )
            if response['RouteTables'][0]['Associations'][0]['Main']:
                continue
            else:
                logger.info("Deleting route table " + r)
                response = client.delete_route_table(
                    RouteTableId=r,
                )

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def get_vpc_acls(resource, vpc):
    try:
        logger.info("Getting ACLs for VPC: " + vpc)
        vpc = resource.Vpc(vpc)
        acls = []
        for a in vpc.network_acls.all():
            acls.append(a.id)
        logger.info("ACLs: " + str(acls))
        return acls

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def delete_acls(client, acls: list):
    try:
        for a in acls:
            logger.info("Describing ACL " + a)
            response = client.describe_network_acls(
                NetworkAclIds=[
                    a
                ]
            )
            if response['NetworkAcls'][0]['IsDefault']:
                continue
            else:
                logger.info("Deleting ACL " + a)
                response = client.delete_network_acl(
                    NetworkAclId=a,
                )

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def get_vpc_security_groups(resource, vpc):
    try:
        logger.info("Getting SGs for VPC: " + vpc)
        vpc = resource.Vpc(vpc)
        sgs = []
        for s in vpc.security_groups.all():
            sgs.append(s.id)
        logger.info("SGs: " + str(sgs))
        return sgs

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def delete_security_groups(client, security_groups: list):
    try:
        for s in security_groups:
            logger.info("Describing security group " + s)
            response = client.describe_security_groups(
                GroupIds=[
                    s,
                ]
            )
            if response['SecurityGroups'][0]['GroupName'] == 'default':
                continue
            else:
                logger.info("Deleting SG " + s)
                response = client.delete_security_group(
                    GroupId=s,
                )

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def lambda_handler(event, context):
    logger.info("Lambda_handler Event")
    logger.info(event)
    try:
        if event["offline"]:
            return True
    except KeyError:
        pass

    try:
        logger.info("Lambda_handler Event")
        logger.info(event)
        aft_session = boto3.session.Session()
        role_arn = utils.build_role_arn(aft_session,
                                        utils.get_ssm_parameter_value(aft_session, utils.SSM_PARAM_AFT_ADMIN_ROLE))
        aft_admin_session = utils.get_boto_session(utils.get_assume_role_credentials(aft_session, role_arn,
                                                                                     utils.get_ssm_parameter_value(
                                                                                         aft_session,
                                                                                         utils.SSM_PARAM_AFT_SESSION_NAME)))
        target_account = event['account_info']['account']['id']
        role_arn = utils.build_role_arn(aft_session,
                                        utils.get_ssm_parameter_value(aft_session, utils.SSM_PARAM_AFT_EXEC_ROLE),
                                        target_account)
        session = utils.get_boto_session(utils.get_assume_role_credentials(aft_admin_session, role_arn,
                                                                           utils.get_ssm_parameter_value(aft_session,
                                                                                                         utils.SSM_PARAM_AFT_SESSION_NAME)))
        client = session.client('ec2')
        regions = get_aws_regions(client)

        if utils.get_ssm_parameter_value(aft_session, utils.SSM_PARAM_FEATURE_DEFAULT_VPCS_ENABLED).lower() == 'true':
            for region in regions:
                logger.info("Creating boto3 session in " + region)
                session = boto3.session.Session(region_name=region)
                client = session.client('ec2')
                vpc = get_default_vpc(client)
                if vpc is not None:
                    resource = boto3.resource('ec2', region_name=region)
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
                    response = delete_vpc(client, vpc)

        return regions

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
