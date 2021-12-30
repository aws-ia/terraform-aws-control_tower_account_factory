import inspect
import json
from typing import Any, Dict, Union

import aft_common.aft_utils as utils
import boto3
from boto3.session import Session

logger = utils.get_logger()


def get_account_request_record(session: Session, id: str) -> Dict[str, Any]:
    table_name = utils.get_ssm_parameter_value(
        session, utils.SSM_PARAM_AFT_DDB_REQ_TABLE
    )
    dynamodb = session.resource("dynamodb")
    table = dynamodb.Table(table_name)
    logger.info("Getting record for id " + id + " in DDB table " + table_name)
    response = table.get_item(Key={"id": id})
    logger.info(response)
    if "Item" in response:
        logger.info("Record found, returning item")
        logger.info(response["Item"])
        response_item: Dict[str, Any] = response["Item"]
        return response_item
    else:
        logger.info("Record not found in DDB table, exiting")
        sys.exit(1)


def is_customizations_event(event: Dict[str, Any]) -> bool:
    if "account_request" in event.keys():
        return True
    else:
        return False


def build_invoke_event(
    session: Session,
    ct_management_session: Session,
    event: Dict[str, Any],
    event_type: str,
) -> Dict[str, Any]:
    account_id: str = ""
    if event_type == "ControlTower":
        if event["detail"]["eventName"] == "CreateManagedAccount":
            account_id = event["detail"]["serviceEventDetails"][
                "createManagedAccountStatus"
            ]["account"]["accountId"]
        elif event["detail"]["eventName"] == "UpdateManagedAccount":
            account_id = event["detail"]["serviceEventDetails"][
                "updateManagedAccountStatus"
            ]["account"]["accountId"]
        account_email = utils.get_account_email_from_id(
            ct_management_session, account_id
        )
        ddb_record = get_account_request_record(session, account_email)
        invoke_event = {"control_tower_event": event, "account_request": ddb_record}
        # convert ddb strings into proper data type for json validation
        account_tags = json.loads(ddb_record["account_tags"])
        invoke_event["account_request"]["account_tags"] = account_tags
        invoke_event["account_provisioning"] = {}
        invoke_event["account_provisioning"]["run_create_pipeline"] = "true"
        logger.info("Invoking SFN with Event - ")
        logger.info(invoke_event)
        return invoke_event

    elif event_type == "Customizations":
        invoke_event = event
        # convert ddb strings into proper data type for json validation
        account_tags = json.loads(event["account_request"]["account_tags"])
        invoke_event["account_request"]["account_tags"] = account_tags
        invoke_event["account_provisioning"] = {}
        invoke_event["account_provisioning"]["run_create_pipeline"] = "true"
        logger.info("Invoking SFN with Event - ")
        logger.info(invoke_event)
        return invoke_event

    raise Exception("Unsupported event type")


def lambda_handler(event: Dict[str, Any], context: Union[Dict[str, Any], None]) -> None:
    try:
        logger.info("Lambda_handler Event")
        logger.info(event)
        session = boto3.session.Session()
        ct_management_session = utils.get_ct_management_session(session)
        response = None
        if utils.is_controltower_event(
            event
        ) and utils.is_aft_supported_controltower_event(event):
            logger.info("Control Tower Event Detected")
            invoke_event = build_invoke_event(
                session, ct_management_session, event, "ControlTower"
            )
            response = utils.invoke_step_function(
                session,
                utils.get_ssm_parameter_value(session, utils.SSM_PARAM_AFT_SFN_NAME),
                json.dumps(invoke_event),
            )
        elif is_customizations_event(event):
            logger.info("Account Customizations Event Detected")
            invoke_event = build_invoke_event(
                session, ct_management_session, event, "Customizations"
            )
            response = utils.invoke_step_function(
                session,
                utils.get_ssm_parameter_value(session, utils.SSM_PARAM_AFT_SFN_NAME),
                json.dumps(invoke_event),
            )
        logger.info(response)

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
