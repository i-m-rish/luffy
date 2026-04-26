from __future__ import annotations

import time
from typing import Any

import httpx
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from auth import require_permission
from management_routes import ACCESS_REQUESTS
from repository import find_by_id, get_entitlements, get_identities

router = APIRouter(tags=["IGA Fulfillment"])

IDP_ASSIGNMENT_URL = "http://127.0.0.1:8002/api/access/assignments"
IDENTITY_TO_IDP_USERNAME = {
    "IGA-IDENTITY-1001": "admin",
    "IGA-IDENTITY-1002": "reviewer",
    "IGA-IDENTITY-1003": "owner",
    "IGA-IDENTITY-1004": "reader",
}
FULFILLMENT_AUDIT: list[dict[str, Any]] = []


def audit(event_type: str, actor: str, request_id: str, detail: str, metadata: dict[str, Any] | None = None) -> None:
    FULFILLMENT_AUDIT.insert(
        0,
        {
            "event_type": event_type,
            "actor": actor,
            "request_id": request_id,
            "detail": detail,
            "metadata": metadata or {},
            "created_at": time.time(),
        },
    )


def resolve_request(request_id: str) -> dict[str, Any]:
    for item in ACCESS_REQUESTS:
        if item["request_id"] == request_id:
            return item
    raise HTTPException(status_code=404, detail={"error": "access_request_not_found", "request_id": request_id})


def resolve_identity_username(identity_id: str) -> str:
    if identity_id in IDENTITY_TO_IDP_USERNAME:
        return IDENTITY_TO_IDP_USERNAME[identity_id]
    identity = find_by_id(get_identities(), "identity_id", identity_id)
    if identity is None:
        raise HTTPException(status_code=400, detail={"error": "identity_not_found", "identity_id": identity_id})
    return str(identity["email"]).split("@")[0]


def resolve_zsp_role(entitlement_id: str) -> str:
    entitlement = find_by_id(get_entitlements(), "entitlement_id", entitlement_id)
    if entitlement is None:
        raise HTTPException(status_code=400, detail={"error": "entitlement_not_found", "entitlement_id": entitlement_id})
    if entitlement.get("application_id") != "zsp-jit-app":
        raise HTTPException(status_code=400, detail={"error": "unsupported_target_application", "application_id": entitlement.get("application_id")})
    native_role = str(entitlement.get("native_entitlement_id"))
    if native_role == "ZSP_SESSION_ADMIN":
        return "ZSP_ADMIN"
    return native_role


def provision_idp_assignment(username: str, app_role: str) -> dict[str, Any]:
    with httpx.Client(timeout=5.0) as client:
        response = client.post(
            IDP_ASSIGNMENT_URL,
            data={"username": username, "client_id": "luffy-zsp", "app_role": app_role},
        )
    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail={"error": "idp_provisioning_failed", "status_code": response.status_code, "body": response.text})
    payload = response.json()
    if not isinstance(payload, dict):
        raise HTTPException(status_code=502, detail={"error": "invalid_idp_response"})
    return payload


@router.post("/api/requests/access/{request_id}/fulfill")
def api_fulfill_access_request(request: Request, request_id: str) -> dict[str, object]:
    actor = require_permission(request, "CREATE_RESOURCE_REQUEST")
    item = resolve_request(request_id)
    username = resolve_identity_username(str(item["target_identity_id"]))
    app_role = resolve_zsp_role(str(item["entitlement_id"]))
    result = provision_idp_assignment(username, app_role)
    item["status"] = "FULFILLED"
    item["fulfilled_by"] = actor.username
    item["fulfilled_at"] = time.time()
    item["provisioning_result"] = result
    audit("ACCESS_REQUEST_FULFILLED", actor.username, request_id, f"Provisioned {app_role} for {username} in IdP", result)
    return item


@router.post("/ui/requests/access/fulfill")
def ui_fulfill_access_request(request: Request, request_id: str = Form(...)) -> RedirectResponse:
    api_fulfill_access_request(request, request_id)
    return RedirectResponse(url="/ui/requests/access", status_code=303)


@router.get("/api/fulfillment/audit")
def api_fulfillment_audit(request: Request) -> list[dict[str, object]]:
    require_permission(request, "VIEW_AUDIT")
    return FULFILLMENT_AUDIT
