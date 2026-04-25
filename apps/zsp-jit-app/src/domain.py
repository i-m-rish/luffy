from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

SESSION_COOKIE_NAME = "luffy_zsp_session"
STATE_COOKIE_NAME = "luffy_zsp_auth_state"
IDP_BASE_URL = "http://127.0.0.1:8002"
CLIENT_ID = "luffy-zsp"
REDIRECT_URI = "http://127.0.0.1:8003/auth/callback"

ROLE_MAPPING = {
    "IGA_ADMIN": "ZSP_ADMIN",
    "ACCESS_REVIEWER": "ZSP_APPROVER",
    "APP_OWNER": "ZSP_OPERATOR",
    "READ_ONLY": "ZSP_VIEWER",
}

APP_PERMISSIONS = {
    "ZSP_ADMIN": {"VIEW", "REQUEST_ELEVATION", "APPROVE_ELEVATION", "VIEW_AUDIT", "ADMIN"},
    "ZSP_APPROVER": {"VIEW", "REQUEST_ELEVATION", "APPROVE_ELEVATION", "VIEW_AUDIT"},
    "ZSP_OPERATOR": {"VIEW", "REQUEST_ELEVATION"},
    "ZSP_VIEWER": {"VIEW"},
}


@dataclass
class LocalUser:
    user_id: str
    username: str
    display_name: str
    email: str
    idp_role: str
    app_role: str
    created_at: float = field(default_factory=time.time)
    last_login_at: float = field(default_factory=time.time)

    @property
    def permissions(self) -> set[str]:
        return APP_PERMISSIONS.get(self.app_role, set())

    def as_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "display_name": self.display_name,
            "email": self.email,
            "idp_role": self.idp_role,
            "app_role": self.app_role,
            "permissions": sorted(self.permissions),
            "created_at": self.created_at,
            "last_login_at": self.last_login_at,
        }


LOCAL_USERS: dict[str, LocalUser] = {}
SESSIONS: dict[str, str] = {}
ELEVATION_REQUESTS: list[dict[str, Any]] = []
AUDIT_EVENTS: list[dict[str, Any]] = []


def create_auth_state() -> str:
    return str(uuid.uuid4())


def map_role(idp_role: str) -> str:
    return ROLE_MAPPING.get(idp_role, "ZSP_VIEWER")


def audit(event_type: str, actor: str, detail: str, metadata: dict[str, Any] | None = None) -> None:
    AUDIT_EVENTS.insert(
        0,
        {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "actor": actor,
            "detail": detail,
            "metadata": metadata or {},
            "created_at": time.time(),
        },
    )


def jit_provision_user(claims: dict[str, Any]) -> LocalUser:
    username = str(claims.get("preferred_username") or claims.get("sub") or "unknown")
    idp_role = str(claims.get("role") or "READ_ONLY")
    app_role = map_role(idp_role)

    existing = LOCAL_USERS.get(username)
    if existing:
        existing.last_login_at = time.time()
        audit("USER_LOGIN", username, "Existing local account signed in through IdP", {"app_role": existing.app_role})
        return existing

    user = LocalUser(
        user_id=str(uuid.uuid4()),
        username=username,
        display_name=str(claims.get("name") or username),
        email=str(claims.get("email") or f"{username}@example.com"),
        idp_role=idp_role,
        app_role=app_role,
    )
    LOCAL_USERS[username] = user
    audit("JIT_PROVISION_USER", username, "Local user provisioned just-in-time from IdP claims", {"app_role": app_role})
    return user


def create_session(username: str) -> str:
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = username
    return session_id


def destroy_session(session_id: str | None) -> None:
    if session_id:
        SESSIONS.pop(session_id, None)


def get_user_from_session(session_id: str | None) -> LocalUser | None:
    if not session_id:
        return None
    username = SESSIONS.get(session_id)
    if not username:
        return None
    return LOCAL_USERS.get(username)


def request_elevation(user: LocalUser, target_role: str, reason: str) -> dict[str, Any]:
    request = {
        "request_id": str(uuid.uuid4()),
        "requester": user.username,
        "target_role": target_role,
        "reason": reason,
        "status": "APPROVED" if "APPROVE_ELEVATION" in user.permissions else "PENDING_APPROVAL",
        "created_at": time.time(),
        "expires_at": time.time() + 1800,
    }
    ELEVATION_REQUESTS.insert(0, request)
    audit("ELEVATION_REQUEST_CREATED", user.username, f"Requested temporary {target_role} access", request)
    if request["status"] == "APPROVED":
        audit("ELEVATION_AUTO_APPROVED", user.username, f"Temporary {target_role} access auto-approved for privileged reviewer/admin", request)
    return request
