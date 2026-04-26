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

app = FastAPI(
    title="Luffy IdP Service",
    description="Enterprise-style local IdP app with identity registry, OAuth-like login, clients, tokens, and UI.",
    version="0.3.0",
)
app.include_router(auth_router)
app.include_router(management_router)


def badge(text: object, css_class: str = "") -> str:
    return f'<span class="badge {css_class}">{escape(str(text))}</span>'


def object_link(label: object, href: str) -> str:
    return f'<a href="{escape(href)}">{escape(str(label))}</a>'


def metric_card(label: str, value: object, hint: str = "") -> str:
    hint_html = f'<div class="muted">{escape(hint)}</div>' if hint else ""
    return f'<div class="metric-card"><div class="metric-label">{escape(label)}</div><div class="metric">{escape(str(value))}</div>{hint_html}</div>'


def table(headers: list[str], rows: list[str]) -> str:
    header_html = "".join(f"<th>{escape(header)}</th>" for header in headers)
    return f'<div class="table-wrap"><table><tr>{header_html}</tr>{"".join(rows)}</table></div>'


def render_page(title: str, body: str, subtitle: str = "") -> HTMLResponse:
    subtitle_html = f"<p class='subtitle'>{escape(subtitle)}</p>" if subtitle else ""
    html = f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{escape(title)}</title>
        <style>
          :root {{ --bg:#f3f6fb; --panel:#fff; --ink:#0f172a; --muted:#64748b; --line:#dbe3ef; --nav:#111827; --accent:#2563eb; --accent2:#7c3aed; --shadow:0 16px 38px rgba(15,23,42,.10); }}
          * {{ box-sizing:border-box; }}
          body {{ font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; margin:0; background:var(--bg); color:var(--ink); }}
          .layout {{ min-height:100vh; display:grid; grid-template-columns:290px 1fr; }}
          aside {{ background:linear-gradient(180deg,#111827,#172554 70%,#312e81); color:white; padding:24px 18px; position:sticky; top:0; height:100vh; overflow:auto; }}
          .brand {{ display:flex; gap:12px; align-items:center; margin-bottom:22px; }}
          .brand-mark {{ width:42px; height:42px; border-radius:14px; display:grid; place-items:center; background:linear-gradient(135deg,#60a5fa,#a78bfa); font-weight:900; }}
          .brand small {{ display:block; color:#bfdbfe; }}
          .side-section {{ color:#93c5fd; font-size:11px; letter-spacing:.09em; text-transform:uppercase; font-weight:800; margin:20px 10px 8px; }}
          nav {{ display:flex; flex-direction:column; gap:5px; }}
          nav a {{ color:#dbeafe; text-decoration:none; padding:10px 12px; border-radius:11px; display:flex; justify-content:space-between; font-size:14px; }}
          nav a:hover {{ background:rgba(255,255,255,.10); color:white; }}
          .nav-pill {{ font-size:11px; color:#bfdbfe; }}
          header {{ padding:24px 34px; background:radial-gradient(circle at top left,#dbeafe 0,#ffffff 42%,#f8fafc 100%); border-bottom:1px solid var(--line); }}
          .topbar {{ display:flex; gap:14px; align-items:center; justify-content:space-between; }}
          .search-box {{ display:flex; gap:8px; flex:1; max-width:680px; }}
          .search-box input {{ width:100%; padding:11px 12px; border:1px solid #cbd5e1; border-radius:12px; background:white; }}
          .search-box button, .button, button {{ border:0; background:var(--accent); color:white; padding:10px 14px; border-radius:12px; font-weight:800; text-decoration:none; cursor:pointer; }}
          input, select, textarea {{ width:100%; padding:10px 12px; border:1px solid #cbd5e1; border-radius:12px; background:white; }}
          textarea {{ min-height:88px; }}
          label {{ font-weight:800; font-size:13px; color:#334155; }}
          .form-card {{ display:grid; gap:12px; max-width:760px; }}
          .session-card {{ background:white; border:1px solid var(--line); border-radius:14px; padding:9px 12px; font-size:13px; color:#334155; }}
          .eyebrow {{ color:#1d4ed8; letter-spacing:.12em; text-transform:uppercase; font-weight:900; font-size:12px; margin-top:20px; }}
          h1 {{ margin:8px 0 0; font-size:32px; }}
          .subtitle {{ color:#475569; margin:8px 0 0; max-width:950px; }}
          .status-strip {{ display:flex; flex-wrap:wrap; gap:10px; margin-top:16px; }}
          .status-chip {{ background:white; border:1px solid var(--line); border-radius:999px; padding:7px 11px; color:#334155; font-size:13px; }}
          main {{ padding:28px 34px 44px; }}
          .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:16px; }}
          .metric-card, .card {{ background:var(--panel); border:1px solid var(--line); border-radius:18px; padding:18px; box-shadow:var(--shadow); }}
          .metric-label {{ color:var(--muted); font-size:13px; font-weight:800; }}
          .metric {{ font-size:34px; font-weight:900; letter-spacing:-.03em; margin-top:6px; }}
          .section-title {{ margin:30px 0 12px; font-size:20px; }}
          .muted {{ color:var(--muted); font-size:13px; }}
          .table-wrap {{ border:1px solid var(--line); border-radius:18px; overflow:auto; background:white; box-shadow:var(--shadow); }}
          table {{ width:100%; border-collapse:collapse; min-width:820px; }}
          th,td {{ padding:13px 14px; border-bottom:1px solid var(--line); text-align:left; font-size:14px; vertical-align:top; }}
          th {{ background:#f8fafc; color:#475569; font-size:11px; text-transform:uppercase; letter-spacing:.06em; }}
          tr:hover td {{ background:#f8fafc; }}
          a {{ color:#1d4ed8; }}
          .badge {{ display:inline-block; padding:4px 9px; border-radius:999px; background:#e5e7eb; font-size:12px; font-weight:800; }}
          .risk-HIGH,.risk-CRITICAL,.status-failure {{ background:#fee2e2; color:#991b1b; }}
          .risk-MEDIUM,.status-VALIDATED_WITH_WARNINGS {{ background:#fef3c7; color:#92400e; }}
          .risk-LOW,.status-operational,.status-success,.status-VALIDATED,.status-PROMOTED_TO_ACTIVE {{ background:#dcfce7; color:#166534; }}
          @media(max-width:900px) {{ .layout {{ grid-template-columns:1fr; }} aside {{ position:relative; height:auto; }} nav {{ flex-direction:row; flex-wrap:wrap; }} .topbar {{ flex-direction:column; align-items:stretch; }} }}
        </style>
      </head>
      <body>
        <div class="layout">
          <aside>
            <div class="brand"><div class="brand-mark">IDP</div><div><strong>Luffy Identity Provider</strong><small>Entra-style directory</small></div></div>
            <nav>
              <div class="side-section">Overview</div>
              <a href="/ui">Dashboard <span class="nav-pill">Home</span></a>
              <a href="/ui/status">Tenant Status <span class="nav-pill">Health</span></a>
              <a href="/ui/search">Global Search <span class="nav-pill">Find</span></a>
              <a href="/ui/idp-management">Draft Management <span class="nav-pill">Sandbox</span></a>
              <div class="side-section">Identity</div>
              <a href="/ui/identities">Users <span class="nav-pill">People</span></a>
              <a href="/ui/groups">Groups <span class="nav-pill">RBAC</span></a>
              <a href="/ui/machine-identities">Machine Identities <span class="nav-pill">NHI</span></a>
              <div class="side-section">Applications</div>
              <a href="/ui/enterprise-applications">Enterprise Apps <span class="nav-pill">SSO</span></a>
              <a href="/ui/app-registrations">App Registrations <span class="nav-pill">OIDC</span></a>
              <a href="/ui/oauth-clients">OAuth Clients <span class="nav-pill">Clients</span></a>
              <div class="side-section">Monitoring</div>
              <a href="/ui/sign-in-logs">Sign-in Logs <span class="nav-pill">Login</span></a>
              <a href="/ui/audit-logs">Audit Logs <span class="nav-pill">Changes</span></a>
              <a href="/ui/conditional-access">Conditional Access <span class="nav-pill">Policy</span></a>
              <a href="/docs">API Docs <span class="nav-pill">OpenAPI</span></a>
            </nav>
          </aside>
          <section>
            <header>
              <div class="topbar">
                <form class="search-box" method="get" action="/ui/search">
                  <input name="q" placeholder="Search users, groups, apps, clients, machines..." />
                  <button type="submit">Search</button>
                </form>
                <div class="session-card">Demo tenant · <a href="/login">Login</a> · <a href="/oauth/status">OAuth status</a></div>
              </div>
              <div class="eyebrow">Identity provider control plane</div>
              <h1>{escape(title)}</h1>
              {subtitle_html}
              <div class="status-strip">
                <span class="status-chip">OIDC demo flow</span>
                <span class="status-chip">Enterprise app assignments</span>
                <span class="status-chip">OAuth clients</span>
                <span class="status-chip">Draft promotion</span>
              </div>
            </header>
            <main>{body}</main>
          </section>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(html)


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
            results.append({"type": "User", "name": str(identity["display_name"]), "id": str(identity["identity_id"]), "href": f"/ui/identity/{identity['identity_id']}"})
    for group in get_groups():
        haystack = " ".join(str(value) for value in group.values()).lower()
        if q in haystack:
            results.append({"type": "Group", "name": str(group["group_name"]), "id": str(group["group_id"]), "href": "/ui/groups"})
    for app_reg in get_app_registrations():
        haystack = " ".join(str(value) for value in app_reg.values()).lower()
        if q in haystack:
            results.append({"type": "Application", "name": str(app_reg["app_name"]), "id": str(app_reg["app_id"]), "href": "/ui/app-registrations"})
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
    auth_cards = "".join([
        metric_card("Registered OAuth Clients", len(REGISTERED_CLIENTS), "Relying-party clients"),
        metric_card("Demo Login Users", len(IDP_USERS), "Users that can sign in"),
        metric_card("Active Auth Codes", len(AUTHORIZATION_CODES), "Short-lived authorization grants"),
        metric_card("Active Tokens", len(ACCESS_TOKENS), "Issued access tokens"),
    ])
    return render_page("Luffy IdP Dashboard", f'<section class="grid">{cards}{auth_cards}</section>', "Entra-style tenant overview with directory, applications, sessions, and logs.")


@app.get("/ui/search", response_class=HTMLResponse)
def ui_search(q: str = Query(default="")) -> HTMLResponse:
    results = search_records(q)
    rows = [f"<tr><td>{badge(item['type'])}</td><td>{object_link(item['name'], item['href'])}</td><td>{escape(item['id'])}</td></tr>" for item in results]
    body = table(["Type", "Name", "Object ID"], rows or ["<tr><td colspan='3'>Enter a search term to find users, groups, apps, clients, or machines.</td></tr>"])
    return render_page("Global Search", body, f"Search results for: {q}" if q else "Search identity provider objects.")


@app.get("/ui/status", response_class=HTMLResponse)
def ui_status() -> HTMLResponse:
    rows = "".join([
        "<tr><td>Issuer</td><td>http://127.0.0.1:8002</td></tr>",
        "<tr><td>Status</td><td><span class='badge status-operational'>operational</span></td></tr>",
        "<tr><td>Supported Flow</td><td>authorization_code_demo</td></tr>",
        "<tr><td>Token Format</td><td>opaque_demo_token</td></tr>",
        f"<tr><td>Registered Clients</td><td>{len(REGISTERED_CLIENTS)}</td></tr>",
        f"<tr><td>Demo Users</td><td>{len(IDP_USERS)}</td></tr>",
        f"<tr><td>Active Auth Codes</td><td>{len(AUTHORIZATION_CODES)}</td></tr>",
        f"<tr><td>Active Tokens</td><td>{len(ACCESS_TOKENS)}</td></tr>",
    ])
    return render_page("Tenant Status", table(["Control", "Value"], [rows]), "Current health, tokens, sessions, and OAuth posture.")


@app.get("/ui/identities", response_class=HTMLResponse)
def ui_identities() -> HTMLResponse:
    rows = []
    for i in get_identities():
        identity_href = f"/ui/identity/{i['identity_id']}"
        rows.append(
            "<tr>"
            f"<td>{object_link(i['identity_id'], identity_href)}</td>"
            f"<td>{object_link(i['display_name'], identity_href)}</td>"
            f"<td>{escape(str(i['lan_id']))}</td>"
            f"<td>{escape(str(i['email']))}</td>"
            f"<td>{badge(i['identity_status'])}</td>"
            "</tr>"
        )
    return render_page("Users", table(["ID", "Name", "LAN ID", "Email", "Status"], rows), "Directory users with profile drill-down.")


@app.get("/ui/identity/{identity_id}", response_class=HTMLResponse)
def ui_identity_detail(identity_id: str) -> HTMLResponse:
    profile = get_identity_profile(identity_id)
    if profile is None:
        return render_page("User Not Found", f"<div class='card'>No user found for {escape(identity_id)}</div>")
    identity = profile["identity"]
    group_rows = [f"<tr><td>{escape(str(g['group_id']))}</td><td>{escape(str(g['group_name']))}</td><td>{badge(g['risk_level'], 'risk-' + g['risk_level'])}</td></tr>" for g in profile["groups"]]
    app_rows = [f"<tr><td>{escape(str(item['app_registration']['app_name']))}</td><td>{escape(str(item['app_registration']['auth_protocol']))}</td><td>{escape(str(item['assignment']['assignment_type']))}</td></tr>" for item in profile["login_applications"]]
    body = "".join([
        f"<div class='card'><h2 style='margin-top:0'>{escape(str(identity['display_name']))}</h2><p class='muted'>{escape(str(identity['email']))} · {escape(str(identity['lan_id']))} · {badge(identity['identity_status'])}</p><p><a class='button' href='/login'>Test login as demo user</a></p></div>",
        "<h2 class='section-title'>Group Memberships</h2>",
        table(["Group ID", "Group", "Risk"], group_rows or ["<tr><td colspan='3'>No groups.</td></tr>"]),
        "<h2 class='section-title'>Enterprise App Access</h2>",
        table(["Application", "Protocol", "Assignment"], app_rows or ["<tr><td colspan='3'>No app access.</td></tr>"]),
    ])
    return render_page(f"User: {identity['display_name']}", body, "User profile with groups and enterprise app access.")


@app.get("/ui/groups", response_class=HTMLResponse)
def ui_groups() -> HTMLResponse:
    memberships = get_group_memberships()
    rows = []
    for group in get_groups():
        count = len([membership for membership in memberships if membership["group_id"] == group["group_id"]])
        rows.append(f"<tr><td>{escape(str(group['group_id']))}</td><td>{escape(str(group['group_name']))}</td><td>{escape(str(group['group_type']))}</td><td>{badge(group['risk_level'], 'risk-' + group['risk_level'])}</td><td>{count}</td><td>{escape(str(group['status']))}</td></tr>")
    return render_page("Groups", table(["ID", "Name", "Type", "Risk", "Members", "Status"], rows), "Groups used for app access, role claims, and authorization.")


@app.get("/ui/enterprise-applications", response_class=HTMLResponse)
def ui_enterprise_applications() -> HTMLResponse:
    assignments = get_app_assignments()
    rows = []
    for app_registration in get_app_registrations():
        assignment_count = len([assignment for assignment in assignments if assignment["app_registration_id"] == app_registration["app_registration_id"]])
        rows.append(f"<tr><td>{escape(str(app_registration['app_id']))}</td><td>{escape(str(app_registration['app_name']))}</td><td>{escape(str(app_registration['auth_protocol']))}</td><td>{badge('SSO' if app_registration['sso_enabled'] else 'NO SSO')}</td><td>{assignment_count}</td><td>{escape(str(app_registration['status']))}</td></tr>")
    return render_page("Enterprise Applications", table(["App ID", "Name", "Protocol", "SSO", "Assignments", "Status"], rows), "Applications assigned to users/groups for SSO.")


@app.get("/ui/app-registrations", response_class=HTMLResponse)
def ui_app_registrations() -> HTMLResponse:
    rows = [f"<tr><td>{escape(str(a['app_id']))}</td><td>{escape(str(a['app_name']))}</td><td>{escape(str(a['auth_protocol']))}</td><td>{escape(str(a['redirect_uri']))}</td><td>{escape(str(a['status']))}</td></tr>" for a in get_app_registrations()]
    return render_page("App Registrations", table(["App ID", "Name", "Protocol", "Redirect URI", "Status"], rows), "OIDC/SAML app registrations and redirect URI posture.")


@app.get("/ui/oauth-clients", response_class=HTMLResponse)
def ui_oauth_clients() -> HTMLResponse:
    rows = [f"<tr><td>{escape(client_id)}</td><td>{escape(str(client['client_name']))}</td><td>{escape(str(client['redirect_uri']))}</td><td>{escape(', '.join(client['allowed_roles']))}</td></tr>" for client_id, client in REGISTERED_CLIENTS.items()]
    return render_page("OAuth Clients", table(["Client ID", "Name", "Redirect URI", "Allowed Roles"], rows), "Registered relying-party clients used by IGA and ZSP.")


@app.get("/ui/machine-identities", response_class=HTMLResponse)
def ui_machine_identities() -> HTMLResponse:
    rows = [f"<tr><td>{escape(str(m['machine_identity_id']))}</td><td>{escape(str(m['name']))}</td><td>{escape(str(m['type']))}</td><td>{escape(str(m['owner']))}</td><td>{badge(m['risk_level'], 'risk-' + m['risk_level'])}</td><td>{escape(str(m['rotation_status']))}</td></tr>" for m in get_machine_identities()]
    return render_page("Machine Identities", table(["ID", "Name", "Type", "Owner", "Risk", "Rotation"], rows), "Non-human identities, rotation status, and ownership.")


@app.get("/ui/sign-in-logs", response_class=HTMLResponse)
def ui_sign_in_logs() -> HTMLResponse:
    rows = [f"<tr><td>{escape(str(log['time']))}</td><td>{escape(str(log['user']))}</td><td>{escape(str(log['app']))}</td><td>{badge(log['result'], 'status-' + log['result'])}</td><td>{escape(str(log['method']))}</td><td>{badge(log['risk'], 'risk-' + log['risk'])}</td></tr>" for log in sign_in_log_rows()]
    return render_page("Sign-in Logs", table(["Time", "User", "Application", "Result", "Method", "Risk"], rows), "Login/logout and authentication event visibility.")


@app.get("/ui/audit-logs", response_class=HTMLResponse)
def ui_audit_logs() -> HTMLResponse:
    rows = [f"<tr><td>{escape(str(log['time']))}</td><td>{escape(str(log['actor']))}</td><td>{escape(str(log['activity']))}</td><td>{escape(str(log['target']))}</td></tr>" for log in audit_log_rows()]
    return render_page("Audit Logs", table(["Time", "Actor", "Activity", "Target"], rows), "Directory and application registration changes.")


@app.get("/ui/conditional-access", response_class=HTMLResponse)
def ui_conditional_access() -> HTMLResponse:
    rows = [
        "<tr><td>Require MFA for Admin Roles</td><td>Users with IGA_ADMIN claim</td><td>Report-only</td><td>High impact</td></tr>",
        "<tr><td>Block Unknown Client Redirects</td><td>OAuth clients</td><td>Enabled</td><td>Critical</td></tr>",
        "<tr><td>Review Machine Identity Rotation</td><td>NHI with overdue rotation</td><td>Enabled</td><td>High</td></tr>",
    ]
    return render_page("Conditional Access", table(["Policy", "Scope", "Mode", "Impact"], rows), "Policy-style controls for login, OAuth clients, and machine identities.")
