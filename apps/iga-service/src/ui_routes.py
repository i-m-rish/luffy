from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from services.governance_service import governance_service
from ui.components import badge, callout, metric_card, page_shell, table

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
        ["ID", "Name", "Pattern", "Risk", "Accounts", "Entitlements", "Assignments", "Critical Entitlements"],
        rows,
    )


@router.get("/ui", response_class=HTMLResponse)
def ui_dashboard() -> HTMLResponse:
    data = governance_service.dashboard()
    top_risks = [risk for risk in data["top_risks"] if risk]
    cards = {
        "Applications": data["application_count"],
        "Identities": data["identity_count"],
        "Accounts": data["account_count"],
        "Active Accounts": data["active_account_count"],
        "Assignments": data["assignment_count"],
        "Correlation Coverage": f"{data['correlation_coverage_percent']}%",
        "Orphan Accounts": data["orphan_account_count"],
        "High-Risk Access": data["high_risk_access_count"],
        "Critical Entitlements": data["critical_entitlement_count"],
        "Terminated Identities": data["terminated_identity_count"],
    }
    card_html = "".join(metric_card(label, value) for label, value in cards.items())
    body = f"""
      <section class="grid">{card_html}</section>
      {callout("Governance focus", top_risks)}
      <h2 class="section-title">Application access summary</h2>
      {render_application_summary_table()}
    """
    return HTMLResponse(
        page_shell(
            "Luffy IGA Dashboard",
            body,
            "Governance visibility over identities, accounts, entitlements, risk, and correlation.",
        )
    )


@router.get("/ui/applications", response_class=HTMLResponse)
def ui_applications() -> HTMLResponse:
    return HTMLResponse(page_shell("IGA Applications", render_application_summary_table()))


@router.get("/ui/identities", response_class=HTMLResponse)
def ui_identities() -> HTMLResponse:
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
        ["ID", "Name", "Employee ID", "LAN ID", "Status", "Accounts", "Assignments", "High Risk"],
        rows,
    )
    return HTMLResponse(page_shell("IGA Identities", body))


@router.get("/ui/identity/{identity_id}/access", response_class=HTMLResponse)
def ui_identity_access(identity_id: str) -> HTMLResponse:
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
      <h2 class="section-title">Access</h2>
      {table(["Application", "Account", "Entitlement", "Risk", "Assigned By", "Assigned At"], rows)}
    """
    return HTMLResponse(page_shell("IGA Identity Access", body))


@router.get("/ui/accounts", response_class=HTMLResponse)
def ui_accounts() -> HTMLResponse:
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
    return HTMLResponse(page_shell("IGA Accounts", table(["ID", "Application", "LAN ID", "Email", "Status", "Correlation"], rows)))


@router.get("/ui/entitlements", response_class=HTMLResponse)
def ui_entitlements() -> HTMLResponse:
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
    return HTMLResponse(page_shell("IGA Entitlements", table(["ID", "Application", "Name", "Description", "Risk"], rows)))


@router.get("/ui/correlation-results", response_class=HTMLResponse)
def ui_correlation_results() -> HTMLResponse:
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
    body = table(["ID", "Account", "Identity", "Result", "Match Attribute", "Confidence", "Reason"], rows)
    return HTMLResponse(page_shell("IGA Correlation Results", body))


@router.get("/ui/orphan-accounts", response_class=HTMLResponse)
def ui_orphan_accounts() -> HTMLResponse:
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
    return HTMLResponse(page_shell("IGA Orphan Accounts", table(["Account", "Application", "LAN ID", "Email", "Reason"], rows)))


@router.get("/ui/high-risk-access", response_class=HTMLResponse)
def ui_high_risk_access() -> HTMLResponse:
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
    return HTMLResponse(page_shell("IGA High-Risk Access", table(["LAN ID", "Application", "Entitlement", "Risk", "Assigned By"], rows)))
