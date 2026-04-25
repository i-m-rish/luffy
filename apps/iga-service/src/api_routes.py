from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from auth import require_permission, require_user
from services.governance_service import governance_service

router = APIRouter(tags=["IGA API"])


@router.get("/health")
def health() -> dict[str, str]:
    return governance_service.health()


@router.get("/dashboard")
def dashboard(request: Request) -> dict[str, object]:
    require_permission(request, "VIEW_DASHBOARD")
    return governance_service.dashboard()


@router.get("/applications")
def applications(request: Request) -> list[dict[str, object]]:
    require_permission(request, "VIEW_APPLICATIONS")
    return governance_service.applications()


@router.get("/application-access-summary")
def application_access_summary(request: Request) -> list[dict[str, object]]:
    require_permission(request, "VIEW_APPLICATIONS")
    return governance_service.application_access_summary()


@router.get("/identities")
def identities(request: Request) -> list[dict[str, object]]:
    require_permission(request, "VIEW_IDENTITIES")
    return governance_service.identities()


@router.get("/identity-access-summary")
def identity_access_summary(request: Request) -> list[dict[str, object]]:
    require_permission(request, "VIEW_IDENTITIES")
    return governance_service.identity_access_summary()


@router.get("/accounts")
def accounts(request: Request) -> list[dict[str, object]]:
    require_permission(request, "VIEW_ACCOUNTS")
    return governance_service.accounts()


@router.get("/entitlements")
def entitlements(request: Request) -> list[dict[str, object]]:
    require_permission(request, "VIEW_ENTITLEMENTS")
    return governance_service.entitlements()


@router.get("/assignments")
def assignments(request: Request) -> list[dict[str, object]]:
    require_user(request)
    return governance_service.assignments()


@router.get("/correlation-results")
def correlation_results(request: Request) -> list[dict[str, object]]:
    require_permission(request, "VIEW_CORRELATION")
    return governance_service.correlation_results()


@router.get("/governance/orphan-accounts")
def orphan_accounts(request: Request) -> list[dict[str, object]]:
    require_permission(request, "VIEW_ORPHANS")
    return governance_service.orphan_accounts()


@router.get("/governance/high-risk-access")
def high_risk_access(request: Request) -> list[dict[str, object]]:
    require_permission(request, "VIEW_HIGH_RISK")
    return governance_service.high_risk_access()


@router.get("/governance/identity/{identity_id}/access")
def identity_access(request: Request, identity_id: str) -> dict[str, object]:
    require_permission(request, "VIEW_IDENTITIES")
    result = governance_service.identity_access(identity_id)
    if result is None:
        raise HTTPException(status_code=404, detail={"error": "identity_not_found", "identity_id": identity_id})
    return result
