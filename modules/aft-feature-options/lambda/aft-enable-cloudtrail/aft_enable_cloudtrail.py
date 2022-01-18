import inspect
from typing import TYPE_CHECKING, Any, Dict, List, Union

import aft_common.aft_utils as utils
import boto3
from boto3.session import Session

if TYPE_CHECKING:
    from mypy_boto3_cloudtrail import CloudTrailClient
else:
    CloudTrailClient = object

logger = utils.get_logger()

CLOUDTRAIL_TRAIL_NAME = "aws-aft-CustomizationsCloudTrail"


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
        bucket_arns.append("arn:aws:s3:::" + b["Name"] + "/*")
    logger.info(str(bucket_arns))
    return bucket_arns


def lambda_handler(event: Dict[str, Any], context: Union[Dict[str, Any], None]) -> None:
    try:
        logger.info("Lambda_handler Event")
        logger.info(event)
        aft_session = boto3.session.Session()
        ct_session = utils.get_ct_management_session(aft_session)
        log_archive_session = utils.get_log_archive_session(aft_session)

        # Get SSM Parameters
        cloudtrail_enabled = utils.get_ssm_parameter_value(
            aft_session, utils.SSM_PARAM_FEATURE_CLOUDTRAIL_DATA_EVENTS_ENABLED
        )
        s3_log_bucket_arn = utils.get_ssm_parameter_value(
            aft_session, "/aft/account/log-archive/log_bucket_arn"
        )
        s3_bucket_name = s3_log_bucket_arn.split(":::")[1]
        kms_key_arn = utils.get_ssm_parameter_value(
            aft_session, "/aft/account/log-archive/kms_key_arn"
        )
        log_bucket_arns = get_log_bucket_arns(log_archive_session)

        if cloudtrail_enabled == "true":
            if not trail_exists(ct_session):
                create_trail(ct_session, s3_bucket_name, kms_key_arn)
            if not event_selectors_exists(ct_session):
                put_event_selectors(ct_session, log_bucket_arns)
            if not trail_is_logging(ct_session):
                start_logging(ct_session)

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
