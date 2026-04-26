from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

APP_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = APP_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from auth import SESSION_COOKIE_NAME, create_session_from_claims  # noqa: E402
from fulfillment_routes import FULFILLMENT_AUDIT  # noqa: E402
from management_routes import ACCESS_REQUESTS  # noqa: E402
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


def reset_iga_flow_state() -> None:
    ACCESS_REQUESTS.clear()
    FULFILLMENT_AUDIT.clear()


def test_usecase_iga_access_request_is_created_and_visible_in_queue() -> None:
    reset_iga_flow_state()
    auth_client = authenticated_client("IGA_ADMIN")

    response = auth_client.post(
        "/api/requests/access",
        data={
            "target_identity_id": "IGA-IDENTITY-1004",
            "entitlement_id": "IGA-ENT-ZSP-OPERATOR",
            "access_type": "ADD_ACCESS",
            "justification": "Need operator access for incident response drill.",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["request_id"] == "AR-0001"
    assert payload["status"] == "SUBMITTED"
    assert ACCESS_REQUESTS[0]["entitlement_id"] == "IGA-ENT-ZSP-OPERATOR"

    queue_response = auth_client.get("/ui/requests/access/fulfillment")
    assert queue_response.status_code == 200
    assert "AR-0001" in queue_response.text
    assert "Fulfill to IdP" in queue_response.text


def test_usecase_iga_fulfillment_rejects_non_zsp_entitlement_before_calling_idp() -> None:
    reset_iga_flow_state()
    auth_client = authenticated_client("IGA_ADMIN")
    auth_client.post(
        "/api/requests/access",
        data={
            "target_identity_id": "IGA-IDENTITY-1004",
            "entitlement_id": "IGA-ENT-JDBC-ASSET-VIEWER",
            "access_type": "ADD_ACCESS",
            "justification": "This should not be fulfilled by the ZSP IdP connector.",
        },
    )

    response = auth_client.post("/api/requests/access/AR-0001/fulfill")

    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "unsupported_target_application"
    assert ACCESS_REQUESTS[0]["status"] == "SUBMITTED"
    assert FULFILLMENT_AUDIT == []


def test_usecase_read_only_user_cannot_fulfill_access_request() -> None:
    reset_iga_flow_state()
    admin_client = authenticated_client("IGA_ADMIN")
    read_only_client = authenticated_client("READ_ONLY")
    admin_client.post(
        "/api/requests/access",
        data={
            "target_identity_id": "IGA-IDENTITY-1004",
            "entitlement_id": "IGA-ENT-ZSP-OPERATOR",
            "access_type": "ADD_ACCESS",
            "justification": "Need operator access.",
        },
    )

    response = read_only_client.post("/api/requests/access/AR-0001/fulfill")

    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "permission_denied"
    assert ACCESS_REQUESTS[0]["status"] == "SUBMITTED"
