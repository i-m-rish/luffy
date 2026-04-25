from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from auth import require_ui_permission
from services.governance_service import governance_service
from ui.components import action_tile, badge, callout, metric_card, page_shell, table

router = APIRouter(tags=["IGA UI"])


def render_application_summary_table() -> str:
    rows = []
    for application in governance_service.application_access_summary():
        risk = str(application["risk_level"])
        rows.append(
            "<tr>"
            f"<td>{application['application_id']}</td>"
            f"<td>{application['application_name']}</td>"
            f"<td>{application['integration_pattern']}</td>"
            f"<td>{badge(risk, 'risk-' + risk)}</td>"
            f"<td>{application['account_count']}</td>"
            f"<td>{application['entitlement_count']}</td>"
            f"<td>{application['assignment_count']}</td>"
            f"<td>{application['critical_entitlement_count']}</td>"
            "</tr>"
        )
    return table(
        ["Source ID", "Source Name", "Connector", "Risk", "Accounts", "Entitlements", "Assignments", "Privileged Entitlements"],
        rows,
    )


def enforce_ui(request: Request, permission: str) -> RedirectResponse | None:
    result = require_ui_permission(request, permission)
    if isinstance(result, RedirectResponse):
        return result
    return None


@router.get("/ui", response_class=HTMLResponse, response_model=None)
def ui_dashboard(request: Request) -> Response:
    redirect = enforce_ui(request, "VIEW_DASHBOARD")
    if redirect:
        return redirect

    data = governance_service.dashboard()
    top_risks = [risk for risk in data["top_risks"] if risk]
    cards = {
        "Sources": data["application_count"],
        "Identities": data["identity_count"],
        "Accounts": data["account_count"],
        "Active Accounts": data["active_account_count"],
        "Access Assignments": data["assignment_count"],
        "Correlation Coverage": f"{data['correlation_coverage_percent']}%",
        "Orphan Accounts": data["orphan_account_count"],
        "High-Risk Access": data["high_risk_access_count"],
        "Privileged Entitlements": data["critical_entitlement_count"],
        "Terminated Identities": data["terminated_identity_count"],
    }
    card_html = "".join(metric_card(label, value) for label, value in cards.items())
    tiles = "".join(
        [
            action_tile("Identity Warehouse", "Search governed identities and open access profiles.", "/ui/identities"),
            action_tile("Sources", "Review onboarded applications, connector style, and risk.", "/ui/applications"),
            action_tile("Access Reviews", "Certification-style review queue and campaign status.", "/ui/access-reviews"),
            action_tile("Policy Violations", "SOD, orphan, leaver, and privileged access findings.", "/ui/policy-violations"),
        ]
    )
    body = f"""
      <section class="grid">{card_html}</section>
      {callout("Governance focus", top_risks)}
      <h2 class="section-title">Quick actions</h2>
      <section class="tile-grid">{tiles}</section>
      <h2 class="section-title">Source access summary</h2>
      {render_application_summary_table()}
    """
    return HTMLResponse(
        page_shell(
            "Luffy Identity Security Console",
            body,
            "SailPoint-style governance cockpit for identities, sources, accounts, entitlements, access reviews, and risk.",
        )
    )


@router.get("/ui/applications", response_class=HTMLResponse, response_model=None)
def ui_applications(request: Request) -> Response:
    redirect = enforce_ui(request, "VIEW_APPLICATIONS")
    if redirect:
        return redirect
    return HTMLResponse(page_shell("Sources", render_application_summary_table(), "Applications onboarded into governance."))


@router.get("/ui/identities", response_class=HTMLResponse, response_model=None)
def ui_identities(request: Request) -> Response:
    redirect = enforce_ui(request, "VIEW_IDENTITIES")
    if redirect:
        return redirect
    rows = []
    for identity in governance_service.identity_access_summary():
        status = str(identity["identity_status"])
        rows.append(
            "<tr>"
            f"<td><a href='/ui/identity/{identity['identity_id']}/access'>{identity['identity_id']}</a></td>"
            f"<td>{identity['display_name']}</td>"
            f"<td>{identity['employee_id']}</td>"
            f"<td>{identity['lan_id']}</td>"
            f"<td>{badge(status, 'status-' + status)}</td>"
            f"<td>{identity['account_count']}</td>"
            f"<td>{identity['assignment_count']}</td>"
            f"<td>{identity['high_risk_assignment_count']}</td>"
            "</tr>"
        )
    body = table(
        ["Identity", "Name", "Employee ID", "Login", "Lifecycle", "Accounts", "Access Items", "High Risk"],
        rows,
    )
    return HTMLResponse(page_shell("Identity Warehouse", body, "Governed people and their access footprint."))


@router.get("/ui/identity/{identity_id}/access", response_class=HTMLResponse, response_model=None)
def ui_identity_access(request: Request, identity_id: str) -> Response:
    redirect = enforce_ui(request, "VIEW_IDENTITIES")
    if redirect:
        return redirect
    access = governance_service.identity_access(identity_id)
    if access is None:
        return HTMLResponse(page_shell("Identity Not Found", f"<div class='card'>No identity found for {identity_id}</div>"))

    identity = access["identity"]
    rows = []
    for account_view in access["accounts"]:
        account = account_view["account"]
        application = account_view["application"]
        for assignment_view in account_view["assignments"]:
            entitlement = assignment_view["entitlement"]
            assignment = assignment_view["assignment"]
            risk = str(entitlement["risk_level"])
            rows.append(
                "<tr>"
                f"<td>{application['application_name']}</td>"
                f"<td>{account['lan_id']}</td>"
                f"<td>{entitlement['entitlement_name']}</td>"
                f"<td>{badge(risk, 'risk-' + risk)}</td>"
                f"<td>{assignment['assigned_by']}</td>"
                f"<td>{assignment['assigned_at']}</td>"
                "</tr>"
            )
    if not rows:
        rows.append("<tr><td colspan='6'>No access found.</td></tr>")

    body = f"""
      <div class="card"><strong>{identity['display_name']}</strong><br />
      <span class="muted">{identity['identity_id']} · {identity['lan_id']} · {identity['identity_status']}</span></div>
      <h2 class="section-title">Access Profile</h2>
      {table(["Source", "Account", "Entitlement", "Risk", "Granted By", "Granted At"], rows)}
    """
    return HTMLResponse(page_shell("Identity Access Profile", body))


@router.get("/ui/accounts", response_class=HTMLResponse, response_model=None)
def ui_accounts(request: Request) -> Response:
    redirect = enforce_ui(request, "VIEW_ACCOUNTS")
    if redirect:
        return redirect
    rows = []
    for account in governance_service.accounts():
        account_status = str(account["account_status"])
        correlation_status = str(account["correlation_status"])
        rows.append(
            "<tr>"
            f"<td>{account['account_id']}</td>"
            f"<td>{account['application_id']}</td>"
            f"<td>{account['lan_id']}</td>"
            f"<td>{account['email']}</td>"
            f"<td>{badge(account_status, 'status-' + account_status)}</td>"
            f"<td>{badge(correlation_status, 'status-' + correlation_status)}</td>"
            "</tr>"
        )
    return HTMLResponse(page_shell("Accounts", table(["Account", "Source", "Login", "Email", "Status", "Correlation"], rows)))


@router.get("/ui/entitlements", response_class=HTMLResponse, response_model=None)
def ui_entitlements(request: Request) -> Response:
    redirect = enforce_ui(request, "VIEW_ENTITLEMENTS")
    if redirect:
        return redirect
    rows = []
    for entitlement in governance_service.entitlements():
        risk = str(entitlement["risk_level"])
        rows.append(
            "<tr>"
            f"<td>{entitlement['entitlement_id']}</td>"
            f"<td>{entitlement['application_id']}</td>"
            f"<td>{entitlement['entitlement_name']}</td>"
            f"<td>{entitlement['entitlement_description']}</td>"
            f"<td>{badge(risk, 'risk-' + risk)}</td>"
            "</tr>"
        )
    return HTMLResponse(page_shell("Entitlement Catalog", table(["Entitlement", "Source", "Display Name", "Description", "Risk"], rows)))


@router.get("/ui/correlation-results", response_class=HTMLResponse, response_model=None)
def ui_correlation_results(request: Request) -> Response:
    redirect = enforce_ui(request, "VIEW_CORRELATION")
    if redirect:
        return redirect
    rows = []
    for result in governance_service.correlation_results():
        status = str(result["result"])
        rows.append(
            "<tr>"
            f"<td>{result['correlation_id']}</td>"
            f"<td>{result['account_id']}</td>"
            f"<td>{result['identity_id'] or '-'}</td>"
            f"<td>{badge(status, 'status-' + status)}</td>"
            f"<td>{result['match_attribute']}</td>"
            f"<td>{result['confidence']}</td>"
            f"<td>{result['reason']}</td>"
            "</tr>"
        )
    body = table(["Run ID", "Account", "Identity", "Result", "Match Attribute", "Confidence", "Reason"], rows)
    return HTMLResponse(page_shell("Correlation Results", body, "Account-to-identity matching results."))


@router.get("/ui/access-reviews", response_class=HTMLResponse, response_model=None)
def ui_access_reviews(request: Request) -> Response:
    redirect = enforce_ui(request, "VIEW_ACCESS_REVIEWS")
    if redirect:
        return redirect
    rows = [
        "<tr><td>Quarterly JDBC Access Review</td><td>Security Asset Operations</td><td>Draft</td><td>5 access items</td><td>App Owner</td></tr>",
        "<tr><td>Privileged Access Review</td><td>All Critical Entitlements</td><td>Design</td><td>1 privileged item</td><td>Security Admin</td></tr>",
        "<tr><td>Orphan Account Review</td><td>Uncorrelated Accounts</td><td>Action Required</td><td>1 orphan account</td><td>IGA Admin</td></tr>",
    ]
    body = table(["Campaign", "Scope", "Status", "Items", "Reviewer"], rows)
    return HTMLResponse(page_shell("Access Reviews", body, "Certification-style access review queue."))


@router.get("/ui/policy-violations", response_class=HTMLResponse, response_model=None)
def ui_policy_violations(request: Request) -> Response:
    redirect = enforce_ui(request, "VIEW_POLICY_VIOLATIONS")
    if redirect:
        return redirect
    rows = [
        "<tr><td>ORPHAN_ACCOUNT</td><td>ORPHAN01 has no correlated identity.</td><td>High</td><td>Open</td></tr>",
        "<tr><td>HIGH_RISK_ACCESS</td><td>System Administrator entitlement exists and needs certification.</td><td>Critical</td><td>Open</td></tr>",
        "<tr><td>LEAVER_GOVERNANCE</td><td>Terminated identity exists for leaver testing.</td><td>Medium</td><td>Monitor</td></tr>",
    ]
    body = table(["Policy", "Finding", "Severity", "Status"], rows)
    return HTMLResponse(page_shell("Policy Violations", body, "SOD, orphan, leaver, and privileged access findings."))


@router.get("/ui/orphan-accounts", response_class=HTMLResponse, response_model=None)
def ui_orphan_accounts(request: Request) -> Response:
    redirect = enforce_ui(request, "VIEW_ORPHANS")
    if redirect:
        return redirect
    rows = []
    for item in governance_service.orphan_accounts():
        account = item["account"]
        application = item["application"]
        correlation = item["correlation_result"]
        rows.append(
            "<tr>"
            f"<td>{account['account_id']}</td>"
            f"<td>{application['application_name']}</td>"
            f"<td>{account['lan_id']}</td>"
            f"<td>{account['email']}</td>"
            f"<td>{correlation['reason']}</td>"
            "</tr>"
        )
    return HTMLResponse(page_shell("Orphan Accounts", table(["Account", "Source", "Login", "Email", "Reason"], rows)))


@router.get("/ui/high-risk-access", response_class=HTMLResponse, response_model=None)
def ui_high_risk_access(request: Request) -> Response:
    redirect = enforce_ui(request, "VIEW_HIGH_RISK")
    if redirect:
        return redirect
    rows = []
    for item in governance_service.high_risk_access():
        account = item["account"]
        application = item["application"]
        entitlement = item["entitlement"]
        assignment = item["assignment"]
        risk = str(entitlement["risk_level"])
        rows.append(
            "<tr>"
            f"<td>{account['lan_id']}</td>"
            f"<td>{application['application_name']}</td>"
            f"<td>{entitlement['entitlement_name']}</td>"
            f"<td>{badge(risk, 'risk-' + risk)}</td>"
            f"<td>{assignment['assigned_by']}</td>"
            "</tr>"
        )
    return HTMLResponse(page_shell("High-Risk Access", table(["Identity Login", "Source", "Entitlement", "Risk", "Granted By"], rows)))
