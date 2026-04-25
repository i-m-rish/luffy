from __future__ import annotations

import json
from pathlib import Path
from typing import Any

APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"

APPLICATION_TYPES = {"HRMS", "IDP", "TARGET", "PAM", "SECURITY", "IGA", "SAAS_TARGET"}
INTEGRATION_PATTERNS = {
    "JSON",
    "JDBC",
    "GRAPHQL",
    "REST",
    "SCIM",
    "PAM_API",
    "EVENT_API",
    "OIDC_DEMO",
    "OIDC_DEMO + FASTAPI",
    "OIDC_JIT_ZSP",
}
RISK_LEVELS = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
APPLICATION_STATUSES = {"ACTIVE", "INACTIVE", "DESIGN", "FUTURE"}
IDENTITY_TYPES = {"HUMAN", "MACHINE"}
IDENTITY_STATUSES = {"ACTIVE", "DISABLED", "TERMINATED", "STAGED"}
ACCOUNT_STATUSES = {"ACTIVE", "DISABLED", "LOCKED", "TERMINATED"}
CORRELATION_STATUSES = {"MATCHED", "PARTIAL", "ORPHAN", "NOT_EVALUATED"}
ENTITLEMENT_STATUSES = {"ACTIVE", "INACTIVE"}
ASSIGNMENT_STATUSES = {"ACTIVE", "REVOKED", "TEMPORARY_ACTIVE"}
CORRELATION_RESULTS = {"MATCHED", "PARTIAL", "ORPHAN"}
MATCH_ATTRIBUTES = {"employee_id", "lan_id", "email", "NONE"}
CONFIDENCE_LEVELS = {"HIGH", "MEDIUM", "LOW", "NONE"}


def load_json(file_name: str) -> list[dict[str, Any]]:
    file_path = DATA_DIR / file_name
    if not file_path.exists():
        raise FileNotFoundError(f"Missing IGA data file: {file_path}")

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


def validate_applications(applications: list[dict[str, Any]]) -> None:
    required = {
        "application_id",
        "application_name",
        "application_type",
        "integration_pattern",
        "risk_level",
        "status",
        "owner",
    }
    for application in applications:
        require_fields(application, required, "application")
        if application["application_type"] not in APPLICATION_TYPES:
            raise ValueError(f"Invalid application_type: {application['application_type']}")
        if application["integration_pattern"] not in INTEGRATION_PATTERNS:
            raise ValueError(f"Invalid integration_pattern: {application['integration_pattern']}")
        if application["risk_level"] not in RISK_LEVELS:
            raise ValueError(f"Invalid application risk_level: {application['risk_level']}")
        if application["status"] not in APPLICATION_STATUSES:
            raise ValueError(f"Invalid application status: {application['status']}")

    ensure_unique(applications, "application_id", "applications")


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


def validate_accounts(accounts: list[dict[str, Any]], applications: list[dict[str, Any]]) -> None:
    required = {
        "account_id",
        "application_id",
        "native_account_id",
        "employee_id",
        "lan_id",
        "email",
        "account_status",
        "correlation_status",
    }
    application_ids = {application["application_id"] for application in applications}

    for account in accounts:
        require_fields(account, required, "account")
        if account["application_id"] not in application_ids:
            raise ValueError(f"Unknown application_id on account: {account['application_id']}")
        if account["account_status"] not in ACCOUNT_STATUSES:
            raise ValueError(f"Invalid account_status: {account['account_status']}")
        if account["correlation_status"] not in CORRELATION_STATUSES:
            raise ValueError(f"Invalid correlation_status: {account['correlation_status']}")

    ensure_unique(accounts, "account_id", "accounts")


def validate_entitlements(entitlements: list[dict[str, Any]], applications: list[dict[str, Any]]) -> None:
    required = {
        "entitlement_id",
        "application_id",
        "native_entitlement_id",
        "entitlement_name",
        "entitlement_description",
        "risk_level",
        "status",
    }
    application_ids = {application["application_id"] for application in applications}

    for entitlement in entitlements:
        require_fields(entitlement, required, "entitlement")
        if entitlement["application_id"] not in application_ids:
            raise ValueError(f"Unknown application_id on entitlement: {entitlement['application_id']}")
        if entitlement["risk_level"] not in RISK_LEVELS:
            raise ValueError(f"Invalid entitlement risk_level: {entitlement['risk_level']}")
        if entitlement["status"] not in ENTITLEMENT_STATUSES:
            raise ValueError(f"Invalid entitlement status: {entitlement['status']}")

    ensure_unique(entitlements, "entitlement_id", "entitlements")


def validate_assignments(
    assignments: list[dict[str, Any]],
    accounts: list[dict[str, Any]],
    entitlements: list[dict[str, Any]],
) -> None:
    required = {
        "assignment_id",
        "account_id",
        "entitlement_id",
        "assignment_status",
        "assigned_by",
        "assigned_at",
    }
    account_ids = {account["account_id"] for account in accounts}
    entitlement_ids = {entitlement["entitlement_id"] for entitlement in entitlements}

    for assignment in assignments:
        require_fields(assignment, required, "assignment")
        if assignment["account_id"] not in account_ids:
            raise ValueError(f"Unknown account_id on assignment: {assignment['account_id']}")
        if assignment["entitlement_id"] not in entitlement_ids:
            raise ValueError(f"Unknown entitlement_id on assignment: {assignment['entitlement_id']}")
        if assignment["assignment_status"] not in ASSIGNMENT_STATUSES:
            raise ValueError(f"Invalid assignment_status: {assignment['assignment_status']}")

    ensure_unique(assignments, "assignment_id", "assignments")


def validate_correlation_results(
    correlation_results: list[dict[str, Any]],
    accounts: list[dict[str, Any]],
    identities: list[dict[str, Any]],
) -> None:
    required = {
        "correlation_id",
        "account_id",
        "identity_id",
        "result",
        "match_attribute",
        "confidence",
        "reason",
    }
    account_ids = {account["account_id"] for account in accounts}
    identity_ids = {identity["identity_id"] for identity in identities}

    for result in correlation_results:
        require_fields(result, required, "correlation_result")
        if result["account_id"] not in account_ids:
            raise ValueError(f"Unknown account_id on correlation result: {result['account_id']}")
        if result["identity_id"] is not None and result["identity_id"] not in identity_ids:
            raise ValueError(f"Unknown identity_id on correlation result: {result['identity_id']}")
        if result["result"] not in CORRELATION_RESULTS:
            raise ValueError(f"Invalid correlation result: {result['result']}")
        if result["match_attribute"] not in MATCH_ATTRIBUTES:
            raise ValueError(f"Invalid match_attribute: {result['match_attribute']}")
        if result["confidence"] not in CONFIDENCE_LEVELS:
            raise ValueError(f"Invalid confidence: {result['confidence']}")
        if result["result"] == "ORPHAN" and result["identity_id"] is not None:
            raise ValueError(f"Orphan result should not have identity_id: {result['correlation_id']}")

    ensure_unique(correlation_results, "correlation_id", "correlation_results")


def validate_all() -> dict[str, int]:
    applications = load_json("application-catalog.json")
    identities = load_json("identities-normalized.json")
    accounts = load_json("accounts-normalized.json")
    entitlements = load_json("entitlements-normalized.json")
    assignments = load_json("assignments-normalized.json")
    correlation_results = load_json("correlation-results.json")

    validate_applications(applications)
    validate_identities(identities)
    validate_accounts(accounts, applications)
    validate_entitlements(entitlements, applications)
    validate_assignments(assignments, accounts, entitlements)
    validate_correlation_results(correlation_results, accounts, identities)

    return {
        "applications": len(applications),
        "identities": len(identities),
        "accounts": len(accounts),
        "entitlements": len(entitlements),
        "assignments": len(assignments),
        "correlation_results": len(correlation_results),
    }


def main() -> None:
    counts = validate_all()
    print("IGA sample data validation passed")
    for name, count in counts.items():
        print(f"{name}: {count}")


if __name__ == "__main__":
    main()
