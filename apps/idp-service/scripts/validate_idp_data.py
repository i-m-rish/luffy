from __future__ import annotations

import json
from pathlib import Path
from typing import Any

APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"

IDENTITY_TYPES = {"HUMAN", "MACHINE"}
IDENTITY_STATUSES = {"ACTIVE", "DISABLED", "TERMINATED", "STAGED"}
GROUP_TYPES = {"SECURITY", "APP_ACCESS", "ADMIN", "SYSTEM"}
RISK_LEVELS = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
STATUSES = {"ACTIVE", "INACTIVE"}
MEMBERSHIP_STATUSES = {"ACTIVE", "REMOVED"}
AUTH_PROTOCOLS = {"OIDC", "SAML", "API_CLIENT_CREDENTIALS", "NONE"}
MACHINE_IDENTITY_TYPES = {
    "SERVICE_ACCOUNT",
    "OAUTH_CLIENT",
    "SERVICE_PRINCIPAL",
    "CERTIFICATE_IDENTITY",
    "DESKTOP_AGENT",
}
MACHINE_IDENTITY_STATUSES = {"ACTIVE", "INACTIVE", "EXPIRED", "ORPHANED"}
ROTATION_STATUSES = {"CURRENT", "DUE_SOON", "OVERDUE", "NOT_APPLICABLE"}


def load_json(file_name: str) -> list[dict[str, Any]]:
    file_path = DATA_DIR / file_name
    if not file_path.exists():
        raise FileNotFoundError(f"Missing IdP data file: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(f"Expected list in {file_name}")

    return data


def require_fields(record: dict[str, Any], fields: set[str], record_type: str) -> None:
    missing = fields - record.keys()
    if missing:
        raise ValueError(f"{record_type} missing required fields: {sorted(missing)}")


def ensure_unique(records: list[dict[str, Any]], field: str, record_type: str) -> None:
    values = [record.get(field) for record in records]
    duplicates = {value for value in values if values.count(value) > 1}
    if duplicates:
        raise ValueError(f"Duplicate {field} values in {record_type}: {sorted(duplicates)}")


def validate_identities(identities: list[dict[str, Any]]) -> None:
    required = {
        "identity_id",
        "employee_id",
        "lan_id",
        "email",
        "display_name",
        "identity_type",
        "identity_status",
        "source_system",
        "created_at",
        "updated_at",
    }
    for identity in identities:
        require_fields(identity, required, "identity")
        if identity["identity_type"] not in IDENTITY_TYPES:
            raise ValueError(f"Invalid identity_type: {identity['identity_type']}")
        if identity["identity_status"] not in IDENTITY_STATUSES:
            raise ValueError(f"Invalid identity_status: {identity['identity_status']}")
        if identity["identity_type"] == "HUMAN" and not identity["employee_id"]:
            raise ValueError(f"Human identity missing employee_id: {identity['identity_id']}")

    ensure_unique(identities, "identity_id", "identities")
    ensure_unique(identities, "employee_id", "identities")
    ensure_unique(identities, "lan_id", "identities")
    ensure_unique(identities, "email", "identities")


def validate_groups(groups: list[dict[str, Any]]) -> None:
    required = {"group_id", "group_name", "group_type", "description", "risk_level", "status"}
    for group in groups:
        require_fields(group, required, "group")
        if group["group_type"] not in GROUP_TYPES:
            raise ValueError(f"Invalid group_type: {group['group_type']}")
        if group["risk_level"] not in RISK_LEVELS:
            raise ValueError(f"Invalid group risk_level: {group['risk_level']}")
        if group["status"] not in STATUSES:
            raise ValueError(f"Invalid group status: {group['status']}")

    ensure_unique(groups, "group_id", "groups")
    ensure_unique(groups, "group_name", "groups")


def validate_group_memberships(
    memberships: list[dict[str, Any]], identities: list[dict[str, Any]], groups: list[dict[str, Any]]
) -> None:
    required = {
        "membership_id",
        "identity_id",
        "group_id",
        "membership_status",
        "assigned_by",
        "assigned_at",
    }
    identity_ids = {identity["identity_id"] for identity in identities}
    group_ids = {group["group_id"] for group in groups}

    for membership in memberships:
        require_fields(membership, required, "group_membership")
        if membership["identity_id"] not in identity_ids:
            raise ValueError(f"Unknown identity_id in group membership: {membership['identity_id']}")
        if membership["group_id"] not in group_ids:
            raise ValueError(f"Unknown group_id in group membership: {membership['group_id']}")
        if membership["membership_status"] not in MEMBERSHIP_STATUSES:
            raise ValueError(f"Invalid membership_status: {membership['membership_status']}")

    ensure_unique(memberships, "membership_id", "group_memberships")


def validate_app_registrations(apps: list[dict[str, Any]]) -> None:
    required = {
        "app_registration_id",
        "app_id",
        "app_name",
        "auth_protocol",
        "sso_enabled",
        "token_audience",
        "status",
    }
    for app in apps:
        require_fields(app, required, "application_registration")
        if app["auth_protocol"] not in AUTH_PROTOCOLS:
            raise ValueError(f"Invalid auth_protocol: {app['auth_protocol']}")
        if not isinstance(app["sso_enabled"], bool):
            raise ValueError(f"sso_enabled must be boolean for app: {app['app_id']}")
        if app["status"] not in STATUSES:
            raise ValueError(f"Invalid app status: {app['status']}")
        if app["sso_enabled"] and app["auth_protocol"] == "NONE":
            raise ValueError(f"SSO-enabled app cannot use NONE auth protocol: {app['app_id']}")

    ensure_unique(apps, "app_registration_id", "app_registrations")
    ensure_unique(apps, "app_id", "app_registrations")


def validate_app_assignments(
    assignments: list[dict[str, Any]], apps: list[dict[str, Any]], groups: list[dict[str, Any]]
) -> None:
    required = {
        "app_assignment_id",
        "app_registration_id",
        "group_id",
        "assignment_status",
        "assigned_at",
    }
    app_registration_ids = {app["app_registration_id"] for app in apps}
    group_ids = {group["group_id"] for group in groups}

    for assignment in assignments:
        require_fields(assignment, required, "app_assignment")
        if assignment["app_registration_id"] not in app_registration_ids:
            raise ValueError(
                f"Unknown app_registration_id in app assignment: {assignment['app_registration_id']}"
            )
        if assignment["group_id"] not in group_ids:
            raise ValueError(f"Unknown group_id in app assignment: {assignment['group_id']}")
        if assignment["assignment_status"] not in MEMBERSHIP_STATUSES:
            raise ValueError(f"Invalid assignment_status: {assignment['assignment_status']}")

    ensure_unique(assignments, "app_assignment_id", "app_assignments")


def validate_machine_identities(machine_identities: list[dict[str, Any]]) -> None:
    required = {
        "machine_identity_id",
        "name",
        "type",
        "owner",
        "used_by_service",
        "risk_level",
        "status",
        "rotation_status",
        "last_used_at",
    }
    for machine_identity in machine_identities:
        require_fields(machine_identity, required, "machine_identity")
        if machine_identity["type"] not in MACHINE_IDENTITY_TYPES:
            raise ValueError(f"Invalid machine identity type: {machine_identity['type']}")
        if machine_identity["risk_level"] not in RISK_LEVELS:
            raise ValueError(f"Invalid machine identity risk_level: {machine_identity['risk_level']}")
        if machine_identity["status"] not in MACHINE_IDENTITY_STATUSES:
            raise ValueError(f"Invalid machine identity status: {machine_identity['status']}")
        if machine_identity["rotation_status"] not in ROTATION_STATUSES:
            raise ValueError(
                f"Invalid machine identity rotation_status: {machine_identity['rotation_status']}"
            )
        if not machine_identity["owner"]:
            raise ValueError(f"Machine identity missing owner: {machine_identity['machine_identity_id']}")

    ensure_unique(machine_identities, "machine_identity_id", "machine_identities")
    ensure_unique(machine_identities, "name", "machine_identities")


def validate_all() -> dict[str, int]:
    identities = load_json("identities.json")
    groups = load_json("groups.json")
    group_memberships = load_json("group-memberships.json")
    app_registrations = load_json("app-registrations.json")
    app_assignments = load_json("app-assignments.json")
    machine_identities = load_json("machine-identities.json")

    validate_identities(identities)
    validate_groups(groups)
    validate_group_memberships(group_memberships, identities, groups)
    validate_app_registrations(app_registrations)
    validate_app_assignments(app_assignments, app_registrations, groups)
    validate_machine_identities(machine_identities)

    return {
        "identities": len(identities),
        "groups": len(groups),
        "group_memberships": len(group_memberships),
        "app_registrations": len(app_registrations),
        "app_assignments": len(app_assignments),
        "machine_identities": len(machine_identities),
    }


def main() -> None:
    counts = validate_all()
    print("IdP sample data validation passed")
    for name, count in counts.items():
        print(f"{name}: {count}")


if __name__ == "__main__":
    main()
