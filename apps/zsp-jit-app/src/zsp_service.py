from __future__ import annotations

from typing import Any

from domain import (
    AUDIT_EVENTS,
    ELEVATION_REQUESTS,
    LOCAL_USERS,
    audit,
    create_session,
    destroy_session,
    get_user_from_session,
    jit_provision_user,
    request_elevation,
)


class ZspService:
    """Application service for JIT provisioning, sessions, elevation, and audit."""

    def health(self) -> dict[str, object]:
        return {"status": "ok", "service": "zsp-jit-app"}

    def create_session_from_claims(self, claims: dict[str, Any]) -> tuple[str, Any]:
        user = jit_provision_user(claims)
        session_id = create_session(user.username)
        return session_id, user

    def get_user(self, session_id: str | None):
        return get_user_from_session(session_id)

    def logout(self, session_id: str | None) -> None:
        user = get_user_from_session(session_id)
        if user:
            audit("USER_LOGOUT", user.username, "User logged out")
        destroy_session(session_id)

    def users(self) -> list[dict[str, object]]:
        return [user.as_dict() for user in LOCAL_USERS.values()]

    def elevation_requests(self) -> list[dict[str, object]]:
        return ELEVATION_REQUESTS

    def audit_events(self) -> list[dict[str, object]]:
        return AUDIT_EVENTS

    def create_elevation_request(self, user, target_role: str, reason: str) -> dict[str, object]:
        return request_elevation(user, target_role, reason)


zsp_service = ZspService()
