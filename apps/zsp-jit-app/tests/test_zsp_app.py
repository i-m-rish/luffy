from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

APP_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = APP_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from fastapi_app import app  # noqa: E402

client = TestClient(app)


def test_zsp_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "zsp-jit-app"}


def test_zsp_home_redirects_to_login_when_unauthenticated() -> None:
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_zsp_login_redirects_to_idp_authorize() -> None:
    response = client.get("/login", follow_redirects=False)

    assert response.status_code == 303
    assert "http://127.0.0.1:8002/oauth/authorize" in response.headers["location"]
    assert "client_id=luffy-zsp" in response.headers["location"]


def test_zsp_profile_requires_authentication() -> None:
    response = client.get("/api/me")

    assert response.status_code == 401


def test_zsp_audit_requires_authentication() -> None:
    response = client.get("/api/audit")

    assert response.status_code == 401
