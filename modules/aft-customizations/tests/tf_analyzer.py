#! /usr/bin/env python3

import logging
import pprint

from common import load_json
from tabulate import tabulate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
pp = pprint.PrettyPrinter(indent=4)

default_config = {
    "resource_categories": [
        "iam",
        "vpc",
        "lambda",
        "db",
        "config",
        "ssm",
        "cloudwatch",
        "event",
        "null_resource",
    ],
    "actions": ["create", "update", "delete"],
}


class tfAnalyzer:
    """Class that analyzes terraform plans"""

    _config = None
    _plan = None
    _report_dir = None

    def __init__(self, config_file=None):
        if config_file:
            self._config = load_json(config_file)
        else:
            self._config = default_config

    def load_plan(self, plan_file):
        self._plan = load_json(plan_file)

    def get_modules(self):
        result = {}
        if "child_modules" in self._plan["planned_values"]["root_module"].keys():
            root_module = self._plan["planned_values"]["root_module"]["child_modules"][
                0
            ]
            root_address = root_module["address"]
        else:
            root_module = self._plan["planned_values"]["root_module"]
            root_address = "."

        resources = []
        if "resources" in root_module.keys():
            resources = root_module["resources"]
        if not "child_modules" in root_module.keys():
            root_module["child_modules"] = {}
        result[root_address] = {
            "child_modules": root_module["child_modules"],
            "resources": resources,
        }
        for m in root_module["child_modules"]:
            child_modules = []
            if "child_modules" in m.keys():
                child_modules = m["child_modules"]
            result[m["address"]] = {
                "resources": m["resources"],
                "child_modules": child_modules,
            }
        print(result.keys())
        return result

    def check_naming_violations(self, results):
        by_violations = {}
        for m in results.keys():
            print(f"Analyzing the naming standards for resources: {m}")
            if not results[m]["resources"]:
                continue
            for r in results[m]["resources"]:
                if "-" in r["name"]:
                    logger.debug(f"GN01: violation for {r}")
                aws_resource_name = None
                name_keys_map = {
                    "aws_lambda_function": "function_name",
                    "aws_lambda_layer_version": "layer_name",
                    "aws_lambda_permission": "function_name",
                }
                tf_resource_types_without_named_aws_resources = [
                    "aws_iam_role_policy_attachment",
                    "aws_lambda_permission",
                    "aws_lambda_event_source_mapping",
                    "time_sleep",
                    "aws_cloudwatch_event_target",
                    "archive_file",
                    "aws_cloudwatch_event_permission",
                ]

                # check-RN01 violations
                if r["type"].split("_")[-1] in r["name"]:
                    logger.debug(f'RN01: {r["type"]} : {r["name"]}')
                    if not "RN01" in by_violations.keys():
                        by_violations["RN01"] = []
                    by_violations["RN01"].append(
                        {
                            "resource": r,
                            "msg": f'{r["name"]} has {r["type"].split("_")[-1]} in the name',
                        }
                    )
                ## check-GN01 violations
                if "-" in r["name"]:
                    logger.debug(f"GN01 --> {r['name']} : {r['type']}")
                    if not "GN01" in by_violations.keys():
                        by_violations["GN01"] = []
                    by_violations["GN01"].append(
                        {"resource": r, "msg": f"{r['name']} has - in the name"}
                    )
                ## check-GN02 violations
                if (
                    "values" in r
                    and r["type"] not in tf_resource_types_without_named_aws_resources
                ):
                    key = "name"
                    # print(r)
                    if r["type"] in name_keys_map.keys():
                        key = name_keys_map[r["type"]]
                    if key not in r["values"]:
                        logger.warning(
                            f"WARN: {key} does not exists in values for {r['type']}"
                        )
                    else:
                        aws_resource_name = r["values"][key]
                        if aws_resource_name:
                            if "_" in aws_resource_name:
                                logger.debug(
                                    f"GN02: violation for {aws_resource_name} ==> {r['name']}, {r['type']}"
                                )
                                if not "GN02" in by_violations.keys():
                                    by_violations["GN02"] = []
                                by_violations["GN02"].append(
                                    {
                                        "resource": r,
                                        "msg": f"{aws_resource_name} has _ in the aws_resource name",
                                    }
                                )
        return by_violations

    def analyze_plan(self):
        count = 0
        results = {}
        by_resource_categories = {}
        by_resource_type = {}
        by_action = {}
        by_naming_violations = {}
        total_naming_violations = 0
        for rc in self._plan["resource_changes"]:
            if rc["change"]["actions"][0] not in ["no-op", "read"]:
                count = count + 1
                logger.debug(f'{rc["type"]} : {rc["name"]}')
                # resource_type
                if rc["type"] not in by_resource_type:
                    by_resource_type[rc["type"]] = []
                by_resource_type[rc["type"]].append(rc)

                # by_action
                action = rc["change"]["actions"][0]
                if action not in by_action:
                    by_action[action] = []
                by_action[action].append(rc)

                # resource_category
                for key in self._config["resource_categories"]:
                    if key in rc["type"]:
                        if key not in by_resource_categories:
                            by_resource_categories[key] = []
                        by_resource_categories[key].append(rc)

        # collect results
        table = [[r, len(by_resource_type[r])] for r in by_resource_type]
        # print(table)
        logger.debug(tabulate(table, ["Resouce_Type", "Count"], tablefmt="github"))

        # print(f"Analysis by Action")
        table = [[r, len(by_action[r])] for r in by_action]
        # print(table)
        logger.debug(tabulate(table, ["Action", "Count"], tablefmt="github"))

        # print(f"Analysis by resource category")
        table = [[r, len(by_resource_categories[r])] for r in by_resource_categories]
        logger.debug(tabulate(table, ["Category", "Count"], tablefmt="github"))
        results["by_categories"] = by_resource_categories
        results["by_action"] = by_action
        results["by_resource_type"] = by_resource_type

        return results


if __name__ == "__main__":
    import sys
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option(
        "-f", "--plan_file", dest="plan_file", help="terraform plan in json format"
    )
    parser.add_option("-c", "--config_file", dest="config_file", help="config")
    (options, args) = parser.parse_args(sys.argv)
    pp.pprint(options)
    tf = tfAnalyzer(options.config_file)
    tf.load_plan(options.plan_file)
    results = tf.analyze_plan()
    counts = {}
    for key in results.keys():
        print(f"Analysis for {key}")
        # print(results[key])
        # table = [[r, len(by_resource_type[r])] for r in by_resource_type]
        table = [[r, len(results[key][r])] for r in results[key]]
        counts[key] = table

        print(tabulate(table, ["Type", "Count"], tablefmt="github"))

    modules = tf.get_modules()
    table = [
        [m, len(modules[m]["child_modules"]), len(modules[m]["resources"])]
        for m in modules
    ]
    print(tabulate(table, ["module", "child-modules", "resources"], tablefmt="github"))
    # print(json.dumps(table))
    # print(resources.keys())
    violations = tf.check_naming_violations(modules)
    table = [[v, len(violations[v])] for v in violations]
    # counts["violations"] = table
    print(tabulate(table, ["ViolationType", "Count"], tablefmt="github"))
    # print(json.dumps(counts))
