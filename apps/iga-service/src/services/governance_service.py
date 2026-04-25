from __future__ import annotations

from typing import Any

from repository import (
    find_by_id,
    get_accounts,
    get_application_access_summary,
    get_applications,
    get_assignments,
    get_correlation_results,
    get_entitlements,
    get_governance_dashboard,
    get_high_risk_access,
    get_identities,
    get_identity_access,
    get_identity_access_summaries,
    get_orphan_accounts,
)


class GovernanceService:
    """Read-only service layer for IGA governance use cases."""

    def health(self) -> dict[str, str]:
        return {"status": "ok", "service": "iga-service"}

    def dashboard(self) -> dict[str, Any]:
        return get_governance_dashboard()

    def applications(self) -> list[dict[str, Any]]:
        return get_applications()

    def application_access_summary(self) -> list[dict[str, Any]]:
        return get_application_access_summary()

    def application_detail(self, application_id: str) -> dict[str, Any] | None:
        applications = get_applications()
        accounts = get_accounts()
        entitlements = get_entitlements()
        assignments = get_assignments()
        correlations = get_correlation_results()
        identities = get_identities()

        application = find_by_id(applications, "application_id", application_id)
        if application is None:
            return None

        source_accounts = [account for account in accounts if account["application_id"] == application_id]
        source_entitlements = [entitlement for entitlement in entitlements if entitlement["application_id"] == application_id]
        source_entitlement_ids = {entitlement["entitlement_id"] for entitlement in source_entitlements}
        source_account_ids = {account["account_id"] for account in source_accounts}
        source_assignments = [
            assignment
            for assignment in assignments
            if assignment["account_id"] in source_account_ids
            or assignment["entitlement_id"] in source_entitlement_ids
        ]

        account_views: list[dict[str, Any]] = []
        for account in source_accounts:
            correlation = find_by_id(correlations, "account_id", account["account_id"])
            identity = None
            if correlation and correlation.get("identity_id"):
                identity = find_by_id(identities, "identity_id", correlation["identity_id"])
            account_views.append({"account": account, "correlation": correlation, "identity": identity})

        entitlement_views: list[dict[str, Any]] = []
        for entitlement in source_entitlements:
            entitlement_assignments = [
                assignment for assignment in source_assignments if assignment["entitlement_id"] == entitlement["entitlement_id"]
            ]
            entitlement_views.append({"entitlement": entitlement, "assignment_count": len(entitlement_assignments)})

        return {
            "application": application,
            "accounts": account_views,
            "entitlements": entitlement_views,
            "assignments": source_assignments,
        }

    def account_detail(self, account_id: str) -> dict[str, Any] | None:
        accounts = get_accounts()
        applications = get_applications()
        assignments = get_assignments()
        entitlements = get_entitlements()
        correlations = get_correlation_results()
        identities = get_identities()

        account = find_by_id(accounts, "account_id", account_id)
        if account is None:
            return None

        application = find_by_id(applications, "application_id", account["application_id"])
        correlation = find_by_id(correlations, "account_id", account_id)
        identity = None
        if correlation and correlation.get("identity_id"):
            identity = find_by_id(identities, "identity_id", correlation["identity_id"])

        account_assignments = [assignment for assignment in assignments if assignment["account_id"] == account_id]
        assignment_views = []
        for assignment in account_assignments:
            entitlement = find_by_id(entitlements, "entitlement_id", assignment["entitlement_id"])
            assignment_views.append({"assignment": assignment, "entitlement": entitlement})

        return {
            "account": account,
            "application": application,
            "correlation": correlation,
            "identity": identity,
            "assignments": assignment_views,
        }

    def entitlement_detail(self, entitlement_id: str) -> dict[str, Any] | None:
        entitlements = get_entitlements()
        applications = get_applications()
        assignments = get_assignments()
        accounts = get_accounts()
        correlations = get_correlation_results()
        identities = get_identities()

        entitlement = find_by_id(entitlements, "entitlement_id", entitlement_id)
        if entitlement is None:
            return None

        application = find_by_id(applications, "application_id", entitlement["application_id"])
        entitlement_assignments = [assignment for assignment in assignments if assignment["entitlement_id"] == entitlement_id]
        assignment_views = []
        for assignment in entitlement_assignments:
            account = find_by_id(accounts, "account_id", assignment["account_id"])
            correlation = find_by_id(correlations, "account_id", assignment["account_id"])
            identity = None
            if correlation and correlation.get("identity_id"):
                identity = find_by_id(identities, "identity_id", correlation["identity_id"])
            assignment_views.append({"assignment": assignment, "account": account, "identity": identity})

        return {
            "entitlement": entitlement,
            "application": application,
            "assignments": assignment_views,
        }

    def identities(self) -> list[dict[str, Any]]:
        return get_identities()

    def identity_access_summary(self) -> list[dict[str, Any]]:
        return get_identity_access_summaries()

    def accounts(self) -> list[dict[str, Any]]:
        return get_accounts()

    def entitlements(self) -> list[dict[str, Any]]:
        return get_entitlements()

    def assignments(self) -> list[dict[str, Any]]:
        return get_assignments()

    def correlation_results(self) -> list[dict[str, Any]]:
        return get_correlation_results()

    def orphan_accounts(self) -> list[dict[str, Any]]:
        return get_orphan_accounts()

    def high_risk_access(self) -> list[dict[str, Any]]:
        return get_high_risk_access()

    def identity_access(self, identity_id: str) -> dict[str, Any] | None:
        return get_identity_access(identity_id)


governance_service = GovernanceService()
