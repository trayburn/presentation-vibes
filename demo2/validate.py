#!/usr/bin/env python3
"""
Demo 2 — Structured Data Validator

This script validates the structured YAML output from the unstructured-to-structured
conversion step. It checks:

1. YAML is parseable
2. All required top-level keys are present
3. All required fields in nested objects are present and non-null
4. Data types are correct (string, integer, boolean, array, object)
5. Enum values are valid
6. Business rules have enforcement_point in {domain, api, ui}
7. API methods are valid HTTP verbs
8. No "MISSING FROM SOURCE" comments remain (indicates incomplete extraction)

Usage:
    python3 validate.py <yaml-file>

Exit codes:
    0 = all validations passed
    1 = one or more validations failed
"""

import sys
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)


# --- Validation Rules ---

REQUIRED_TOP_KEYS = {
    "project", "tech_stack", "data_model", "business_rules",
    "api_endpoints", "out_of_scope", "conventions"
}

VALID_HTTP_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH"}
VALID_ENFORCEMENT_POINTS = {"domain", "api", "ui"}
VALID_SEVERITIES = {"error", "warning"}

PROJECT_FIELDS = {
    "name": str,
    "description": str,
    "mvp_timeline_weeks": int,
}

TECH_STACK_FIELDS = {
    "backend": str,
    "frontend": str,
    "database": str,
    "testing": list,
    "deployment": str,
    "error_handling": str,
}

CONVENTIONS_FIELDS = {
    "error_response_format": str,
    "result_pattern": str,
    "ci_cd": str,
    "no_manual_deploys": bool,
}


class ValidationReport:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed = []

    def error(self, msg):
        self.errors.append(msg)

    def warning(self, msg):
        self.warnings.append(msg)

    def ok(self, msg):
        self.passed.append(msg)

    @property
    def success(self):
        return len(self.errors) == 0

    def print_report(self):
        print(f"\n{'='*60}")
        print(f"STRUCTURED DATA VALIDATION REPORT")
        print(f"{'='*60}")
        print(f"\nPassed: {len(self.passed)}  Warnings: {len(self.warnings)}  Errors: {len(self.errors)}")
        print()

        if self.passed:
            print("--- PASSED ---")
            for p in self.passed:
                print(f"  ✓ {p}")
            print()

        if self.warnings:
            print("--- WARNINGS ---")
            for w in self.warnings:
                print(f"  ⚠ {w}")
            print()

        if self.errors:
            print("--- ERRORS ---")
            for e in self.errors:
                print(f"  ✗ {e}")
            print()

        print(f"{'='*60}")
        if self.success:
            print("RESULT: ALL VALIDATIONS PASSED ✓")
        else:
            print(f"RESULT: {len(self.errors)} VALIDATION ERROR(S) ✗")
        print(f"{'='*60}")

        return 0 if self.success else 1


def check_required_keys(data, report):
    """Check all required top-level keys are present."""
    for key in REQUIRED_TOP_KEYS:
        if key not in data:
            report.error(f"Missing required top-level key: '{key}'")
        elif data[key] is None:
            report.error(f"Top-level key '{key}' is null")
        else:
            report.ok(f"Top-level key '{key}' present and non-null")


def check_types(data, report):
    """Check data types of all fields match expected types."""

    def check_field(obj, field_name, expected_type, path):
        if field_name not in obj:
            report.error(f"Missing required field: '{path}.{field_name}'")
            return
        val = obj[field_name]
        if val is None:
            report.error(f"Field '{path}.{field_name}' is null")
            return
        if not isinstance(val, expected_type):
            report.error(
                f"Field '{path}.{field_name}' has type {type(val).__name__}, "
                f"expected {expected_type.__name__}"
            )
            return
        report.ok(f"Field '{path}.{field_name}' has correct type {expected_type.__name__}")

    # Project
    if "project" in data and isinstance(data["project"], dict):
        for field, typ in PROJECT_FIELDS.items():
            check_field(data["project"], field, typ, "project")

    # Tech stack
    if "tech_stack" in data and isinstance(data["tech_stack"], dict):
        for field, typ in TECH_STACK_FIELDS.items():
            check_field(data["tech_stack"], field, typ, "tech_stack")

    # Conventions
    if "conventions" in data and isinstance(data["conventions"], dict):
        for field, typ in CONVENTIONS_FIELDS.items():
            check_field(data["conventions"], field, typ, "conventions")


def check_data_model(data, report):
    """Validate data_model array."""
    dm = data.get("data_model")
    if not isinstance(dm, list) or len(dm) == 0:
        report.error("data_model is empty or not a list")
        return

    for i, entity in enumerate(dm):
        if not isinstance(entity, dict):
            report.error(f"data_model[{i}] is not an object")
            continue

        name = entity.get("entity_name")
        if not name:
            report.error(f"data_model[{i}].entity_name is missing")
        else:
            report.ok(f"data_model entity '{name}' present")

        fields = entity.get("fields")
        if not isinstance(fields, list) or len(fields) == 0:
            report.error(f"data_model[{i}].fields is empty or not a list")
            continue

        for j, field in enumerate(fields):
            if not isinstance(field, dict):
                report.error(f"data_model[{i}].fields[{j}] is not an object")
                continue

            for req in ("name", "type", "required"):
                if req not in field or field[req] is None:
                    report.error(f"data_model[{i}].fields[{j}].{req} is missing or null")
                else:
                    report.ok(f"data_model[{i}].fields[{j}].{req} = {field[req]}")


def check_business_rules(data, report):
    """Validate business_rules array."""
    rules = data.get("business_rules")
    if not isinstance(rules, list) or len(rules) == 0:
        report.error("business_rules is empty or not a list")
        return

    for i, rule in enumerate(rules):
        if not isinstance(rule, dict):
            report.error(f"business_rules[{i}] is not an object")
            continue

        if not rule.get("rule"):
            report.error(f"business_rules[{i}].rule is missing")
        else:
            report.ok(f"business_rules[{i}]: '{rule['rule'][:50]}...'")

        ep = rule.get("enforcement_point")
        if ep not in VALID_ENFORCEMENT_POINTS:
            report.error(
                f"business_rules[{i}].enforcement_point = '{ep}', "
                f"must be one of {VALID_ENFORCEMENT_POINTS}"
            )
        else:
            report.ok(f"business_rules[{i}].enforcement_point = '{ep}'")

        sev = rule.get("severity")
        if sev not in VALID_SEVERITIES:
            report.error(
                f"business_rules[{i}].severity = '{sev}', "
                f"must be one of {VALID_SEVERITIES}"
            )


def check_api_endpoints(data, report):
    """Validate api_endpoints array."""
    endpoints = data.get("api_endpoints")
    if not isinstance(endpoints, list) or len(endpoints) == 0:
        report.error("api_endpoints is empty or not a list")
        return

    for i, ep in enumerate(endpoints):
        if not isinstance(ep, dict):
            report.error(f"api_endpoints[{i}] is not an object")
            continue

        method = ep.get("method", "").upper()
        if method not in VALID_HTTP_METHODS:
            report.error(f"api_endpoints[{i}].method = '{method}', not a valid HTTP method")
        else:
            report.ok(f"api_endpoints[{i}]: {method} {ep.get('path', '?')}")

        if not ep.get("path"):
            report.error(f"api_endpoints[{i}].path is missing")

        if not ep.get("description"):
            report.error(f"api_endpoints[{i}].description is missing")

        if "requires_auth" not in ep:
            report.error(f"api_endpoints[{i}].requires_auth is missing")
        elif not isinstance(ep["requires_auth"], bool):
            report.error(f"api_endpoints[{i}].requires_auth is not boolean")


def check_no_missing_markers(raw_text, report):
    """Check that no MISSING FROM SOURCE markers remain."""
    if "MISSING FROM SOURCE" in raw_text:
        count = raw_text.count("MISSING FROM SOURCE")
        report.error(f"Found {count} 'MISSING FROM SOURCE' marker(s) — extraction incomplete")
    else:
        report.ok("No 'MISSING FROM SOURCE' markers found")


def check_out_of_scope(data, report):
    """Validate out_of_scope is a non-empty list."""
    oos = data.get("out_of_scope")
    if not isinstance(oos, list) or len(oos) == 0:
        report.error("out_of_scope is empty or not a list")
        return

    for i, item in enumerate(oos):
        if not isinstance(item, str) or not item.strip():
            report.error(f"out_of_scope[{i}] is empty or not a string")
        else:
            report.ok(f"out_of_scope[{i}]: '{item}'")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate.py <yaml-file>")
        sys.exit(1)

    yaml_path = Path(sys.argv[1])
    if not yaml_path.exists():
        print(f"ERROR: File not found: {yaml_path}")
        sys.exit(1)

    raw_text = yaml_path.read_text(encoding="utf-8")

    try:
        data = yaml.safe_load(raw_text)
    except yaml.YAMLError as e:
        print(f"ERROR: YAML parse error: {e}")
        sys.exit(1)

    if not isinstance(data, dict):
        print("ERROR: Top-level YAML is not a mapping/object")
        sys.exit(1)

    report = ValidationReport()

    check_required_keys(data, report)
    check_types(data, report)
    check_data_model(data, report)
    check_business_rules(data, report)
    check_api_endpoints(data, report)
    check_out_of_scope(data, report)
    check_no_missing_markers(raw_text, report)

    sys.exit(report.print_report())


if __name__ == "__main__":
    main()