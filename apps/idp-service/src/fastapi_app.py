from __future__ import annotations

from html import escape

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from auth import ACCESS_TOKENS, AUTHORIZATION_CODES, IDP_USERS, REGISTERED_CLIENTS
from auth_routes import router as auth_router
from management_routes import router as management_router
from repository import (
    get_app_assignments,
    get_app_registrations,
    get_dashboard,
    get_group_memberships,
    get_groups,
    get_identities,
    get_identity_profile,
    get_machine_identities,
)
from ui_components import badge, render_page, table

app = FastAPI(
    title="Luffy IdP Service",
    description="Enterprise-style local IdP app with identity registry, OAuth-like login, clients, tokens, and UI.",
    version="0.3.0",
)
app.include_router(auth_router)
app.include_router(management_router)


def object_link(label: object, href: str) -> str:
    return f'<a href="{escape(href)}">{escape(str(label))}</a>'


def metric_card(label: str, value: object, hint: str = "") -> str:
    hint_html = f'<div class="muted">{escape(hint)}</div>' if hint else ""
    return f'<div class="metric-card"><div class="metric-label">{escape(label)}</div><div class="metric">{escape(str(value))}</div>{hint_html}</div>'


def sign_in_log_rows() -> list[dict[str, object]]:
    return [
        {"time": "2026-04-25T20:01:00Z", "user": "admin", "app": "Luffy IGA Service", "result": "success", "method": "password + auth code", "risk": "LOW"},
        {"time": "2026-04-25T20:06:00Z", "user": "reviewer", "app": "Secure Operations Portal", "result": "success", "method": "password + auth code", "risk": "LOW"},
        {"time": "2026-04-25T20:11:00Z", "user": "reader", "app": "Secure Operations Portal", "result": "success", "method": "password + auth code", "risk": "LOW"},
        {"time": "2026-04-25T20:19:00Z", "user": "unknown", "app": "Luffy IGA Service", "result": "failure", "method": "invalid password", "risk": "MEDIUM"},
    ]


def audit_log_rows() -> list[dict[str, object]]:
    return [
        {"time": "2026-04-25T19:55:00Z", "actor": "system", "activity": "Registered relying-party client", "target": "luffy-iga"},
        {"time": "2026-04-25T19:57:00Z", "actor": "system", "activity": "Registered relying-party client", "target": "luffy-zsp"},
        {"time": "2026-04-25T20:00:00Z", "actor": "admin", "activity": "Issued authorization code", "target": "Luffy IGA Service"},
        {"time": "2026-04-25T20:05:00Z", "actor": "reviewer", "activity": "Issued access token", "target": "Secure Operations Portal"},
    ]


def search_records(query: str) -> list[dict[str, str]]:
    q = query.lower().strip()
    results: list[dict[str, str]] = []
    if not q:
        return results

    for identity in get_identities():
        haystack = " ".join(str(value) for value in identity.values()).lower()
        if q in haystack:
            identity_id = str(identity["identity_id"])
            results.append({"type": "User", "name": str(identity["display_name"]), "id": identity_id, "href": f"/ui/identity/{identity_id}"})

    for group in get_groups():
        haystack = " ".join(str(value) for value in group.values()).lower()
        if q in haystack:
            results.append({"type": "Group", "name": str(group["group_name"]), "id": str(group["group_id"]), "href": "/ui/groups"})

    for app_registration in get_app_registrations():
        haystack = " ".join(str(value) for value in app_registration.values()).lower()
        if q in haystack:
            results.append({"type": "Application", "name": str(app_registration["app_name"]), "id": str(app_registration["app_id"]), "href": "/ui/app-registrations"})

    for machine in get_machine_identities():
        haystack = " ".join(str(value) for value in machine.values()).lower()
        if q in haystack:
            results.append({"type": "Machine Identity", "name": str(machine["name"]), "id": str(machine["machine_identity_id"]), "href": "/ui/machine-identities"})

    for client_id, client in REGISTERED_CLIENTS.items():
        haystack = f"{client_id} {' '.join(str(value) for value in client.values())}".lower()
        if q in haystack:
            results.append({"type": "OAuth Client", "name": str(client["client_name"]), "id": client_id, "href": "/ui/oauth-clients"})

    return results


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "idp-service"}


@app.get("/dashboard")
def dashboard() -> dict[str, object]:
    return get_dashboard()


@app.get("/identities")
def identities() -> list[dict[str, object]]:
    return get_identities()


@app.get("/groups")
def groups() -> list[dict[str, object]]:
    return get_groups()


@app.get("/group-memberships")
def group_memberships() -> list[dict[str, object]]:
    return get_group_memberships()


@app.get("/app-registrations")
def app_registrations() -> list[dict[str, object]]:
    return get_app_registrations()


@app.get("/app-assignments")
def app_assignments() -> list[dict[str, object]]:
    return get_app_assignments()


@app.get("/machine-identities")
def machine_identities() -> list[dict[str, object]]:
    return get_machine_identities()


@app.get("/identity/{identity_id}/profile")
def identity_profile(identity_id: str) -> dict[str, object]:
    profile = get_identity_profile(identity_id)
    if profile is None:
        raise HTTPException(status_code=404, detail={"error": "identity_not_found", "identity_id": identity_id})
    return profile


@app.get("/ui", response_class=HTMLResponse)
def ui_dashboard() -> HTMLResponse:
    data = get_dashboard()
    cards = "".join(metric_card(key.replace("_", " ").title(), value) for key, value in data.items())
    auth_cards = "".join(
        [
            metric_card("Registered OAuth Clients", len(REGISTERED_CLIENTS), "Relying-party clients"),
            metric_card("Demo Login Users", len(IDP_USERS), "Users that can sign in"),
            metric_card("Active Auth Codes", len(AUTHORIZATION_CODES), "Short-lived authorization grants"),
            metric_card("Active Tokens", len(ACCESS_TOKENS), "Issued access tokens"),
        ]
    )
    return render_page("Luffy IdP Dashboard", f'<section class="grid">{cards}{auth_cards}</section>', "Entra-style tenant overview with directory, applications, sessions, and logs.")


@app.get("/ui/search", response_class=HTMLResponse)
def ui_search(q: str = Query(default="")) -> HTMLResponse:
    results = search_records(q)
    rows = [
        f"<tr><td>{badge(item['type'])}</td><td>{object_link(item['name'], item['href'])}</td><td>{escape(item['id'])}</td></tr>"
        for item in results
    ]
    body = table(["Type", "Name", "Object ID"], rows or ["<tr><td colspan='3'>Enter a search term to find users, groups, apps, clients, or machines.</td></tr>"])
    return render_page("Global Search", body, f"Search results for: {q}" if q else "Search identity provider objects.")


@app.get("/ui/status", response_class=HTMLResponse)
def ui_status() -> HTMLResponse:
    rows = [
        "<tr><td>Issuer</td><td>http://127.0.0.1:8002</td></tr>",
        "<tr><td>Status</td><td><span class='badge status-operational'>operational</span></td></tr>",
        "<tr><td>Supported Flow</td><td>authorization_code_demo</td></tr>",
        "<tr><td>Token Format</td><td>opaque_demo_token</td></tr>",
        f"<tr><td>Registered Clients</td><td>{len(REGISTERED_CLIENTS)}</td></tr>",
        f"<tr><td>Demo Users</td><td>{len(IDP_USERS)}</td></tr>",
        f"<tr><td>Active Auth Codes</td><td>{len(AUTHORIZATION_CODES)}</td></tr>",
        f"<tr><td>Active Tokens</td><td>{len(ACCESS_TOKENS)}</td></tr>",
    ]
    return render_page("Tenant Status", table(["Control", "Value"], rows), "Current health, tokens, sessions, and OAuth posture.")


@app.get("/ui/identities", response_class=HTMLResponse)
def ui_identities() -> HTMLResponse:
    rows: list[str] = []
    for identity in get_identities():
        identity_id = str(identity["identity_id"])
        href = f"/ui/identity/{identity_id}"
        rows.append(
            "<tr>"
            f"<td>{object_link(identity_id, href)}</td>"
            f"<td>{object_link(identity['display_name'], href)}</td>"
            f"<td>{escape(str(identity['lan_id']))}</td>"
            f"<td>{escape(str(identity['email']))}</td>"
            f"<td>{badge(identity['identity_status'])}</td>"
            "</tr>"
        )
    return render_page("Users", table(["ID", "Name", "LAN ID", "Email", "Status"], rows), "Directory users with profile drill-down.")


@app.get("/ui/identity/{identity_id}", response_class=HTMLResponse)
def ui_identity_detail(identity_id: str) -> HTMLResponse:
    profile = get_identity_profile(identity_id)
    if profile is None:
        return render_page("User Not Found", f"<div class='card'>No user found for {escape(identity_id)}</div>")

    identity = profile["identity"]
    group_rows = [
        f"<tr><td>{escape(str(group['group_id']))}</td><td>{escape(str(group['group_name']))}</td><td>{badge(group['risk_level'], 'risk-' + group['risk_level'])}</td></tr>"
        for group in profile["groups"]
    ]
    app_rows = [
        f"<tr><td>{escape(str(item['app_registration']['app_name']))}</td><td>{escape(str(item['app_registration']['auth_protocol']))}</td><td>{escape(str(item['assignment']['assignment_type']))}</td></tr>"
        for item in profile["login_applications"]
    ]
    body = "".join(
        [
            f"<div class='card'><h2 style='margin-top:0'>{escape(str(identity['display_name']))}</h2><p class='muted'>{escape(str(identity['email']))} · {escape(str(identity['lan_id']))} · {badge(identity['identity_status'])}</p><p><a class='button' href='/login'>Test login as demo user</a></p></div>",
            "<h2 class='section-title'>Group Memberships</h2>",
            table(["Group ID", "Group", "Risk"], group_rows or ["<tr><td colspan='3'>No groups.</td></tr>"]),
            "<h2 class='section-title'>Enterprise App Access</h2>",
            table(["Application", "Protocol", "Assignment"], app_rows or ["<tr><td colspan='3'>No app access.</td></tr>"]),
        ]
    )
    return render_page(f"User: {identity['display_name']}", body, "User profile with groups and enterprise app access.")


@app.get("/ui/groups", response_class=HTMLResponse)
def ui_groups() -> HTMLResponse:
    memberships = get_group_memberships()
    rows = []
    for group in get_groups():
        count = len([membership for membership in memberships if membership["group_id"] == group["group_id"]])
        rows.append(
            f"<tr><td>{escape(str(group['group_id']))}</td><td>{escape(str(group['group_name']))}</td><td>{escape(str(group['group_type']))}</td><td>{badge(group['risk_level'], 'risk-' + group['risk_level'])}</td><td>{count}</td><td>{escape(str(group['status']))}</td></tr>"
        )
    return render_page("Groups", table(["ID", "Name", "Type", "Risk", "Members", "Status"], rows), "Groups used for app access, role claims, and authorization.")


@app.get("/ui/enterprise-applications", response_class=HTMLResponse)
def ui_enterprise_applications() -> HTMLResponse:
    assignments = get_app_assignments()
    rows = []
    for app_registration in get_app_registrations():
        assignment_count = len([assignment for assignment in assignments if assignment["app_registration_id"] == app_registration["app_registration_id"]])
        sso_label = "SSO" if app_registration["sso_enabled"] else "NO SSO"
        rows.append(
            f"<tr><td>{escape(str(app_registration['app_id']))}</td><td>{escape(str(app_registration['app_name']))}</td><td>{escape(str(app_registration['auth_protocol']))}</td><td>{badge(sso_label)}</td><td>{assignment_count}</td><td>{escape(str(app_registration['status']))}</td></tr>"
        )
    return render_page("Enterprise Applications", table(["App ID", "Name", "Protocol", "SSO", "Assignments", "Status"], rows), "Applications assigned to users/groups for SSO.")


@app.get("/ui/app-registrations", response_class=HTMLResponse)
def ui_app_registrations() -> HTMLResponse:
    rows = [
        f"<tr><td>{escape(str(app_registration['app_id']))}</td><td>{escape(str(app_registration['app_name']))}</td><td>{escape(str(app_registration['auth_protocol']))}</td><td>{escape(str(app_registration['redirect_uri']))}</td><td>{escape(str(app_registration['status']))}</td></tr>"
        for app_registration in get_app_registrations()
    ]
    return render_page("App Registrations", table(["App ID", "Name", "Protocol", "Redirect URI", "Status"], rows), "OIDC/SAML app registrations and redirect URI posture.")


@app.get("/ui/oauth-clients", response_class=HTMLResponse)
def ui_oauth_clients() -> HTMLResponse:
    rows = [
        f"<tr><td>{escape(client_id)}</td><td>{escape(str(client['client_name']))}</td><td>{escape(str(client['redirect_uri']))}</td><td>{escape(', '.join(client['allowed_roles']))}</td></tr>"
        for client_id, client in REGISTERED_CLIENTS.items()
    ]
    return render_page("OAuth Clients", table(["Client ID", "Name", "Redirect URI", "Allowed Roles"], rows), "Registered relying-party clients used by IGA and ZSP.")


@app.get("/ui/machine-identities", response_class=HTMLResponse)
def ui_machine_identities() -> HTMLResponse:
    rows = [
        f"<tr><td>{escape(str(machine['machine_identity_id']))}</td><td>{escape(str(machine['name']))}</td><td>{escape(str(machine['type']))}</td><td>{escape(str(machine['owner']))}</td><td>{badge(machine['risk_level'], 'risk-' + machine['risk_level'])}</td><td>{escape(str(machine['rotation_status']))}</td></tr>"
        for machine in get_machine_identities()
    ]
    return render_page("Machine Identities", table(["ID", "Name", "Type", "Owner", "Risk", "Rotation"], rows), "Non-human identities, rotation status, and ownership.")


@app.get("/ui/sign-in-logs", response_class=HTMLResponse)
def ui_sign_in_logs() -> HTMLResponse:
    rows = [
        f"<tr><td>{escape(str(log['time']))}</td><td>{escape(str(log['user']))}</td><td>{escape(str(log['app']))}</td><td>{badge(log['result'], 'status-' + log['result'])}</td><td>{escape(str(log['method']))}</td><td>{badge(log['risk'], 'risk-' + log['risk'])}</td></tr>"
        for log in sign_in_log_rows()
    ]
    return render_page("Sign-in Logs", table(["Time", "User", "Application", "Result", "Method", "Risk"], rows), "Login/logout and authentication event visibility.")


@app.get("/ui/audit-logs", response_class=HTMLResponse)
def ui_audit_logs() -> HTMLResponse:
    rows = [
        f"<tr><td>{escape(str(log['time']))}</td><td>{escape(str(log['actor']))}</td><td>{escape(str(log['activity']))}</td><td>{escape(str(log['target']))}</td></tr>"
        for log in audit_log_rows()
    ]
    return render_page("Audit Logs", table(["Time", "Actor", "Activity", "Target"], rows), "Directory and application registration changes.")


@app.get("/ui/conditional-access", response_class=HTMLResponse)
def ui_conditional_access() -> HTMLResponse:
    rows = [
        "<tr><td>Require MFA for Admin Roles</td><td>Users with IGA_ADMIN claim</td><td>Report-only</td><td>High impact</td></tr>",
        "<tr><td>Block Unknown Client Redirects</td><td>OAuth clients</td><td>Enabled</td><td>Critical</td></tr>",
        "<tr><td>Review Machine Identity Rotation</td><td>NHI with overdue rotation</td><td>Enabled</td><td>High</td></tr>",
    ]
    return render_page("Conditional Access", table(["Policy", "Scope", "Mode", "Impact"], rows), "Policy-style controls for login, OAuth clients, and machine identities.")
