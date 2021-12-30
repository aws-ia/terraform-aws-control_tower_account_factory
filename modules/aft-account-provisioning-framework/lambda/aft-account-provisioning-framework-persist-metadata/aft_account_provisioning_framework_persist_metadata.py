import inspect
from typing import Any, Dict, Union

import aft_common.aft_utils as utils
import boto3
from boto3.session import Session

logger = utils.get_logger()


def persist_metadata(
    payload: Dict[str, Any], account_info: Dict[str, str], session: Session
) -> Dict[str, Any]:

    logger.info("Function Start - persist_metadata")

    account_tags = payload["account_request"]["account_tags"]
    account_customizations_name = payload["account_request"][
        "account_customizations_name"
    ]
    metadata_table_name = utils.get_ssm_parameter_value(
        session, utils.SSM_PARAM_AFT_DDB_META_TABLE
    )

    item = {
        "id": account_info["id"],
        "email": account_info["email"],
        "account_name": account_info["name"],
        "account_creation_time": account_info["joined_date"],
        "account_status": account_info["status"],
        "account_level_tags": account_tags,
        "account_customizations_name": account_customizations_name,
        "parent_ou": account_info["parent_id"],
        "vcs_information": {},
        "terraform_workspace": {},
    }

    logger.info("Writing item to " + metadata_table_name)
    logger.info(item)

    response = utils.put_ddb_item(session, metadata_table_name, item)

    logger.info(response)
    return response


def lambda_handler(
    event: Dict[str, Any], context: Union[Dict[str, Any], None]
) -> Dict[str, Any]:
    try:
        logger.info("AFT Account Provisioning Framework Handler Start")

        rollback = None

        try:
            if event["rollback"]:
                rollback = True
        except KeyError:
            pass

        payload = event["payload"]
        action = event["action"]

        session = boto3.session.Session()

        if action == "persist_metadata":
            account_info = payload["account_info"]["account"]
            update_metadata = persist_metadata(payload, account_info, session)
            return update_metadata
        else:
            raise Exception(
                "Incorrect Command Passed to Lambda Function. Input: {action}. Expected: 'persist_metadata'"
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
