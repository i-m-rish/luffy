from __future__ import annotations

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = APP_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from repository import get_high_risk_access, get_identity_access, get_orphan_accounts, get_routes  # noqa: E402


def test_api_routes_include_expected_read_only_endpoints() -> None:
    routes = get_routes()

    assert "/health" in routes
    assert "/applications" in routes
    assert "/identities" in routes
    assert "/accounts" in routes
    assert "/entitlements" in routes
    assert "/assignments" in routes
    assert "/correlation-results" in routes
    assert "/governance/orphan-accounts" in routes
    assert "/governance/high-risk-access" in routes


def test_health_route_returns_service_status() -> None:
    routes = get_routes()

    assert routes["/health"] == {"status": "ok", "service": "iga-service"}


def test_identity_access_returns_accounts_and_assignments() -> None:
    result = get_identity_access("IGA-IDENTITY-1001")

    assert result is not None
    assert result["identity"]["employee_id"] == "1001"
    assert len(result["accounts"]) == 1
    assert result["accounts"][0]["account"]["lan_id"] == "RSINGH01"
    assert result["accounts"][0]["assignments"]


def test_identity_access_returns_none_for_unknown_identity() -> None:
    result = get_identity_access("IGA-IDENTITY-DOES-NOT-EXIST")

    assert result is None


def test_orphan_accounts_endpoint_data() -> None:
    orphan_accounts = get_orphan_accounts()

    assert len(orphan_accounts) == 1
    assert orphan_accounts[0]["account"]["lan_id"] == "ORPHAN01"
    assert orphan_accounts[0]["correlation_result"]["result"] == "ORPHAN"


def test_high_risk_access_endpoint_data() -> None:
    high_risk_access = get_high_risk_access()
    entitlement_names = {
        item["entitlement"]["entitlement_name"] for item in high_risk_access
    }

    assert "Remediation Manager" in entitlement_names
    assert "System Administrator" in entitlement_names
