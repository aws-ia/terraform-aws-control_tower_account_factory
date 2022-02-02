import inspect
from typing import Any, Dict, Union

import aft_common.aft_utils as utils
from aft_common.customizations import get_running_pipeline_count, list_pipelines
from boto3.session import Session

logger = utils.get_logger()


def lambda_handler(
    event: Dict[str, Any], context: Union[Dict[str, Any], None]
) -> Dict[str, int]:

    logger.info("Lambda_handler Event")
    logger.info(event)

    try:
        session = Session()
        pipelines = list_pipelines(session)
        running_pipelines = get_running_pipeline_count(session, pipelines)

        return {"running_pipelines": running_pipelines}

    except Exception as e:
        message = {
            "FILE": __file__.split("/")[-1],
            "METHOD": inspect.stack()[0][3],
            "EXCEPTION": str(e),
        }
        logger.exception(message)
        raise
