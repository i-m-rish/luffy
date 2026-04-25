from __future__ import annotations

import json
from pathlib import Path
from typing import Any

APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"
HIGH_RISK_LEVELS = {"HIGH", "CRITICAL"}


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
        if entitlement is None or entitlement["risk_level"] not in HIGH_RISK_LEVELS:
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


def get_identity_access_summaries() -> list[dict[str, Any]]:
    identities = get_identities()
    summaries: list[dict[str, Any]] = []

    for identity in identities:
        access = get_identity_access(identity["identity_id"])
        accounts = access["accounts"] if access is not None else []
        assignments = [
            assignment_view
            for account_view in accounts
            for assignment_view in account_view["assignments"]
        ]
        high_risk_assignments = [
            assignment_view
            for assignment_view in assignments
            if assignment_view["entitlement"] is not None
            and assignment_view["entitlement"]["risk_level"] in HIGH_RISK_LEVELS
        ]

        summaries.append(
            {
                "identity_id": identity["identity_id"],
                "display_name": identity["display_name"],
                "employee_id": identity["employee_id"],
                "lan_id": identity["lan_id"],
                "identity_status": identity["identity_status"],
                "account_count": len(accounts),
                "assignment_count": len(assignments),
                "high_risk_assignment_count": len(high_risk_assignments),
            }
        )

    return summaries


def get_application_access_summary() -> list[dict[str, Any]]:
    applications = get_applications()
    accounts = get_accounts()
    entitlements = get_entitlements()
    assignments = get_assignments()

    summaries: list[dict[str, Any]] = []
    for application in applications:
        app_accounts = [
            account for account in accounts if account["application_id"] == application["application_id"]
        ]
        app_entitlements = [
            entitlement
            for entitlement in entitlements
            if entitlement["application_id"] == application["application_id"]
        ]
        app_entitlement_ids = {entitlement["entitlement_id"] for entitlement in app_entitlements}
        app_assignments = [
            assignment
            for assignment in assignments
            if assignment["entitlement_id"] in app_entitlement_ids
        ]
        critical_entitlements = [
            entitlement for entitlement in app_entitlements if entitlement["risk_level"] == "CRITICAL"
        ]

        summaries.append(
            {
                "application_id": application["application_id"],
                "application_name": application["application_name"],
                "application_type": application["application_type"],
                "integration_pattern": application["integration_pattern"],
                "risk_level": application["risk_level"],
                "status": application["status"],
                "account_count": len(app_accounts),
                "entitlement_count": len(app_entitlements),
                "assignment_count": len(app_assignments),
                "critical_entitlement_count": len(critical_entitlements),
            }
        )

    return summaries


def get_governance_dashboard() -> dict[str, Any]:
    applications = get_applications()
    identities = get_identities()
    accounts = get_accounts()
    entitlements = get_entitlements()
    assignments = get_assignments()
    correlations = get_correlation_results()
    orphan_accounts = get_orphan_accounts()
    high_risk_access = get_high_risk_access()

    matched_correlations = [result for result in correlations if result["result"] == "MATCHED"]
    terminated_identities = [
        identity for identity in identities if identity["identity_status"] == "TERMINATED"
    ]
    critical_entitlements = [
        entitlement for entitlement in entitlements if entitlement["risk_level"] == "CRITICAL"
    ]
    active_accounts = [account for account in accounts if account["account_status"] == "ACTIVE"]

    return {
        "application_count": len(applications),
        "identity_count": len(identities),
        "account_count": len(accounts),
        "active_account_count": len(active_accounts),
        "entitlement_count": len(entitlements),
        "assignment_count": len(assignments),
        "matched_account_count": len(matched_correlations),
        "orphan_account_count": len(orphan_accounts),
        "high_risk_access_count": len(high_risk_access),
        "critical_entitlement_count": len(critical_entitlements),
        "terminated_identity_count": len(terminated_identities),
        "correlation_coverage_percent": round((len(matched_correlations) / len(accounts)) * 100, 2)
        if accounts
        else 0,
        "top_risks": [
            "Active orphan account requires owner review." if orphan_accounts else None,
            "High-risk access exists and should be reviewed." if high_risk_access else None,
            "Critical entitlement exists in catalog." if critical_entitlements else None,
            "Terminated identity exists for leaver governance testing." if terminated_identities else None,
        ],
    }


def get_routes() -> dict[str, Any]:
    return {
        "/health": {"status": "ok", "service": "iga-service"},
        "/dashboard": get_governance_dashboard(),
        "/applications": get_applications(),
        "/application-access-summary": get_application_access_summary(),
        "/identities": get_identities(),
        "/identity-access-summary": get_identity_access_summaries(),
        "/accounts": get_accounts(),
        "/entitlements": get_entitlements(),
        "/assignments": get_assignments(),
        "/correlation-results": get_correlation_results(),
        "/governance/orphan-accounts": get_orphan_accounts(),
        "/governance/high-risk-access": get_high_risk_access(),
    }
