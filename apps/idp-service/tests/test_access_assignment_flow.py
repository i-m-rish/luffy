from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

APP_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = APP_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from access_model import APP_ROLE_ASSIGNMENTS  # noqa: E402
from fastapi_app import app  # noqa: E402

client = TestClient(app)


def restore_assignments(snapshot: dict[str, dict[str, str]]) -> None:
    APP_ROLE_ASSIGNMENTS.clear()
    APP_ROLE_ASSIGNMENTS.update({user: roles.copy() for user, roles in snapshot.items()})


def test_usecase_idp_assignment_api_changes_token_app_role_claim() -> None:
    previous_assignments = {user: roles.copy() for user, roles in APP_ROLE_ASSIGNMENTS.items()}
    try:
        assign_response = client.post(
            "/api/access/assignments",
            data={"username": "reader", "client_id": "luffy-zsp", "app_role": "ZSP_OPERATOR"},
        )
        assert assign_response.status_code == 200
        assert assign_response.json() == {
            "username": "reader",
            "client_id": "luffy-zsp",
            "app_role": "ZSP_OPERATOR",
            "status": "ASSIGNED",
        }

        login_response = client.post(
            "/oauth/authorize",
            data={
                "client_id": "luffy-zsp",
                "redirect_uri": "http://127.0.0.1:8003/auth/callback",
                "state": "flow-test",
                "username": "reader",
                "password": "reader123",
            },
            follow_redirects=False,
        )
        assert login_response.status_code == 303
        location = login_response.headers["location"]
        code = location.split("code=")[1].split("&")[0]

        token_response = client.post(
            "/oauth/token",
            data={
                "code": code,
                "client_id": "luffy-zsp",
                "redirect_uri": "http://127.0.0.1:8003/auth/callback",
            },
        )
        assert token_response.status_code == 200
        claims = token_response.json()["claims"]
        assert claims["preferred_username"] == "reader"
        assert claims["app_roles"]["luffy-zsp"] == "ZSP_OPERATOR"
        assert claims["app_role"] == "ZSP_OPERATOR"
        assert claims["role"] == "APP_OWNER"
    finally:
        restore_assignments(previous_assignments)


def test_usecase_idp_rejects_invalid_app_role_assignment() -> None:
    response = client.post(
        "/api/access/assignments",
        data={"username": "reader", "client_id": "luffy-zsp", "app_role": "NOT_A_REAL_ROLE"},
    )

    assert response.status_code == 400
    assert "not valid" in response.json()["detail"]


def test_usecase_idp_can_remove_app_role_assignment() -> None:
    previous_assignments = {user: roles.copy() for user, roles in APP_ROLE_ASSIGNMENTS.items()}
    try:
        client.post(
            "/api/access/assignments",
            data={"username": "reader", "client_id": "luffy-zsp", "app_role": "ZSP_OPERATOR"},
        )
        remove_response = client.request(
            "DELETE",
            "/api/access/assignments",
            data={"username": "reader", "client_id": "luffy-zsp"},
        )

        assert remove_response.status_code == 200
        assert remove_response.json() == {"username": "reader", "client_id": "luffy-zsp", "status": "REMOVED"}
        assert "luffy-zsp" not in APP_ROLE_ASSIGNMENTS.get("reader", {})
    finally:
        restore_assignments(previous_assignments)
