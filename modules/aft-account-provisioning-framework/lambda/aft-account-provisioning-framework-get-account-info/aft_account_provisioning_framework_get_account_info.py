import inspect
from typing import Any, Dict, Union

import aft_common.aft_utils as utils
import boto3
from aft_common.account import AftAccountInfo
from boto3.session import Session

logger = utils.get_logger()


def get_ct_execution_session(
    aft_management_session: Session, ct_management_session: Session, account_id: str
) -> Session:
    session_name = utils.get_ssm_parameter_value(
        aft_management_session, utils.SSM_PARAM_AFT_SESSION_NAME
    )
    admin_credentials = utils.get_assume_role_credentials(
        ct_management_session,
        utils.build_role_arn(
            ct_management_session, "AWSControlTowerExecution", account_id
        ),
        session_name,
    )

    return utils.get_boto_session(admin_credentials)


def get_account_info(
    payload: Dict[str, Any], session: Session, ct_management_session: Session
) -> AftAccountInfo:
    logger.info("Function Start - get_account_info")

    account_id = None

    # Handle a Control Tower Event
    if "account" in payload["control_tower_event"]:
        if (
            payload["control_tower_event"]["detail"]["eventName"]
            == "CreateManagedAccount"
        ):
            account_id = payload["control_tower_event"]["detail"][
                "serviceEventDetails"
            ]["createManagedAccountStatus"]["account"]["accountId"]
        elif (
            payload["control_tower_event"]["detail"]["eventName"]
            == "UpdateManagedAccount"
        ):
            account_id = payload["control_tower_event"]["detail"][
                "serviceEventDetails"
            ]["updateManagedAccountStatus"]["account"]["accountId"]
        if account_id:
            logger.info(f"Account Id [{account_id}] found in control_tower_event")
            return utils.get_account_info(ct_management_session, account_id)

    elif "id" in payload["account_request"]:
        email = payload["account_request"]["id"]
        logger.info("Account Email: " + email)
        account_id = utils.get_account_id_from_email(ct_management_session, email)
        return utils.get_account_info(ct_management_session, account_id)

    raise Exception("Account was not found")


def lambda_handler(
    event: Dict[str, Any], context: Union[Dict[str, Any], None]
) -> AftAccountInfo:
    try:
        logger.info("AFT Account Provisioning Framework Get Account Info Handler Start")

        payload = event["payload"]
        action = event["action"]

        session = boto3.session.Session()
        ct_management_session = utils.get_ct_management_session(session)
        if action == "get_account_info":
            return get_account_info(payload, session, ct_management_session)
        else:
            raise Exception(
                "Incorrect Command Passed to Lambda Function. Input: {action}. Expected: 'get_account_info'"
            )

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
