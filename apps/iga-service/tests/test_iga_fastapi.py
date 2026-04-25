from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

APP_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = APP_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from fastapi_app import app  # noqa: E402

client = TestClient(app)


def test_fastapi_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "iga-service"}


def test_fastapi_applications_endpoint() -> None:
    response = client.get("/applications")

    assert response.status_code == 200
    applications = response.json()
    assert len(applications) == 8
    assert any(application["application_id"] == "jdbc-target" for application in applications)


def test_fastapi_identity_access_endpoint() -> None:
    response = client.get("/governance/identity/IGA-IDENTITY-1001/access")

    assert response.status_code == 200
    payload = response.json()
    assert payload["identity"]["employee_id"] == "1001"
    assert payload["accounts"][0]["account"]["lan_id"] == "RSINGH01"


def test_fastapi_unknown_identity_returns_404() -> None:
    response = client.get("/governance/identity/IGA-IDENTITY-UNKNOWN/access")

    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "identity_not_found"


def test_fastapi_orphan_accounts_endpoint() -> None:
    response = client.get("/governance/orphan-accounts")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["account"]["lan_id"] == "ORPHAN01"


def test_fastapi_high_risk_access_endpoint() -> None:
    response = client.get("/governance/high-risk-access")

    assert response.status_code == 200
    payload = response.json()
    names = {item["entitlement"]["entitlement_name"] for item in payload}
    assert "Remediation Manager" in names
    assert "System Administrator" in names


def test_iga_ui_dashboard_renders_html() -> None:
    response = client.get("/ui")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Luffy IGA Dashboard" in response.text
    assert "Orphan Accounts" in response.text


def test_iga_ui_accounts_renders_html() -> None:
    response = client.get("/ui/accounts")

    assert response.status_code == 200
    assert "ORPHAN01" in response.text
    assert "MATCHED" in response.text


def test_iga_ui_high_risk_access_renders_html() -> None:
    response = client.get("/ui/high-risk-access")

    assert response.status_code == 200
    assert "System Administrator" in response.text
    assert "Remediation Manager" in response.text
