from __future__ import annotations

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = APP_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from validate_iga_data import load_json, validate_all  # noqa: E402


def test_iga_sample_data_validation_passes() -> None:
    counts = validate_all()

    assert counts == {
        "applications": 8,
        "identities": 6,
        "accounts": 5,
        "entitlements": 5,
        "assignments": 5,
        "correlation_results": 5,
    }


def test_application_catalog_contains_required_foundation_apps() -> None:
    applications = load_json("application-catalog.json")
    application_ids = {application["application_id"] for application in applications}

    assert "hrms-service" in application_ids
    assert "idp-service" in application_ids
    assert "jdbc-target" in application_ids
    assert "pam-target" in application_ids
    assert "api-security-gateway" in application_ids


def test_iga_has_orphan_account_for_correlation_testing() -> None:
    accounts = load_json("accounts-normalized.json")
    orphan_accounts = [account for account in accounts if account["correlation_status"] == "ORPHAN"]

    assert len(orphan_accounts) == 1
    assert orphan_accounts[0]["lan_id"] == "ORPHAN01"


def test_iga_has_correlation_result_for_every_account() -> None:
    accounts = load_json("accounts-normalized.json")
    correlation_results = load_json("correlation-results.json")

    account_ids = {account["account_id"] for account in accounts}
    correlated_account_ids = {result["account_id"] for result in correlation_results}

    assert account_ids == correlated_account_ids


def test_iga_has_critical_entitlement_for_risk_testing() -> None:
    entitlements = load_json("entitlements-normalized.json")
    critical_entitlements = [
        entitlement for entitlement in entitlements if entitlement["risk_level"] == "CRITICAL"
    ]

    assert len(critical_entitlements) == 1
    assert critical_entitlements[0]["entitlement_name"] == "System Administrator"


def test_assignment_references_are_valid() -> None:
    accounts = load_json("accounts-normalized.json")
    entitlements = load_json("entitlements-normalized.json")
    assignments = load_json("assignments-normalized.json")

    account_ids = {account["account_id"] for account in accounts}
    entitlement_ids = {entitlement["entitlement_id"] for entitlement in entitlements}

    assert all(assignment["account_id"] in account_ids for assignment in assignments)
    assert all(assignment["entitlement_id"] in entitlement_ids for assignment in assignments)


def test_terminated_identity_exists_for_governance_testing() -> None:
    identities = load_json("identities-normalized.json")
    terminated = [identity for identity in identities if identity["identity_status"] == "TERMINATED"]

    assert len(terminated) == 1
    assert terminated[0]["employee_id"] == "1006"


def test_graphql_schema_and_examples_exist() -> None:
    schema_file = APP_DIR / "graphql" / "schema.graphql"
    examples_file = APP_DIR / "graphql" / "example-queries.graphql"

    assert schema_file.exists()
    assert examples_file.exists()

    schema = schema_file.read_text(encoding="utf-8")
    examples = examples_file.read_text(encoding="utf-8")

    assert "type Query" in schema
    assert "type Identity" in schema
    assert "type Account" in schema
    assert "GetIdentityAccess" in examples
    assert "GetOrphanAccounts" in examples
