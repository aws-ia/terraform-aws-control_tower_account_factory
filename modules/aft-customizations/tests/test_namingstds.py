import os
import logging
import pprint
import sys
import json
import jsonschema
import pytest

@pytest.mark.unit
def test_naming_violations(plan):
    result = {}
    violations = plan["violations"]
    print(violations)
    table = [[v, len(violations[v])] for v in violations]
    print(violations)
    for t in table:
        assert {t[1]} == 0
