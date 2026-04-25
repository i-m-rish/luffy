from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

APP_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = APP_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from auth import SESSION_COOKIE_NAME, create_session_from_claims  # noqa: E402
from fastapi_app import app  # noqa: E402

client = TestClient(app)


def authenticated_client(role: str = "IGA_ADMIN") -> TestClient:
    test_client = TestClient(app)
    session_id = create_session_from_claims(
        {
            "sub": f"test-{role.lower()}",
            "preferred_username": f"test-{role.lower()}",
            "name": f"Test {role}",
            "email": f"test-{role.lower()}@example.com",
            "role": role,
        }
    )
    test_client.cookies.set(SESSION_COOKIE_NAME, session_id)
    return test_client


def test_fastapi_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "iga-service"}


def test_protected_api_requires_authentication() -> None:
    response = client.get("/applications")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_ui_redirects_to_login_when_unauthenticated() -> None:
    response = client.get("/ui", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_login_redirects_to_idp() -> None:
    response = client.get("/login", follow_redirects=False)

    assert response.status_code == 303
    assert "http://127.0.0.1:8002/oauth/authorize" in response.headers["location"]
    assert "client_id=luffy-iga" in response.headers["location"]


def test_fastapi_applications_endpoint_for_admin() -> None:
    auth_client = authenticated_client("IGA_ADMIN")
    response = auth_client.get("/applications")

    assert response.status_code == 200
    applications = response.json()
    assert len(applications) == 8
    assert any(application["application_id"] == "jdbc-target" for application in applications)


def test_fastapi_identity_access_endpoint_for_admin() -> None:
    auth_client = authenticated_client("IGA_ADMIN")
    response = auth_client.get("/governance/identity/IGA-IDENTITY-1001/access")

    assert response.status_code == 200
    payload = response.json()
    assert payload["identity"]["employee_id"] == "1001"
    assert payload["accounts"][0]["account"]["lan_id"] == "RSINGH01"


def test_fastapi_unknown_identity_returns_404_for_admin() -> None:
    auth_client = authenticated_client("IGA_ADMIN")
    response = auth_client.get("/governance/identity/IGA-IDENTITY-UNKNOWN/access")

    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "identity_not_found"


def test_fastapi_orphan_accounts_endpoint_for_admin() -> None:
    auth_client = authenticated_client("IGA_ADMIN")
    response = auth_client.get("/governance/orphan-accounts")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["account"]["lan_id"] == "ORPHAN01"


def test_fastapi_high_risk_access_endpoint_for_admin() -> None:
    auth_client = authenticated_client("IGA_ADMIN")
    response = auth_client.get("/governance/high-risk-access")

    assert response.status_code == 200
    payload = response.json()
    names = {item["entitlement"]["entitlement_name"] for item in payload}
    assert "Remediation Manager" in names
    assert "System Administrator" in names


def test_read_only_user_cannot_access_high_risk_api() -> None:
    auth_client = authenticated_client("READ_ONLY")
    response = auth_client.get("/governance/high-risk-access")

    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "permission_denied"


def test_iga_ui_dashboard_renders_html_for_admin() -> None:
    auth_client = authenticated_client("IGA_ADMIN")
    response = auth_client.get("/ui")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Luffy Identity Security Console" in response.text
    assert "Orphan Accounts" in response.text


def test_iga_ui_accounts_renders_html_for_admin() -> None:
    auth_client = authenticated_client("IGA_ADMIN")
    response = auth_client.get("/ui/accounts")

    assert response.status_code == 200
    assert "ORPHAN01" in response.text
    assert "MATCHED" in response.text


def test_iga_ui_high_risk_access_renders_html_for_admin() -> None:
    auth_client = authenticated_client("IGA_ADMIN")
    response = auth_client.get("/ui/high-risk-access")

    assert response.status_code == 200
    assert "System Administrator" in response.text
    assert "Remediation Manager" in response.text


def test_read_only_user_is_redirected_from_high_risk_ui() -> None:
    auth_client = authenticated_client("READ_ONLY")
    response = auth_client.get("/ui/high-risk-access", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/forbidden"
