import inspect
import json
import os
import uuid
import boto3
from aft_common import aft_utils as utils

logger = utils.get_logger()


def new_ct_request_is_valid(session, request):
    try:
        logger.info("Validating new CT Account Request")
        org_account_emails = utils.get_org_account_emails(session)
        org_account_names = utils.get_org_account_names(session)

        ct_parameters = request["control_tower_parameters"]

        if ct_parameters["AccountEmail"] not in org_account_emails:
            logger.info(
                "Requested AccountEmail is valid: " + ct_parameters["AccountEmail"]
            )
            if ct_parameters["AccountName"] not in org_account_names:
                logger.info(
                    "Requested account_name is valid: " + ct_parameters["AccountName"]
                )
                return True
            else:
                logger.info(
                    "Requested AccountName is NOT valid: " + ct_parameters["AccountName"]
                )
                return False
        else:
            logger.info(f"Requested AccountEmail is NOT valid: {ct_parameters['AccountEmail']}")
            return False

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def modify_ct_request_is_valid(session, request):
    try:
        logger.info("Validating modify CT Account Request")

        old_ct_parameters = request["old_control_tower_parameters"]
        new_ct_parameters = request["control_tower_parameters"]

        for i in old_ct_parameters.keys():
            if i != "ManagedOrganizationalUnit":
                if old_ct_parameters[i] != new_ct_parameters[i]:
                    logger.info(i + " cannot be modified")
                    return False

        logger.info("Modify CT Account Request is Valid")
        return True

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def add_header(request, **kwargs):
    request.headers.add_header('User-Agent', 'account-factory-terraform-' + aft_version)


def create_new_account(session, ct_management_session, request):
    try:
        client = ct_management_session.client("servicecatalog")
        event_system = client.meta.events
        event_system.register_first('before-sign.*.*', add_header)
        provisioning_parameters = []

        for k, v in request["control_tower_parameters"].items():
            provisioning_parameters.append({"Key": k, "Value": v})

        logger.info(
            "Creating new account leveraging parameters: " + str(provisioning_parameters)
        )

        response = client.provision_product(
            ProductId=utils.get_ct_product_id(session, ct_management_session),
            ProvisioningArtifactId=utils.get_ct_provisioning_artifact_id(
                session, ct_management_session
            ),
            ProvisionedProductName=request["control_tower_parameters"]["AccountName"],
            ProvisioningParameters=provisioning_parameters,
            ProvisionToken=str(uuid.uuid1()),
        )
        logger.info(response)
        return response

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def modify_existing_account(session, ct_management_session, request):
    try:
        client = ct_management_session.client('servicecatalog')
        event_system = client.meta.events
        event_system.register_first('before-sign.*.*', add_header)
        provisioning_parameters = []
        for k, v in request['control_tower_parameters'].items():
            provisioning_parameters.append({"Key": k, "Value": v})

        # Get all provisioned product IDs for "CONTROL_TOWER_ACCOUNT" type
        provisioned_product_ids = []
        response = client.scan_provisioned_products(
            AccessLevelFilter={
                'Key': 'Account',
                'Value': 'self'
            },
        )
        for p in response['ProvisionedProducts']:
            if p['Type'] == 'CONTROL_TOWER_ACCOUNT':
                provisioned_product_ids.append({'Id': p['Id'], 'ProvisioningArtifactId': p['ProvisioningArtifactId']})

        for p in provisioned_product_ids:
            response = client.get_provisioned_product_outputs(
                ProvisionedProductId=p['Id'],
                OutputKeys=[
                    'AccountEmail',
                ]
            )
            if response['Outputs'][0]['OutputValue'] == request['control_tower_parameters']['AccountEmail']:
                target_product_id = p['Id']
                target_provisioning_artifact_id = p['ProvisioningArtifactId']

                logger.info("Modifying existing account leveraging parameters: " + str(
                    provisioning_parameters) + " with provisioned product ID " + target_product_id)
                response = client.update_provisioned_product(
                    ProvisionedProductId=target_product_id,
                    ProductId=utils.get_ct_product_id(session, ct_management_session),
                    ProvisioningArtifactId=target_provisioning_artifact_id,
                    ProvisioningParameters=provisioning_parameters,
                    UpdateToken=str(uuid.uuid1())
                )
                logger.info(response)
                break

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def lambda_handler(event, context):
    try:
        if event["offline"]:
            return True
    except KeyError:
        pass

    try:
        logger.info("Lambda_handler Event")
        logger.info(event)
        global aft_version

        session = boto3.session.Session()
        ct_management_session = utils.get_ct_management_session(session)
        aft_version = utils.get_ssm_parameter_value(session, "/aft/config/aft/version")

        if utils.product_provisioning_in_progress(
                ct_management_session,
                utils.get_ct_product_id(session, ct_management_session),
        ):
            logger.info("Exiting due to provisioning in progress")
            return 0
        else:
            sqs_message = utils.receive_sqs_message(
                session,
                utils.get_ssm_parameter_value(
                    session, utils.SSM_PARAM_ACCOUNT_REQUEST_QUEUE
                ),
            )
            if sqs_message is not None:
                sqs_body = json.loads(sqs_message["Body"])
                if sqs_body["operation"] == "INSERT":
                    if new_ct_request_is_valid(ct_management_session, sqs_body):
                        response = create_new_account(session, ct_management_session, sqs_body)
                elif sqs_body["operation"] == "MODIFY":
                    if modify_ct_request_is_valid(ct_management_session, sqs_body):
                        response = modify_existing_account(session, ct_management_session, sqs_body)
                else:
                    logger.info("Unknown operation received in message")

                utils.delete_sqs_message(session, sqs_message)
                return response

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
