from __future__ import annotations

from fastapi import FastAPI, HTTPException

from repository import (
    get_accounts,
    get_applications,
    get_assignments,
    get_correlation_results,
    get_entitlements,
    get_high_risk_access,
    get_identities,
    get_identity_access,
    get_orphan_accounts,
)

app = FastAPI(
    title="Luffy IGA Service",
    description="Read-only IGA governance API over normalized sample data.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "iga-service"}


@app.get("/applications")
def applications() -> list[dict[str, object]]:
    return get_applications()


@app.get("/identities")
def identities() -> list[dict[str, object]]:
    return get_identities()


@app.get("/accounts")
def accounts() -> list[dict[str, object]]:
    return get_accounts()


@app.get("/entitlements")
def entitlements() -> list[dict[str, object]]:
    return get_entitlements()


@app.get("/assignments")
def assignments() -> list[dict[str, object]]:
    return get_assignments()


@app.get("/correlation-results")
def correlation_results() -> list[dict[str, object]]:
    return get_correlation_results()


@app.get("/governance/orphan-accounts")
def orphan_accounts() -> list[dict[str, object]]:
    return get_orphan_accounts()


@app.get("/governance/high-risk-access")
def high_risk_access() -> list[dict[str, object]]:
    return get_high_risk_access()


@app.get("/governance/identity/{identity_id}/access")
def identity_access(identity_id: str) -> dict[str, object]:
    result = get_identity_access(identity_id)
    if result is None:
        raise HTTPException(status_code=404, detail={"error": "identity_not_found", "identity_id": identity_id})
    return result
