from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse

SESSION_COOKIE_NAME = "luffy_iga_session"
IDP_STATE_COOKIE_NAME = "luffy_iga_auth_state"
IDP_BASE_URL = "http://127.0.0.1:8002"
IGA_CLIENT_ID = "luffy-iga"
IGA_REDIRECT_URI = "http://127.0.0.1:8001/auth/callback"

ROLE_PERMISSIONS = {
    "IGA_ADMIN": {
        "VIEW_DASHBOARD",
        "VIEW_APPLICATIONS",
        "VIEW_IDENTITIES",
        "VIEW_ACCOUNTS",
        "VIEW_ENTITLEMENTS",
        "VIEW_CORRELATION",
        "VIEW_ORPHANS",
        "VIEW_HIGH_RISK",
        "VIEW_ACCESS_REVIEWS",
        "VIEW_POLICY_VIOLATIONS",
        "VIEW_AUDIT",
        "ADMIN_READ",
        "CREATE_RESOURCE_REQUEST",
    },
    "ACCESS_REVIEWER": {
        "VIEW_DASHBOARD",
        "VIEW_APPLICATIONS",
        "VIEW_IDENTITIES",
        "VIEW_ACCOUNTS",
        "VIEW_ENTITLEMENTS",
        "VIEW_CORRELATION",
        "VIEW_ORPHANS",
        "VIEW_HIGH_RISK",
        "VIEW_ACCESS_REVIEWS",
        "VIEW_POLICY_VIOLATIONS",
    },
    "APP_OWNER": {
        "VIEW_DASHBOARD",
        "VIEW_APPLICATIONS",
        "VIEW_IDENTITIES",
        "VIEW_ACCOUNTS",
        "VIEW_ENTITLEMENTS",
        "VIEW_ACCESS_REVIEWS",
        "CREATE_RESOURCE_REQUEST",
    },
    "READ_ONLY": {
        "VIEW_DASHBOARD",
        "VIEW_APPLICATIONS",
        "VIEW_IDENTITIES",
    },
}


@dataclass(frozen=True)
class AuthenticatedUser:
    username: str
    display_name: str
    email: str
    role: str
    source: str = "idp-service"

    @property
    def permissions(self) -> set[str]:
        return ROLE_PERMISSIONS.get(self.role, set())

    def public_profile(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "display_name": self.display_name,
            "email": self.email,
            "role": self.role,
            "source": self.source,
            "permissions": sorted(self.permissions),
        }


ACTIVE_SESSIONS: dict[str, AuthenticatedUser] = {}


def create_auth_state() -> str:
    return str(uuid.uuid4())


def create_session_from_claims(claims: dict[str, Any]) -> str:
    role = str(claims.get("role", "READ_ONLY"))
    if role not in ROLE_PERMISSIONS:
        role = "READ_ONLY"

    user = AuthenticatedUser(
        username=str(claims.get("preferred_username") or claims.get("sub") or "unknown"),
        display_name=str(claims.get("name") or claims.get("preferred_username") or "Unknown User"),
        email=str(claims.get("email") or "unknown@example.com"),
        role=role,
    )
    session_id = str(uuid.uuid4())
    ACTIVE_SESSIONS[session_id] = user
    return session_id


def destroy_session(session_id: str | None) -> None:
    if session_id:
        ACTIVE_SESSIONS.pop(session_id, None)


def get_current_user(request: Request) -> AuthenticatedUser | None:
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        return None
    return ACTIVE_SESSIONS.get(session_id)


def require_user(request: Request) -> AuthenticatedUser:
    user = get_current_user(request)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def require_permission(request: Request, permission: str) -> AuthenticatedUser:
    user = require_user(request)
    if permission not in user.permissions:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "permission_denied",
                "required_permission": permission,
                "role": user.role,
            },
        )
    return user


def require_ui_permission(request: Request, permission: str) -> AuthenticatedUser | RedirectResponse:
    user = get_current_user(request)
    if user is None:
        return RedirectResponse(url="/login", status_code=303)

    if permission not in user.permissions:
        return RedirectResponse(url="/forbidden", status_code=303)

    return user
