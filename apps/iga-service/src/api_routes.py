from __future__ import annotations

from fastapi import APIRouter, HTTPException

from services.governance_service import governance_service

router = APIRouter(tags=["IGA API"])


@router.get("/health")
def health() -> dict[str, str]:
    return governance_service.health()


@router.get("/dashboard")
def dashboard() -> dict[str, object]:
    return governance_service.dashboard()


@router.get("/applications")
def applications() -> list[dict[str, object]]:
    return governance_service.applications()


@router.get("/application-access-summary")
def application_access_summary() -> list[dict[str, object]]:
    return governance_service.application_access_summary()


@router.get("/identities")
def identities() -> list[dict[str, object]]:
    return governance_service.identities()


@router.get("/identity-access-summary")
def identity_access_summary() -> list[dict[str, object]]:
    return governance_service.identity_access_summary()


@router.get("/accounts")
def accounts() -> list[dict[str, object]]:
    return governance_service.accounts()


@router.get("/entitlements")
def entitlements() -> list[dict[str, object]]:
    return governance_service.entitlements()


@router.get("/assignments")
def assignments() -> list[dict[str, object]]:
    return governance_service.assignments()


@router.get("/correlation-results")
def correlation_results() -> list[dict[str, object]]:
    return governance_service.correlation_results()


@router.get("/governance/orphan-accounts")
def orphan_accounts() -> list[dict[str, object]]:
    return governance_service.orphan_accounts()


@router.get("/governance/high-risk-access")
def high_risk_access() -> list[dict[str, object]]:
    return governance_service.high_risk_access()


@router.get("/governance/identity/{identity_id}/access")
def identity_access(identity_id: str) -> dict[str, object]:
    result = governance_service.identity_access(identity_id)
    if result is None:
        raise HTTPException(status_code=404, detail={"error": "identity_not_found", "identity_id": identity_id})
    return result
