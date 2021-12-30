import inspect
from typing import TYPE_CHECKING, Any, Dict, List, Union

import aft_common.aft_utils as utils
import boto3
from boto3.session import Session

if TYPE_CHECKING:
    from mypy_boto3_organizations.type_defs import TagTypeDef
else:
    TagTypeDef = object

logger = utils.get_logger()


def tag_account(
    payload: Dict[str, Any],
    account_info: Dict[str, str],
    ct_management_session: Session,
    rollback: bool,
) -> None:
    logger.info("Start Function - tag_account")
    logger.info(payload)

    tags = payload["account_request"]["account_tags"]
    tag_list: List[TagTypeDef] = [{"Key": k, "Value": v} for k, v in tags.items()]
    utils.tag_org_resource(
        ct_management_session, account_info["id"], tag_list, rollback
    )


def lambda_handler(event: Dict[str, Any], context: Union[Dict[str, Any], None]) -> None:
    try:
        logger.info("AFT Account Provisioning Framework Handler Start")

        rollback = False
        try:
            if event["rollback"]:
                rollback = True
        except KeyError:
            pass

        payload = event["payload"]
        action = event["action"]

        session = boto3.session.Session()
        ct_management_session = utils.get_ct_management_session(session)

        if action == "tag_account":
            account_info = payload["account_info"]["account"]
            tag_account(payload, account_info, ct_management_session, rollback)
        else:
            raise Exception(
                "Incorrect Command Passed to Lambda Function. Input: {action}. Expected: 'tag_account'"
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
