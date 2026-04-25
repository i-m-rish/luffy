from __future__ import annotations

import hashlib
import hmac
import uuid
from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse

SESSION_COOKIE_NAME = "luffy_iga_session"

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
        "VIEW_AUDIT",
        "ADMIN_READ",
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
    },
    "APP_OWNER": {
        "VIEW_DASHBOARD",
        "VIEW_APPLICATIONS",
        "VIEW_IDENTITIES",
        "VIEW_ACCOUNTS",
        "VIEW_ENTITLEMENTS",
    },
    "READ_ONLY": {
        "VIEW_DASHBOARD",
        "VIEW_APPLICATIONS",
        "VIEW_IDENTITIES",
    },
}


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class DemoUser:
    username: str
    display_name: str
    role: str
    password_hash: str

    @property
    def permissions(self) -> set[str]:
        return ROLE_PERMISSIONS[self.role]

    def public_profile(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "display_name": self.display_name,
            "role": self.role,
            "permissions": sorted(self.permissions),
        }


DEMO_USERS = {
    "admin": DemoUser(
        username="admin",
        display_name="IGA Administrator",
        role="IGA_ADMIN",
        password_hash=hash_password("admin123"),
    ),
    "reviewer": DemoUser(
        username="reviewer",
        display_name="Access Reviewer",
        role="ACCESS_REVIEWER",
        password_hash=hash_password("reviewer123"),
    ),
    "owner": DemoUser(
        username="owner",
        display_name="Application Owner",
        role="APP_OWNER",
        password_hash=hash_password("owner123"),
    ),
    "reader": DemoUser(
        username="reader",
        display_name="Read Only User",
        role="READ_ONLY",
        password_hash=hash_password("reader123"),
    ),
}

ACTIVE_SESSIONS: dict[str, str] = {}


def authenticate_user(username: str, password: str) -> DemoUser | None:
    user = DEMO_USERS.get(username)
    if user is None:
        return None

    candidate_hash = hash_password(password)
    if not hmac.compare_digest(candidate_hash, user.password_hash):
        return None

    return user


def create_session(username: str) -> str:
    session_id = str(uuid.uuid4())
    ACTIVE_SESSIONS[session_id] = username
    return session_id


def destroy_session(session_id: str | None) -> None:
    if session_id:
        ACTIVE_SESSIONS.pop(session_id, None)


def get_current_user(request: Request) -> DemoUser | None:
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        return None

    username = ACTIVE_SESSIONS.get(session_id)
    if not username:
        return None

    return DEMO_USERS.get(username)


def require_user(request: Request) -> DemoUser:
    user = get_current_user(request)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def require_permission(request: Request, permission: str) -> DemoUser:
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


def require_ui_permission(request: Request, permission: str) -> DemoUser | RedirectResponse:
    user = get_current_user(request)
    if user is None:
        return RedirectResponse(url="/login", status_code=303)

    if permission not in user.permissions:
        return RedirectResponse(url="/forbidden", status_code=303)

    return user
