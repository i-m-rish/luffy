from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

APP_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = APP_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from domain import AUDIT_EVENTS, LOCAL_USERS, SESSIONS, create_session, jit_provision_user  # noqa: E402
from fastapi_app import app  # noqa: E402

client = TestClient(app)


def reset_zsp_state() -> None:
    LOCAL_USERS.clear()
    SESSIONS.clear()
    AUDIT_EVENTS.clear()


def test_usecase_zsp_jit_provisions_operator_from_explicit_app_role_claim() -> None:
    reset_zsp_state()

    user = jit_provision_user(
        {
            "preferred_username": "reader",
            "name": "Read Only User",
            "email": "read.only@example.com",
            "role": "READ_ONLY",
            "app_role": "ZSP_OPERATOR",
            "app_roles": {"luffy-zsp": "ZSP_OPERATOR"},
        }
    )

    assert user.username == "reader"
    assert user.app_role == "ZSP_OPERATOR"
    assert "REQUEST_ELEVATION" in user.permissions
    assert "VIEW_AUDIT" not in user.permissions
    assert AUDIT_EVENTS[0]["event_type"] == "JIT_PROVISION_USER"
    assert AUDIT_EVENTS[0]["metadata"]["app_role"] == "ZSP_OPERATOR"


def test_usecase_zsp_jit_updates_existing_user_when_assignment_changes() -> None:
    reset_zsp_state()

    first_login = jit_provision_user(
        {
            "preferred_username": "reader",
            "name": "Read Only User",
            "email": "read.only@example.com",
            "role": "READ_ONLY",
            "app_role": "ZSP_VIEWER",
        }
    )
    second_login = jit_provision_user(
        {
            "preferred_username": "reader",
            "name": "Read Only User",
            "email": "read.only@example.com",
            "role": "READ_ONLY",
            "app_role": "ZSP_APPROVER",
        }
    )

    assert first_login.user_id == second_login.user_id
    assert second_login.app_role == "ZSP_APPROVER"
    assert "APPROVE_ELEVATION" in second_login.permissions
    assert "VIEW_AUDIT" in second_login.permissions
    assert AUDIT_EVENTS[0]["event_type"] == "USER_LOGIN"
    assert AUDIT_EVENTS[0]["metadata"]["app_role"] == "ZSP_APPROVER"


def test_usecase_zsp_viewer_cannot_view_audit_api() -> None:
    reset_zsp_state()
    user = jit_provision_user(
        {
            "preferred_username": "reader",
            "name": "Read Only User",
            "email": "read.only@example.com",
            "role": "READ_ONLY",
            "app_role": "ZSP_VIEWER",
        }
    )
    session_id = create_session(user.username)
    client.cookies.set("luffy_zsp_session", session_id)

    response = client.get("/api/audit")

    assert response.status_code == 403
    assert response.json()["detail"] == "Audit permission required"


def test_usecase_zsp_approver_can_view_audit_api() -> None:
    reset_zsp_state()
    user = jit_provision_user(
        {
            "preferred_username": "reviewer",
            "name": "Access Reviewer",
            "email": "access.reviewer@example.com",
            "role": "ACCESS_REVIEWER",
            "app_role": "ZSP_APPROVER",
        }
    )
    session_id = create_session(user.username)
    client.cookies.set("luffy_zsp_session", session_id)

    response = client.get("/api/audit")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
