from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

APP_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = APP_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from fastapi_app import app  # noqa: E402

client = TestClient(app)


def test_idp_fastapi_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "idp-service"}


def test_idp_dashboard_metrics() -> None:
    response = client.get("/dashboard")

    assert response.status_code == 200
    payload = response.json()
    assert payload["identity_count"] == 6
    assert payload["group_count"] == 5
    assert payload["app_registration_count"] == 5
    assert payload["machine_identity_count"] == 4


def test_idp_identity_profile() -> None:
    response = client.get("/identity/IDP-1004/profile")

    assert response.status_code == 200
    payload = response.json()
    assert payload["identity"]["lan_id"] == "PKAPOOR01"
    assert payload["groups"]


def test_idp_unknown_identity_returns_404() -> None:
    response = client.get("/identity/IDP-UNKNOWN/profile")

    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "identity_not_found"


def test_idp_ui_dashboard_renders_html() -> None:
    response = client.get("/ui")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Luffy IdP Dashboard" in response.text


def test_idp_ui_identities_renders_html() -> None:
    response = client.get("/ui/identities")

    assert response.status_code == 200
    assert "Rishabh Singh" in response.text
