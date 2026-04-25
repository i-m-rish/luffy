from __future__ import annotations

import json
from pathlib import Path
from typing import Any

APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"


def load_json(file_name: str) -> list[dict[str, Any]]:
    file_path = DATA_DIR / file_name
    if not file_path.exists():
        raise FileNotFoundError(f"Missing IGA data file: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(f"Expected list in {file_name}")

    return data


def get_applications() -> list[dict[str, Any]]:
    return load_json("application-catalog.json")


def get_identities() -> list[dict[str, Any]]:
    return load_json("identities-normalized.json")


def get_accounts() -> list[dict[str, Any]]:
    return load_json("accounts-normalized.json")


def get_entitlements() -> list[dict[str, Any]]:
    return load_json("entitlements-normalized.json")


def get_assignments() -> list[dict[str, Any]]:
    return load_json("assignments-normalized.json")


def get_correlation_results() -> list[dict[str, Any]]:
    return load_json("correlation-results.json")


def find_by_id(records: list[dict[str, Any]], key: str, value: str) -> dict[str, Any] | None:
    return next((record for record in records if record.get(key) == value), None)


def get_identity_access(identity_id: str) -> dict[str, Any] | None:
    identities = get_identities()
    accounts = get_accounts()
    applications = get_applications()
    assignments = get_assignments()
    entitlements = get_entitlements()
    correlations = get_correlation_results()

    identity = find_by_id(identities, "identity_id", identity_id)
    if identity is None:
        return None

    matched_account_ids = {
        correlation["account_id"]
        for correlation in correlations
        if correlation.get("identity_id") == identity_id
    }

    identity_accounts = [account for account in accounts if account["account_id"] in matched_account_ids]

    account_views: list[dict[str, Any]] = []
    for account in identity_accounts:
        application = find_by_id(applications, "application_id", account["application_id"])
        account_assignments = [
            assignment
            for assignment in assignments
            if assignment["account_id"] == account["account_id"]
        ]

        assignment_views: list[dict[str, Any]] = []
        for assignment in account_assignments:
            entitlement = find_by_id(entitlements, "entitlement_id", assignment["entitlement_id"])
            assignment_views.append(
                {
                    "assignment": assignment,
                    "entitlement": entitlement,
                }
            )

        account_views.append(
            {
                "account": account,
                "application": application,
                "assignments": assignment_views,
            }
        )

    return {
        "identity": identity,
        "accounts": account_views,
    }


def get_orphan_accounts() -> list[dict[str, Any]]:
    accounts = get_accounts()
    applications = get_applications()
    correlations = get_correlation_results()

    orphan_accounts = [account for account in accounts if account["correlation_status"] == "ORPHAN"]
    results: list[dict[str, Any]] = []

    for account in orphan_accounts:
        application = find_by_id(applications, "application_id", account["application_id"])
        correlation = find_by_id(correlations, "account_id", account["account_id"])
        results.append(
            {
                "account": account,
                "application": application,
                "correlation_result": correlation,
            }
        )

    return results


def get_high_risk_access() -> list[dict[str, Any]]:
    accounts = get_accounts()
    applications = get_applications()
    assignments = get_assignments()
    entitlements = get_entitlements()

    results: list[dict[str, Any]] = []
    for assignment in assignments:
        entitlement = find_by_id(entitlements, "entitlement_id", assignment["entitlement_id"])
        if entitlement is None or entitlement["risk_level"] not in {"HIGH", "CRITICAL"}:
            continue

        account = find_by_id(accounts, "account_id", assignment["account_id"])
        application = None
        if account is not None:
            application = find_by_id(applications, "application_id", account["application_id"])

        results.append(
            {
                "assignment": assignment,
                "account": account,
                "entitlement": entitlement,
                "application": application,
            }
        )

    return results


def get_routes() -> dict[str, Any]:
    return {
        "/health": {"status": "ok", "service": "iga-service"},
        "/applications": get_applications(),
        "/identities": get_identities(),
        "/accounts": get_accounts(),
        "/entitlements": get_entitlements(),
        "/assignments": get_assignments(),
        "/correlation-results": get_correlation_results(),
        "/governance/orphan-accounts": get_orphan_accounts(),
        "/governance/high-risk-access": get_high_risk_access(),
    }
