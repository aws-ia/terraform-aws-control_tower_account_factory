import inspect
import os
import json
import boto3
import jsonschema
import aft_common.aft_utils as utils

logger = utils.get_logger()

AFT_PIPELINE_ACCOUNTS = ["ct-management", "log-archive", "audit"]


def validate_request(payload):
    logger.info("Function Start - validate_request")
    schema_path = os.path.join(os.path.dirname(__file__), "schema/request_schema.json")
    with open(schema_path) as schema_file:
        schema_object = json.load(schema_file)
    logger.info("Schema Loaded:" + json.dumps(schema_object))
    validated = jsonschema.validate(payload, schema_object)
    if validated is None:
        logger.info("Request Validated")
        return True
    else:
        raise Exception("Failure validating request.\n{validated}")


def filter_non_aft_accounts(session, account_list, operation="include"):
    aft_accounts = utils.get_all_aft_account_ids(session)
    core_accounts = get_core_accounts(session)
    logger.info("Running AFT Filter for accounts " + str(account_list))
    filtered_accounts = []
    for a in account_list:
        logger.info("Evaluating account " + a)
        if a not in aft_accounts:
            if operation == "include":
                if a not in core_accounts:
                    logger.info("Account " + a + " is being filtered.")
                    filtered_accounts.append(a)
                else:
                    logger.info("Account " + a + " is NOT being filtered.")
        else:
            logger.info("Account " + a + " is NOT being filtered.")
    for a in filtered_accounts:
        if a in account_list:
            account_list.remove(a)
    return account_list


def get_core_accounts(session):
    try:
        core_accounts = []
        logger.info("Getting core accounts -")
        for a in AFT_PIPELINE_ACCOUNTS:
            id = utils.get_ssm_parameter_value(session, '/aft/account/' + a + '/account-id')
            logger.info("Account ID for " + a + " is " + id)
            core_accounts.append(id)
        logger.info("Core accounts: " + str(core_accounts))
        return core_accounts

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def get_included_accounts(session, ct_mgmt_session, included: list):
    try:
        all_aft_accounts = utils.get_all_aft_account_ids(session)
        logger.info("All AFT accounts: " + str(all_aft_accounts))
        included_accounts = []
        for d in included:
            if d['type'] == 'all':
                if all_aft_accounts is not None:
                    included_accounts.extend(all_aft_accounts)
            if d['type'] == 'core':
                core_accounts = get_core_accounts(session)
                included_accounts.extend(core_accounts)
            if d['type'] == 'ous':
                ou_accounts = utils.get_account_ids_in_ous(ct_mgmt_session, d['target_value'])
                if ou_accounts is not None:
                    included_accounts.extend(ou_accounts)
            if d['type'] == 'tags':
                tag_accounts = utils.get_accounts_by_tags(session, ct_mgmt_session, d['target_value'])
                if tag_accounts is not None:
                    included_accounts.extend(tag_accounts)
            if d['type'] == 'accounts':
                included_accounts.extend(d['target_value'])
        # Remove Duplicates
        included_accounts = list(set(included_accounts))
        logger.info("Included Accounts (pre-AFT filter): " + str(included_accounts))

        # Filter non-AFT accounts
        included_accounts = filter_non_aft_accounts(session, included_accounts)

        logger.info("Included Accounts (post-AFT filter): " + str(included_accounts))
        return included_accounts

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def get_excluded_accounts(session, ct_mgmt_session, excluded: list):
    try:
        excluded_accounts = []
        for d in excluded:
            if d['type'] == 'core':
                core_accounts = get_core_accounts(session)
                excluded_accounts.extend(core_accounts)
            if d['type'] == 'ous':
                ou_accounts = utils.get_account_ids_in_ous(ct_mgmt_session, d['target_value'])
                if ou_accounts is not None:
                    excluded_accounts.extend(ou_accounts)
            if d['type'] == 'tags':
                tag_accounts = utils.get_accounts_by_tags(session, ct_mgmt_session, d['target_value'])
                if tag_accounts is not None:
                    excluded_accounts.extend(tag_accounts)
            if d['type'] == 'accounts':
                excluded_accounts.extend(d['target_value'])
        # Remove Duplicates
        excluded_accounts = list(set(excluded_accounts))
        logger.info("Excluded Accounts (pre-AFT filter): " + str(excluded_accounts))

        # Filter non-AFT accounts
        excluded_accounts = filter_non_aft_accounts(session, excluded_accounts, "exclude")

        logger.info("Excluded Accounts (post-AFT filter): " + str(excluded_accounts))
        return excluded_accounts

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise


def get_target_accounts(included_accounts, excluded_accounts):
    for i in excluded_accounts:
        if i in included_accounts:
            included_accounts.remove(i)
    logger.info("TARGET ACCOUNTS: " + str(included_accounts))
    return included_accounts


def lambda_handler(event, context):
    logger.info("Lambda_handler Event")
    logger.info(event)
    try:
        if event["offline"]:
            return True
    except KeyError:
        pass

    try:
        payload = event
        if not validate_request(payload):
            sys.exit(1)
        else:
            session = boto3.session.Session()
            ct_mgmt_session = utils.get_ct_management_session(session)
            included_accounts = get_included_accounts(session, ct_mgmt_session, payload['include'])
            if 'exclude' in payload.keys():
                excluded_accounts = get_excluded_accounts(session, ct_mgmt_session, payload['exclude'])
                target_accounts = get_target_accounts(included_accounts, excluded_accounts)
            else:
                target_accounts = included_accounts

            return {
                'number_pending_accounts': len(target_accounts),
                'pending_accounts': target_accounts
            }

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
