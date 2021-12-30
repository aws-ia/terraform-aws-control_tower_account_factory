import logging
import os
import pprint

import pytest

pp = pprint.PrettyPrinter(indent=4, depth=6)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)-8s %(message)s",
)

from tf_analyzer import tfAnalyzer

BASE_DIR = os.path.join(os.path.dirname(__file__))
fixture_path = "."


def pytest_generate_tests(metafunc):
    os.environ["local_configuration_path"] = "./testdata/temp_configuration_file.tar.gz"
    os.environ["terraform_version"] = "0.15.5"
    os.environ["terraform_api_endpoint"] = "https://app.terraform.io/api/v2"


@pytest.fixture
def plan():
    plan_file = "./tfplan.json"
    tf = tfAnalyzer()
    tf.load_plan(plan_file)
    results = {}
    results["plan_analysis"] = tf.analyze_plan()
    resources = tf.get_modules()
    results["modules"] = resources
    violations = tf.check_naming_violations(resources)
    results["violations"] = violations
    return results
