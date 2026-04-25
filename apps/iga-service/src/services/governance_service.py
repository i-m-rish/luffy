from __future__ import annotations

from typing import Any

from repository import (
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
