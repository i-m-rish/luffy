from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from auth import require_ui_permission
from services.governance_service import governance_service
from ui.components import action_tile, badge, callout, metric_card, page_shell, table

router = APIRouter(tags=["IGA UI"])


def object_link(label: object, href: str) -> str:
    return f"<a href='{href}'>{label}</a>"


def detail_card(title: str, rows: list[tuple[str, object]]) -> str:
    row_html = "".join(f"<tr><th>{label}</th><td>{value}</td></tr>" for label, value in rows)
    return f"<div class='card'><h2 style='margin-top:0'>{title}</h2><table style='min-width:0'>{row_html}</table></div>"


def render_application_summary_table() -> str:
    rows = []
    for application in governance_service.application_access_summary():
        risk = str(application["risk_level"])
        source_link = object_link(application["application_name"], f"/ui/application/{application['application_id']}")
        rows.append(
            "<tr>"
            f"<td>{object_link(application['application_id'], f'/ui/application/{application['application_id']}')}</td>"
            f"<td>{source_link}</td>"
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
            action_tile("Identity Warehouse", "Open identities and drill into accounts/access profiles.", "/ui/identities"),
            action_tile("Sources", "Open app/source records and attached accounts/entitlements.", "/ui/applications"),
            action_tile("High-Risk Access", "Review critical access and jump to account/entitlement objects.", "/ui/high-risk-access"),
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
    return HTMLResponse(page_shell("Luffy Identity Security Console", body, "SailPoint-style governance cockpit with object drill-down across identities, sources, accounts, entitlements, and risk."))


@router.get("/ui/applications", response_class=HTMLResponse, response_model=None)
def ui_applications(request: Request) -> Response:
    redirect = enforce_ui(request, "VIEW_APPLICATIONS")
    if redirect:
        return redirect
    return HTMLResponse(page_shell("Sources", render_application_summary_table(), "Open any source to view attached accounts, entitlements, assignments, and risk."))


@router.get("/ui/application/{application_id}", response_class=HTMLResponse, response_model=None)
def ui_application_detail(request: Request, application_id: str) -> Response:
    redirect = enforce_ui(request, "VIEW_APPLICATIONS")
    if redirect:
        return redirect
    detail = governance_service.application_detail(application_id)
    if detail is None:
        return HTMLResponse(page_shell("Source Not Found", f"<div class='card'>No source found for {application_id}</div>"), status_code=404)

    app = detail["application"]
    account_rows = []
    for view in detail["accounts"]:
        account = view["account"]
        identity = view["identity"]
        correlation = view["correlation"]
        account_rows.append(
            "<tr>"
            f"<td>{object_link(account['account_id'], f'/ui/account/{account['account_id']}')}</td>"
            f"<td>{account['lan_id']}</td>"
            f"<td>{account['email']}</td>"
            f"<td>{object_link(identity['display_name'], f'/ui/identity/{identity['identity_id']}/access') if identity else '-'}</td>"
            f"<td>{badge(account['correlation_status'], 'status-' + account['correlation_status'])}</td>"
            f"<td>{correlation['reason'] if correlation else '-'}</td>"
            "</tr>"
        )
    entitlement_rows = []
    for view in detail["entitlements"]:
        entitlement = view["entitlement"]
        risk = str(entitlement["risk_level"])
        entitlement_rows.append(
            "<tr>"
            f"<td>{object_link(entitlement['entitlement_name'], f'/ui/entitlement/{entitlement['entitlement_id']}')}</td>"
            f"<td>{entitlement['native_entitlement_id']}</td>"
            f"<td>{badge(risk, 'risk-' + risk)}</td>"
            f"<td>{view['assignment_count']}</td>"
            f"<td>{entitlement['entitlement_description']}</td>"
            "</tr>"
        )
    body = "".join([
        detail_card("Source Overview", [
            ("Source ID", app["application_id"]),
            ("Name", app["application_name"]),
            ("Type", app["application_type"]),
            ("Integration Pattern", app["integration_pattern"]),
            ("Risk", badge(app["risk_level"], "risk-" + app["risk_level"])),
            ("Owner", app["owner"]),
            ("Status", badge(app["status"], "status-" + app["status"])),
        ]),
        "<h2 class='section-title'>Attached Accounts</h2>",
        table(["Account", "Login", "Email", "Identity", "Correlation", "Reason"], account_rows or ["<tr><td colspan='6'>No accounts attached.</td></tr>"]),
        "<h2 class='section-title'>Entitlements</h2>",
        table(["Entitlement", "Native ID", "Risk", "Assignments", "Description"], entitlement_rows or ["<tr><td colspan='5'>No entitlements attached.</td></tr>"]),
    ])
    return HTMLResponse(page_shell(f"Source: {app['application_name']}", body, "Source object view with attached account and entitlement objects."))


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
            f"<td>{object_link(identity['identity_id'], f'/ui/identity/{identity['identity_id']}/access')}</td>"
            f"<td>{object_link(identity['display_name'], f'/ui/identity/{identity['identity_id']}/access')}</td>"
            f"<td>{identity['employee_id']}</td>"
            f"<td>{identity['lan_id']}</td>"
            f"<td>{badge(status, 'status-' + status)}</td>"
            f"<td>{identity['account_count']}</td>"
            f"<td>{identity['assignment_count']}</td>"
            f"<td>{identity['high_risk_assignment_count']}</td>"
            "</tr>"
        )
    body = table(["Identity", "Name", "Employee ID", "Login", "Lifecycle", "Accounts", "Access Items", "High Risk"], rows)
    return HTMLResponse(page_shell("Identity Warehouse", body, "Open an identity to view its accounts and access across sources."))


@router.get("/ui/identity/{identity_id}/access", response_class=HTMLResponse, response_model=None)
def ui_identity_access(request: Request, identity_id: str) -> Response:
    redirect = enforce_ui(request, "VIEW_IDENTITIES")
    if redirect:
        return redirect
    access = governance_service.identity_access(identity_id)
    if access is None:
        return HTMLResponse(page_shell("Identity Not Found", f"<div class='card'>No identity found for {identity_id}</div>"), status_code=404)

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
                f"<td>{object_link(application['application_name'], f'/ui/application/{application['application_id']}')}</td>"
                f"<td>{object_link(account['lan_id'], f'/ui/account/{account['account_id']}')}</td>"
                f"<td>{object_link(entitlement['entitlement_name'], f'/ui/entitlement/{entitlement['entitlement_id']}')}</td>"
                f"<td>{badge(risk, 'risk-' + risk)}</td>"
                f"<td>{badge(assignment['assignment_status'], 'status-' + assignment['assignment_status'])}</td>"
                f"<td>{assignment['assigned_by']}</td>"
                f"<td>{assignment['assigned_at']}</td>"
                "</tr>"
            )
    body = f"""
      {detail_card('Identity Overview', [
        ('Identity ID', identity['identity_id']),
        ('Name', identity['display_name']),
        ('Employee ID', identity['employee_id']),
        ('Login', identity['lan_id']),
        ('Email', identity['email']),
        ('Lifecycle', badge(identity['identity_status'], 'status-' + identity['identity_status'])),
        ('Source System', identity['source_system']),
      ])}
      <h2 class="section-title">Access Profile</h2>
      {table(["Source", "Account", "Entitlement", "Risk", "Assignment", "Granted By", "Granted At"], rows or ["<tr><td colspan='7'>No access found.</td></tr>"])}
    """
    return HTMLResponse(page_shell("Identity Access Profile", body, "Identity object view connected to account, source, and entitlement objects."))


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
            f"<td>{object_link(account['account_id'], f'/ui/account/{account['account_id']}')}</td>"
            f"<td>{object_link(account['application_id'], f'/ui/application/{account['application_id']}')}</td>"
            f"<td>{account['lan_id']}</td>"
            f"<td>{account['email']}</td>"
            f"<td>{badge(account_status, 'status-' + account_status)}</td>"
            f"<td>{badge(correlation_status, 'status-' + correlation_status)}</td>"
            "</tr>"
        )
    return HTMLResponse(page_shell("Accounts", table(["Account", "Source", "Login", "Email", "Status", "Correlation"], rows), "Open an account to view attached identity and assigned entitlements."))


@router.get("/ui/account/{account_id}", response_class=HTMLResponse, response_model=None)
def ui_account_detail(request: Request, account_id: str) -> Response:
    redirect = enforce_ui(request, "VIEW_ACCOUNTS")
    if redirect:
        return redirect
    detail = governance_service.account_detail(account_id)
    if detail is None:
        return HTMLResponse(page_shell("Account Not Found", f"<div class='card'>No account found for {account_id}</div>"), status_code=404)

    account = detail["account"]
    application = detail["application"]
    identity = detail["identity"]
    correlation = detail["correlation"]
    assignment_rows = []
    for view in detail["assignments"]:
        assignment = view["assignment"]
        entitlement = view["entitlement"]
        risk = str(entitlement["risk_level"])
        assignment_rows.append(
            "<tr>"
            f"<td>{object_link(entitlement['entitlement_name'], f'/ui/entitlement/{entitlement['entitlement_id']}')}</td>"
            f"<td>{badge(risk, 'risk-' + risk)}</td>"
            f"<td>{badge(assignment['assignment_status'], 'status-' + assignment['assignment_status'])}</td>"
            f"<td>{assignment['assigned_by']}</td>"
            f"<td>{assignment['assigned_at']}</td>"
            "</tr>"
        )
    body = "".join([
        detail_card("Account Overview", [
            ("Account ID", account["account_id"]),
            ("Native Account", account["native_account_id"]),
            ("Source", object_link(application["application_name"], f"/ui/application/{application['application_id']}") if application else account["application_id"]),
            ("Login", account["lan_id"]),
            ("Email", account["email"]),
            ("Status", badge(account["account_status"], "status-" + account["account_status"])),
            ("Correlation", badge(account["correlation_status"], "status-" + account["correlation_status"])),
            ("Identity", object_link(identity["display_name"], f"/ui/identity/{identity['identity_id']}/access") if identity else "-"),
            ("Correlation Reason", correlation["reason"] if correlation else "-"),
        ]),
        "<h2 class='section-title'>Assigned Entitlements</h2>",
        table(["Entitlement", "Risk", "Assignment", "Granted By", "Granted At"], assignment_rows or ["<tr><td colspan='5'>No assigned entitlements.</td></tr>"]),
    ])
    return HTMLResponse(page_shell(f"Account: {account['lan_id']}", body, "Account object view connected to identity, source, and entitlements."))


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
            f"<td>{object_link(entitlement['entitlement_id'], f'/ui/entitlement/{entitlement['entitlement_id']}')}</td>"
            f"<td>{object_link(entitlement['application_id'], f'/ui/application/{entitlement['application_id']}')}</td>"
            f"<td>{object_link(entitlement['entitlement_name'], f'/ui/entitlement/{entitlement['entitlement_id']}')}</td>"
            f"<td>{entitlement['entitlement_description']}</td>"
            f"<td>{badge(risk, 'risk-' + risk)}</td>"
            "</tr>"
        )
    return HTMLResponse(page_shell("Entitlement Catalog", table(["Entitlement", "Source", "Display Name", "Description", "Risk"], rows), "Open an entitlement to view assigned accounts and identities."))


@router.get("/ui/entitlement/{entitlement_id}", response_class=HTMLResponse, response_model=None)
def ui_entitlement_detail(request: Request, entitlement_id: str) -> Response:
    redirect = enforce_ui(request, "VIEW_ENTITLEMENTS")
    if redirect:
        return redirect
    detail = governance_service.entitlement_detail(entitlement_id)
    if detail is None:
        return HTMLResponse(page_shell("Entitlement Not Found", f"<div class='card'>No entitlement found for {entitlement_id}</div>"), status_code=404)

    entitlement = detail["entitlement"]
    application = detail["application"]
    risk = str(entitlement["risk_level"])
    assignment_rows = []
    for view in detail["assignments"]:
        assignment = view["assignment"]
        account = view["account"]
        identity = view["identity"]
        assignment_rows.append(
            "<tr>"
            f"<td>{object_link(account['lan_id'], f'/ui/account/{account['account_id']}') if account else '-'}</td>"
            f"<td>{object_link(identity['display_name'], f'/ui/identity/{identity['identity_id']}/access') if identity else '-'}</td>"
            f"<td>{badge(assignment['assignment_status'], 'status-' + assignment['assignment_status'])}</td>"
            f"<td>{assignment['assigned_by']}</td>"
            f"<td>{assignment['assigned_at']}</td>"
            "</tr>"
        )
    body = "".join([
        detail_card("Entitlement Overview", [
            ("Entitlement ID", entitlement["entitlement_id"]),
            ("Name", entitlement["entitlement_name"]),
            ("Native ID", entitlement["native_entitlement_id"]),
            ("Source", object_link(application["application_name"], f"/ui/application/{application['application_id']}") if application else entitlement["application_id"]),
            ("Risk", badge(risk, "risk-" + risk)),
            ("Status", badge(entitlement["status"], "status-" + entitlement["status"])),
            ("Description", entitlement["entitlement_description"]),
        ]),
        "<h2 class='section-title'>Assigned Accounts</h2>",
        table(["Account", "Identity", "Assignment", "Granted By", "Granted At"], assignment_rows or ["<tr><td colspan='5'>No assignments found.</td></tr>"]),
    ])
    return HTMLResponse(page_shell(f"Entitlement: {entitlement['entitlement_name']}", body, "Entitlement object view connected to accounts, identities, and source."))


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
            f"<td>{object_link(result['account_id'], f'/ui/account/{result['account_id']}')}</td>"
            f"<td>{object_link(result['identity_id'], f'/ui/identity/{result['identity_id']}/access') if result['identity_id'] else '-'}</td>"
            f"<td>{badge(status, 'status-' + status)}</td>"
            f"<td>{result['match_attribute']}</td>"
            f"<td>{result['confidence']}</td>"
            f"<td>{result['reason']}</td>"
            "</tr>"
        )
    body = table(["Run ID", "Account", "Identity", "Result", "Match Attribute", "Confidence", "Reason"], rows)
    return HTMLResponse(page_shell("Correlation Results", body, "Account-to-identity matching results with clickable linked objects."))


@router.get("/ui/access-reviews", response_class=HTMLResponse, response_model=None)
def ui_access_reviews(request: Request) -> Response:
    redirect = enforce_ui(request, "VIEW_ACCESS_REVIEWS")
    if redirect:
        return redirect
    rows = [
        "<tr><td>Quarterly JDBC Access Review</td><td><a href='/ui/application/jdbc-target'>Security Asset Operations</a></td><td>Draft</td><td>5 access items</td><td>App Owner</td></tr>",
        "<tr><td>ZSP Temporary Privilege Review</td><td><a href='/ui/application/zsp-jit-app'>Secure Operations Portal</a></td><td>Design</td><td>Critical temporary access</td><td>Security Admin</td></tr>",
        "<tr><td>Orphan Account Review</td><td><a href='/ui/orphan-accounts'>Uncorrelated Accounts</a></td><td>Action Required</td><td>1 orphan account</td><td>IGA Admin</td></tr>",
    ]
    body = table(["Campaign", "Scope", "Status", "Items", "Reviewer"], rows)
    return HTMLResponse(page_shell("Access Reviews", body, "Certification-style access review queue with links to governed objects."))


@router.get("/ui/policy-violations", response_class=HTMLResponse, response_model=None)
def ui_policy_violations(request: Request) -> Response:
    redirect = enforce_ui(request, "VIEW_POLICY_VIOLATIONS")
    if redirect:
        return redirect
    rows = [
        "<tr><td>ORPHAN_ACCOUNT</td><td><a href='/ui/account/IGA-ACC-JDBC-5'>ORPHAN01</a> has no correlated identity.</td><td>High</td><td>Open</td></tr>",
        "<tr><td>HIGH_RISK_ACCESS</td><td><a href='/ui/entitlement/IGA-ENT-JDBC-SYSTEM-ADMINISTRATOR'>System Administrator</a> exists and needs certification.</td><td>Critical</td><td>Open</td></tr>",
        "<tr><td>ZSP_TEMPORARY_PRIVILEGE</td><td><a href='/ui/entitlement/IGA-ENT-ZSP-SESSION-ADMIN-TEMP'>Temporary Session Administrator</a> requires review.</td><td>Critical</td><td>Open</td></tr>",
        "<tr><td>LEAVER_GOVERNANCE</td><td>Terminated identity exists for leaver testing.</td><td>Medium</td><td>Monitor</td></tr>",
    ]
    body = table(["Policy", "Finding", "Severity", "Status"], rows)
    return HTMLResponse(page_shell("Policy Violations", body, "SOD, orphan, leaver, and privileged access findings linked to affected objects."))


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
            f"<td>{object_link(account['account_id'], f'/ui/account/{account['account_id']}')}</td>"
            f"<td>{object_link(application['application_name'], f'/ui/application/{application['application_id']}')}</td>"
            f"<td>{account['lan_id']}</td>"
            f"<td>{account['email']}</td>"
            f"<td>{correlation['reason']}</td>"
            "</tr>"
        )
    return HTMLResponse(page_shell("Orphan Accounts", table(["Account", "Source", "Login", "Email", "Reason"], rows), "Orphan account findings linked to account and source objects."))


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
            f"<td>{object_link(account['lan_id'], f'/ui/account/{account['account_id']}')}</td>"
            f"<td>{object_link(application['application_name'], f'/ui/application/{application['application_id']}')}</td>"
            f"<td>{object_link(entitlement['entitlement_name'], f'/ui/entitlement/{entitlement['entitlement_id']}')}</td>"
            f"<td>{badge(risk, 'risk-' + risk)}</td>"
            f"<td>{badge(assignment['assignment_status'], 'status-' + assignment['assignment_status'])}</td>"
            f"<td>{assignment['assigned_by']}</td>"
            "</tr>"
        )
    return HTMLResponse(page_shell("High-Risk Access", table(["Account", "Source", "Entitlement", "Risk", "Assignment", "Granted By"], rows), "Critical and high-risk access linked to affected account, source, and entitlement objects."))
