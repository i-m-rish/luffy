from __future__ import annotations

from html import escape

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from auth import require_ui_permission
from services.governance_service import governance_service
from ui.components import action_tile, badge, callout, metric_card, page_shell, table

router = APIRouter(tags=["IGA UI"])


def object_link(label: object, href: str) -> str:
    return f"<a href='{escape(href)}'>{escape(str(label))}</a>"


def pill_list(items: list[object]) -> str:
    if not items:
        return "<span class='muted'>None defined</span>"
    return " ".join(f"<span class='badge'>{escape(str(item))}</span>" for item in items)


def detail_card(title: str, rows: list[tuple[str, object]]) -> str:
    row_html = "".join(f"<tr><th>{escape(label)}</th><td>{value}</td></tr>" for label, value in rows)
    return f"<div class='card'><h2 style='margin-top:0'>{escape(title)}</h2><table style='min-width:0'>{row_html}</table></div>"


def integration_card(integration: dict[str, object] | None) -> str:
    if not integration:
        return detail_card("Integration Method", [("Status", "No integration metadata has been captured for this source yet.")])

    return detail_card(
        "Integration Method",
        [
            ("Market Pattern", escape(str(integration.get("market_pattern", "-")))),
            ("Connector Type", escape(str(integration.get("connector_type", "-")))),
            ("Authentication", escape(str(integration.get("authentication_method", "-")))),
            ("Aggregation", escape(str(integration.get("aggregation_method", "-")))),
            ("Provisioning", escape(str(integration.get("provisioning_method", "-")))),
            ("Correlation Rule", escape(str(integration.get("correlation_rule", "-")))),
            ("Supported Operations", pill_list(list(integration.get("supported_operations", [])))),
            ("Account Schema", pill_list(list(integration.get("account_schema", [])))),
            ("Entitlement Schema", pill_list(list(integration.get("entitlement_schema", [])))),
            ("Standard Controls", pill_list(list(integration.get("standard_controls", [])))),
        ],
    )


def render_application_summary_table() -> str:
    rows: list[str] = []
    for application in governance_service.application_access_summary():
        risk = str(application["risk_level"])
        app_id = str(application["application_id"])
        app_href = f"/ui/application/{app_id}"
        rows.append(
            "<tr>"
            f"<td>{object_link(app_id, app_href)}</td>"
            f"<td>{object_link(application['application_name'], app_href)}</td>"
            f"<td>{escape(str(application['integration_pattern']))}</td>"
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
            action_tile("Sources", "Open source records with integration method, schema, and operations.", "/ui/applications"),
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
    return HTMLResponse(page_shell("Luffy Identity Security Console", body, "SailPoint-style governance cockpit with object drill-down and source integration intelligence."))


@router.get("/ui/applications", response_class=HTMLResponse, response_model=None)
def ui_applications(request: Request) -> Response:
    redirect = enforce_ui(request, "VIEW_APPLICATIONS")
    if redirect:
        return redirect
    return HTMLResponse(page_shell("Sources", render_application_summary_table(), "Open any source to view attached accounts, entitlements, integration method, schemas, and supported operations."))


@router.get("/ui/application/{application_id}", response_class=HTMLResponse, response_model=None)
def ui_application_detail(request: Request, application_id: str) -> Response:
    redirect = enforce_ui(request, "VIEW_APPLICATIONS")
    if redirect:
        return redirect
    detail = governance_service.application_detail(application_id)
    if detail is None:
        return HTMLResponse(page_shell("Source Not Found", f"<div class='card'>No source found for {escape(application_id)}</div>"), status_code=404)

    app = detail["application"]
    integration = detail.get("integration")
    account_rows: list[str] = []
    for view in detail["accounts"]:
        account = view["account"]
        identity = view["identity"]
        correlation = view["correlation"]
        account_id = str(account["account_id"])
        identity_cell = "-"
        if identity:
            identity_id = str(identity["identity_id"])
            identity_cell = object_link(identity["display_name"], f"/ui/identity/{identity_id}/access")
        account_rows.append(
            "<tr>"
            f"<td>{object_link(account_id, f'/ui/account/{account_id}')}</td>"
            f"<td>{escape(str(account['lan_id']))}</td>"
            f"<td>{escape(str(account['email']))}</td>"
            f"<td>{identity_cell}</td>"
            f"<td>{badge(account['correlation_status'], 'status-' + account['correlation_status'])}</td>"
            f"<td>{escape(str(correlation['reason'])) if correlation else '-'}</td>"
            "</tr>"
        )

    entitlement_rows: list[str] = []
    for view in detail["entitlements"]:
        entitlement = view["entitlement"]
        entitlement_id = str(entitlement["entitlement_id"])
        risk = str(entitlement["risk_level"])
        entitlement_rows.append(
            "<tr>"
            f"<td>{object_link(entitlement['entitlement_name'], f'/ui/entitlement/{entitlement_id}')}</td>"
            f"<td>{escape(str(entitlement['native_entitlement_id']))}</td>"
            f"<td>{badge(risk, 'risk-' + risk)}</td>"
            f"<td>{view['assignment_count']}</td>"
            f"<td>{escape(str(entitlement['entitlement_description']))}</td>"
            "</tr>"
        )

    body = "".join([
        detail_card("Source Overview", [
            ("Source ID", escape(str(app["application_id"]))),
            ("Name", escape(str(app["application_name"]))),
            ("Type", escape(str(app["application_type"]))),
            ("Integration Pattern", escape(str(app["integration_pattern"]))),
            ("Risk", badge(app["risk_level"], "risk-" + app["risk_level"])),
            ("Owner", escape(str(app["owner"]))),
            ("Status", badge(app["status"], "status-" + app["status"])),
        ]),
        integration_card(integration),
        "<h2 class='section-title'>Attached Accounts</h2>",
        table(["Account", "Login", "Email", "Identity", "Correlation", "Reason"], account_rows or ["<tr><td colspan='6'>No accounts attached.</td></tr>"]),
        "<h2 class='section-title'>Entitlements</h2>",
        table(["Entitlement", "Native ID", "Risk", "Assignments", "Description"], entitlement_rows or ["<tr><td colspan='5'>No entitlements attached.</td></tr>"]),
    ])
    return HTMLResponse(page_shell(f"Source: {app['application_name']}", body, "Source object view with integration method, account schema, entitlement schema, controls, accounts, and entitlements."))


@router.get("/ui/identities", response_class=HTMLResponse, response_model=None)
def ui_identities(request: Request) -> Response:
    redirect = enforce_ui(request, "VIEW_IDENTITIES")
    if redirect:
        return redirect
    rows: list[str] = []
    for identity in governance_service.identity_access_summary():
        status = str(identity["identity_status"])
        identity_id = str(identity["identity_id"])
        href = f"/ui/identity/{identity_id}/access"
        rows.append(
            "<tr>"
            f"<td>{object_link(identity_id, href)}</td>"
            f"<td>{object_link(identity['display_name'], href)}</td>"
            f"<td>{escape(str(identity['employee_id']))}</td>"
            f"<td>{escape(str(identity['lan_id']))}</td>"
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
        return HTMLResponse(page_shell("Identity Not Found", f"<div class='card'>No identity found for {escape(identity_id)}</div>"), status_code=404)

    identity = access["identity"]
    rows: list[str] = []
    for account_view in access["accounts"]:
        account = account_view["account"]
        application = account_view["application"]
        application_id = str(application["application_id"])
        account_id = str(account["account_id"])
        for assignment_view in account_view["assignments"]:
            entitlement = assignment_view["entitlement"]
            assignment = assignment_view["assignment"]
            entitlement_id = str(entitlement["entitlement_id"])
            risk = str(entitlement["risk_level"])
            rows.append(
                "<tr>"
                f"<td>{object_link(application['application_name'], f'/ui/application/{application_id}')}</td>"
                f"<td>{object_link(account['lan_id'], f'/ui/account/{account_id}')}</td>"
                f"<td>{object_link(entitlement['entitlement_name'], f'/ui/entitlement/{entitlement_id}')}</td>"
                f"<td>{badge(risk, 'risk-' + risk)}</td>"
                f"<td>{badge(assignment['assignment_status'], 'status-' + assignment['assignment_status'])}</td>"
                f"<td>{escape(str(assignment['assigned_by']))}</td>"
                f"<td>{escape(str(assignment['assigned_at']))}</td>"
                "</tr>"
            )
    body = f"""
      {detail_card('Identity Overview', [
        ('Identity ID', escape(str(identity['identity_id']))),
        ('Name', escape(str(identity['display_name']))),
        ('Employee ID', escape(str(identity['employee_id']))),
        ('Login', escape(str(identity['lan_id']))),
        ('Email', escape(str(identity['email']))),
        ('Lifecycle', badge(identity['identity_status'], 'status-' + identity['identity_status'])),
        ('Source System', escape(str(identity['source_system']))),
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
    rows: list[str] = []
    for account in governance_service.accounts():
        account_status = str(account["account_status"])
        correlation_status = str(account["correlation_status"])
        account_id = str(account["account_id"])
        app_id = str(account["application_id"])
        rows.append(
            "<tr>"
            f"<td>{object_link(account_id, f'/ui/account/{account_id}')}</td>"
            f"<td>{object_link(app_id, f'/ui/application/{app_id}')}</td>"
            f"<td>{escape(str(account['lan_id']))}</td>"
            f"<td>{escape(str(account['email']))}</td>"
            f"<td>{badge(account_status, 'status-' + account_status)}</td>"
            f"<td>{badge(correlation_status, 'status-' + correlation_status)}</td>"
            "</tr>"
        )
    return HTMLResponse(page_shell("Accounts", table(["Account", "Source", "Login", "Email", "Status", "Correlation"], rows), "Open an account to view attached identity, source integration, and assigned entitlements."))


@router.get("/ui/account/{account_id}", response_class=HTMLResponse, response_model=None)
def ui_account_detail(request: Request, account_id: str) -> Response:
    redirect = enforce_ui(request, "VIEW_ACCOUNTS")
    if redirect:
        return redirect
    detail = governance_service.account_detail(account_id)
    if detail is None:
        return HTMLResponse(page_shell("Account Not Found", f"<div class='card'>No account found for {escape(account_id)}</div>"), status_code=404)

    account = detail["account"]
    application = detail["application"]
    identity = detail["identity"]
    correlation = detail["correlation"]
    integration = detail.get("integration")
    source_cell = escape(str(account["application_id"]))
    if application:
        source_app_id = str(application["application_id"])
        source_cell = object_link(application["application_name"], f"/ui/application/{source_app_id}")
    identity_cell = "-"
    if identity:
        identity_id = str(identity["identity_id"])
        identity_cell = object_link(identity["display_name"], f"/ui/identity/{identity_id}/access")
    assignment_rows: list[str] = []
    for view in detail["assignments"]:
        assignment = view["assignment"]
        entitlement = view["entitlement"]
        entitlement_id = str(entitlement["entitlement_id"])
        risk = str(entitlement["risk_level"])
        assignment_rows.append(
            "<tr>"
            f"<td>{object_link(entitlement['entitlement_name'], f'/ui/entitlement/{entitlement_id}')}</td>"
            f"<td>{badge(risk, 'risk-' + risk)}</td>"
            f"<td>{badge(assignment['assignment_status'], 'status-' + assignment['assignment_status'])}</td>"
            f"<td>{escape(str(assignment['assigned_by']))}</td>"
            f"<td>{escape(str(assignment['assigned_at']))}</td>"
            "</tr>"
        )
    body = "".join([
        detail_card("Account Overview", [
            ("Account ID", escape(str(account["account_id"]))),
            ("Native Account", escape(str(account["native_account_id"]))),
            ("Source", source_cell),
            ("Login", escape(str(account["lan_id"]))),
            ("Email", escape(str(account["email"]))),
            ("Status", badge(account["account_status"], "status-" + account["account_status"])),
            ("Correlation", badge(account["correlation_status"], "status-" + account["correlation_status"])),
            ("Identity", identity_cell),
            ("Correlation Reason", escape(str(correlation["reason"])) if correlation else "-"),
        ]),
        integration_card(integration),
        "<h2 class='section-title'>Assigned Entitlements</h2>",
        table(["Entitlement", "Risk", "Assignment", "Granted By", "Granted At"], assignment_rows or ["<tr><td colspan='5'>No assigned entitlements.</td></tr>"]),
    ])
    return HTMLResponse(page_shell(f"Account: {account['lan_id']}", body, "Account object view connected to identity, source integration, and entitlements."))


@router.get("/ui/entitlements", response_class=HTMLResponse, response_model=None)
def ui_entitlements(request: Request) -> Response:
    redirect = enforce_ui(request, "VIEW_ENTITLEMENTS")
    if redirect:
        return redirect
    rows: list[str] = []
    for entitlement in governance_service.entitlements():
        risk = str(entitlement["risk_level"])
        entitlement_id = str(entitlement["entitlement_id"])
        app_id = str(entitlement["application_id"])
        rows.append(
            "<tr>"
            f"<td>{object_link(entitlement_id, f'/ui/entitlement/{entitlement_id}')}</td>"
            f"<td>{object_link(app_id, f'/ui/application/{app_id}')}</td>"
            f"<td>{object_link(entitlement['entitlement_name'], f'/ui/entitlement/{entitlement_id}')}</td>"
            f"<td>{escape(str(entitlement['entitlement_description']))}</td>"
            f"<td>{badge(risk, 'risk-' + risk)}</td>"
            "</tr>"
        )
    return HTMLResponse(page_shell("Entitlement Catalog", table(["Entitlement", "Source", "Display Name", "Description", "Risk"], rows), "Open an entitlement to view assigned accounts, identities, source schema, and integration method."))


@router.get("/ui/entitlement/{entitlement_id}", response_class=HTMLResponse, response_model=None)
def ui_entitlement_detail(request: Request, entitlement_id: str) -> Response:
    redirect = enforce_ui(request, "VIEW_ENTITLEMENTS")
    if redirect:
        return redirect
    detail = governance_service.entitlement_detail(entitlement_id)
    if detail is None:
        return HTMLResponse(page_shell("Entitlement Not Found", f"<div class='card'>No entitlement found for {escape(entitlement_id)}</div>"), status_code=404)

    entitlement = detail["entitlement"]
    application = detail["application"]
    integration = detail.get("integration")
    risk = str(entitlement["risk_level"])
    source_cell = escape(str(entitlement["application_id"]))
    if application:
        app_id = str(application["application_id"])
        source_cell = object_link(application["application_name"], f"/ui/application/{app_id}")
    assignment_rows: list[str] = []
    for view in detail["assignments"]:
        assignment = view["assignment"]
        account = view["account"]
        identity = view["identity"]
        account_cell = "-"
        if account:
            linked_account_id = str(account["account_id"])
            account_cell = object_link(account["lan_id"], f"/ui/account/{linked_account_id}")
        identity_cell = "-"
        if identity:
            linked_identity_id = str(identity["identity_id"])
            identity_cell = object_link(identity["display_name"], f"/ui/identity/{linked_identity_id}/access")
        assignment_rows.append(
            "<tr>"
            f"<td>{account_cell}</td>"
            f"<td>{identity_cell}</td>"
            f"<td>{badge(assignment['assignment_status'], 'status-' + assignment['assignment_status'])}</td>"
            f"<td>{escape(str(assignment['assigned_by']))}</td>"
            f"<td>{escape(str(assignment['assigned_at']))}</td>"
            "</tr>"
        )
    body = "".join([
        detail_card("Entitlement Overview", [
            ("Entitlement ID", escape(str(entitlement["entitlement_id"]))),
            ("Name", escape(str(entitlement["entitlement_name"]))),
            ("Native ID", escape(str(entitlement["native_entitlement_id"]))),
            ("Source", source_cell),
            ("Risk", badge(risk, "risk-" + risk)),
            ("Status", badge(entitlement["status"], "status-" + entitlement["status"])),
            ("Description", escape(str(entitlement["entitlement_description"]))),
        ]),
        integration_card(integration),
        "<h2 class='section-title'>Assigned Accounts</h2>",
        table(["Account", "Identity", "Assignment", "Granted By", "Granted At"], assignment_rows or ["<tr><td colspan='5'>No assignments found.</td></tr>"]),
    ])
    return HTMLResponse(page_shell(f"Entitlement: {entitlement['entitlement_name']}", body, "Entitlement object view connected to accounts, identities, source schema, and integration method."))


@router.get("/ui/correlation-results", response_class=HTMLResponse, response_model=None)
def ui_correlation_results(request: Request) -> Response:
    redirect = enforce_ui(request, "VIEW_CORRELATION")
    if redirect:
        return redirect
    rows: list[str] = []
    for result in governance_service.correlation_results():
        status = str(result["result"])
        account_id = str(result["account_id"])
        identity_id = result["identity_id"]
        identity_cell = object_link(identity_id, f"/ui/identity/{identity_id}/access") if identity_id else "-"
        rows.append(
            "<tr>"
            f"<td>{escape(str(result['correlation_id']))}</td>"
            f"<td>{object_link(account_id, f'/ui/account/{account_id}')}</td>"
            f"<td>{identity_cell}</td>"
            f"<td>{badge(status, 'status-' + status)}</td>"
            f"<td>{escape(str(result['match_attribute']))}</td>"
            f"<td>{escape(str(result['confidence']))}</td>"
            f"<td>{escape(str(result['reason']))}</td>"
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
    rows: list[str] = []
    for item in governance_service.orphan_accounts():
        account = item["account"]
        application = item["application"]
        correlation = item["correlation_result"]
        account_id = str(account["account_id"])
        app_id = str(application["application_id"])
        rows.append(
            "<tr>"
            f"<td>{object_link(account_id, f'/ui/account/{account_id}')}</td>"
            f"<td>{object_link(application['application_name'], f'/ui/application/{app_id}')}</td>"
            f"<td>{escape(str(account['lan_id']))}</td>"
            f"<td>{escape(str(account['email']))}</td>"
            f"<td>{escape(str(correlation['reason']))}</td>"
            "</tr>"
        )
    return HTMLResponse(page_shell("Orphan Accounts", table(["Account", "Source", "Login", "Email", "Reason"], rows), "Orphan account findings linked to account and source objects."))


@router.get("/ui/high-risk-access", response_class=HTMLResponse, response_model=None)
def ui_high_risk_access(request: Request) -> Response:
    redirect = enforce_ui(request, "VIEW_HIGH_RISK")
    if redirect:
        return redirect
    rows: list[str] = []
    for item in governance_service.high_risk_access():
        account = item["account"]
        application = item["application"]
        entitlement = item["entitlement"]
        assignment = item["assignment"]
        account_id = str(account["account_id"])
        application_id = str(application["application_id"])
        entitlement_id = str(entitlement["entitlement_id"])
        risk = str(entitlement["risk_level"])
        rows.append(
            "<tr>"
            f"<td>{object_link(account['lan_id'], f'/ui/account/{account_id}')}</td>"
            f"<td>{object_link(application['application_name'], f'/ui/application/{application_id}')}</td>"
            f"<td>{object_link(entitlement['entitlement_name'], f'/ui/entitlement/{entitlement_id}')}</td>"
            f"<td>{badge(risk, 'risk-' + risk)}</td>"
            f"<td>{badge(assignment['assignment_status'], 'status-' + assignment['assignment_status'])}</td>"
            f"<td>{escape(str(assignment['assigned_by']))}</td>"
            "</tr>"
        )
    return HTMLResponse(page_shell("High-Risk Access", table(["Account", "Source", "Entitlement", "Risk", "Assignment", "Granted By"], rows), "Critical and high-risk access linked to affected account, source, and entitlement objects."))
