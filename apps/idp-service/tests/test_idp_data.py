from __future__ import annotations

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = APP_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from validate_idp_data import load_json, validate_all  # noqa: E402


def test_idp_sample_data_validation_passes() -> None:
    counts = validate_all()

    assert counts == {
        "identities": 6,
        "groups": 5,
        "group_memberships": 5,
        "app_registrations": 5,
        "app_assignments": 4,
        "machine_identities": 4,
    }


def test_idp_has_disabled_identity_for_leaver_scenario() -> None:
    identities = load_json("identities.json")

    disabled = [identity for identity in identities if identity["identity_status"] == "DISABLED"]

    assert len(disabled) == 1
    assert disabled[0]["employee_id"] == "1006"


def test_idp_has_critical_admin_group() -> None:
    groups = load_json("groups.json")

    critical_groups = [group for group in groups if group["risk_level"] == "CRITICAL"]

    assert len(critical_groups) == 1
    assert critical_groups[0]["group_id"] == "GRP-SECURITY-ADMIN"


def test_group_memberships_reference_valid_identities_and_groups() -> None:
    identities = load_json("identities.json")
    groups = load_json("groups.json")
    memberships = load_json("group-memberships.json")

    identity_ids = {identity["identity_id"] for identity in identities}
    group_ids = {group["group_id"] for group in groups}

    assert all(membership["identity_id"] in identity_ids for membership in memberships)
    assert all(membership["group_id"] in group_ids for membership in memberships)


def test_app_assignments_reference_valid_apps_and_groups() -> None:
    apps = load_json("app-registrations.json")
    groups = load_json("groups.json")
    assignments = load_json("app-assignments.json")

    app_registration_ids = {app["app_registration_id"] for app in apps}
    group_ids = {group["group_id"] for group in groups}

    assert all(
        assignment["app_registration_id"] in app_registration_ids for assignment in assignments
    )
    assert all(assignment["group_id"] in group_ids for assignment in assignments)


def test_idp_includes_non_sso_jdbc_registration() -> None:
    apps = load_json("app-registrations.json")

    jdbc_app = next(app for app in apps if app["app_id"] == "jdbc-target")

    assert jdbc_app["sso_enabled"] is False
    assert jdbc_app["auth_protocol"] == "NONE"


def test_idp_includes_oidc_and_saml_app_registrations() -> None:
    apps = load_json("app-registrations.json")
    protocols = {app["auth_protocol"] for app in apps}

    assert "OIDC" in protocols
    assert "SAML" in protocols


def test_machine_identity_overdue_rotation_exists_for_risk_testing() -> None:
    machine_identities = load_json("machine-identities.json")

    overdue = [
        machine_identity
        for machine_identity in machine_identities
        if machine_identity["rotation_status"] == "OVERDUE"
    ]

    assert len(overdue) == 1
    assert overdue[0]["risk_level"] == "CRITICAL"
    assert overdue[0]["used_by_service"] == "api-security-gateway"


def test_graphql_schema_exists_and_defines_query_type() -> None:
    schema_file = APP_DIR / "graphql" / "schema.graphql"

    assert schema_file.exists()
    schema = schema_file.read_text(encoding="utf-8")
    assert "type Query" in schema
    assert "type Identity" in schema
    assert "type MachineIdentity" in schema


def test_graphql_examples_exist() -> None:
    examples_file = APP_DIR / "graphql" / "example-queries.graphql"

    assert examples_file.exists()
    examples = examples_file.read_text(encoding="utf-8")
    assert "GetIdentityWithGroups" in examples
    assert "GetApplicationLoginGroups" in examples
    assert "GetHighRiskMachineIdentities" in examples
