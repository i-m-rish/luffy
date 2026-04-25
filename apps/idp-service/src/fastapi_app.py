from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from auth import ACCESS_TOKENS, AUTHORIZATION_CODES, IDP_USERS, REGISTERED_CLIENTS
from auth_routes import router as auth_router
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
    version="0.2.0",
)
app.include_router(auth_router)


def render_page(title: str, body: str) -> HTMLResponse:
    html = f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{title}</title>
        <style>
          body {{ font-family: Arial, sans-serif; margin: 0; background: #f6f8fa; color: #17202a; }}
          header {{ background: #111827; color: white; padding: 18px 28px; }}
          main {{ padding: 24px 28px; }}
          nav a {{ color: #dbeafe; margin-right: 16px; text-decoration: none; }}
          .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 16px; }}
          .card {{ background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; box-shadow: 0 1px 2px rgba(0,0,0,.05); }}
          .metric {{ font-size: 30px; font-weight: 700; margin-top: 8px; }}
          table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; }}
          th, td {{ padding: 10px 12px; border-bottom: 1px solid #e5e7eb; text-align: left; font-size: 14px; }}
          th {{ background: #f3f4f6; }}
          .badge {{ display: inline-block; padding: 3px 8px; border-radius: 999px; background: #e5e7eb; font-size: 12px; font-weight: 700; }}
          .risk-HIGH, .risk-CRITICAL {{ background: #fee2e2; color: #991b1b; }}
          .risk-MEDIUM {{ background: #fef3c7; color: #92400e; }}
          .risk-LOW {{ background: #dcfce7; color: #166534; }}
          .status-operational {{ background: #dcfce7; color: #166534; }}
          .muted {{ color: #64748b; }}
        </style>
      </head>
      <body>
        <header>
          <h1>{title}</h1>
          <nav>
            <a href="/ui">Dashboard</a>
            <a href="/ui/status">IdP Status</a>
            <a href="/ui/identities">Identities</a>
            <a href="/ui/groups">Groups</a>
            <a href="/ui/app-registrations">Apps</a>
            <a href="/ui/oauth-clients">OAuth Clients</a>
            <a href="/ui/machine-identities">Machine Identities</a>
            <a href="/docs">API Docs</a>
          </nav>
        </header>
        <main>{body}</main>
      </body>
    </html>
    """
    return HTMLResponse(html)


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
    cards = "".join(
        f'<div class="card"><div>{key.replace("_", " ").title()}</div><div class="metric">{value}</div></div>'
        for key, value in data.items()
    )
    auth_cards = "".join(
        [
            f'<div class="card"><div>Registered OAuth Clients</div><div class="metric">{len(REGISTERED_CLIENTS)}</div></div>',
            f'<div class="card"><div>Demo Login Users</div><div class="metric">{len(IDP_USERS)}</div></div>',
            f'<div class="card"><div>Active Auth Codes</div><div class="metric">{len(AUTHORIZATION_CODES)}</div></div>',
            f'<div class="card"><div>Active Tokens</div><div class="metric">{len(ACCESS_TOKENS)}</div></div>',
        ]
    )
    return render_page(
        "Luffy IdP Dashboard",
        f'<section class="grid">{cards}{auth_cards}</section>',
    )


@app.get("/ui/status", response_class=HTMLResponse)
def ui_status() -> HTMLResponse:
    rows = "".join(
        [
            "<tr><td>Issuer</td><td>http://127.0.0.1:8002</td></tr>",
            "<tr><td>Status</td><td><span class='badge status-operational'>operational</span></td></tr>",
            "<tr><td>Supported Flow</td><td>authorization_code_demo</td></tr>",
            "<tr><td>Token Format</td><td>opaque_demo_token</td></tr>",
            f"<tr><td>Registered Clients</td><td>{len(REGISTERED_CLIENTS)}</td></tr>",
            f"<tr><td>Demo Users</td><td>{len(IDP_USERS)}</td></tr>",
            f"<tr><td>Active Auth Codes</td><td>{len(AUTHORIZATION_CODES)}</td></tr>",
            f"<tr><td>Active Tokens</td><td>{len(ACCESS_TOKENS)}</td></tr>",
        ]
    )
    return render_page("IdP Status", f"<table><tr><th>Control</th><th>Value</th></tr>{rows}</table>")


@app.get("/ui/identities", response_class=HTMLResponse)
def ui_identities() -> HTMLResponse:
    rows = "".join(
        f"<tr><td>{i['identity_id']}</td><td>{i['display_name']}</td><td>{i['lan_id']}</td><td>{i['email']}</td><td><span class='badge'>{i['identity_status']}</span></td></tr>"
        for i in get_identities()
    )
    return render_page("IdP Identities", f"<table><tr><th>ID</th><th>Name</th><th>LAN ID</th><th>Email</th><th>Status</th></tr>{rows}</table>")


@app.get("/ui/groups", response_class=HTMLResponse)
def ui_groups() -> HTMLResponse:
    rows = "".join(
        f"<tr><td>{g['group_id']}</td><td>{g['group_name']}</td><td>{g['group_type']}</td><td><span class='badge risk-{g['risk_level']}'>{g['risk_level']}</span></td><td>{g['status']}</td></tr>"
        for g in get_groups()
    )
    return render_page("IdP Groups", f"<table><tr><th>ID</th><th>Name</th><th>Type</th><th>Risk</th><th>Status</th></tr>{rows}</table>")


@app.get("/ui/app-registrations", response_class=HTMLResponse)
def ui_app_registrations() -> HTMLResponse:
    rows = "".join(
        f"<tr><td>{a['app_id']}</td><td>{a['app_name']}</td><td>{a['auth_protocol']}</td><td>{a['sso_enabled']}</td><td>{a['status']}</td></tr>"
        for a in get_app_registrations()
    )
    return render_page("IdP App Registrations", f"<table><tr><th>App ID</th><th>Name</th><th>Protocol</th><th>SSO</th><th>Status</th></tr>{rows}</table>")


@app.get("/ui/oauth-clients", response_class=HTMLResponse)
def ui_oauth_clients() -> HTMLResponse:
    rows = "".join(
        f"<tr><td>{client_id}</td><td>{client['client_name']}</td><td>{client['redirect_uri']}</td><td>{', '.join(client['allowed_roles'])}</td></tr>"
        for client_id, client in REGISTERED_CLIENTS.items()
    )
    return render_page("IdP OAuth Clients", f"<table><tr><th>Client ID</th><th>Name</th><th>Redirect URI</th><th>Allowed Roles</th></tr>{rows}</table>")


@app.get("/ui/machine-identities", response_class=HTMLResponse)
def ui_machine_identities() -> HTMLResponse:
    rows = "".join(
        f"<tr><td>{m['machine_identity_id']}</td><td>{m['name']}</td><td>{m['type']}</td><td>{m['owner']}</td><td><span class='badge risk-{m['risk_level']}'>{m['risk_level']}</span></td><td>{m['rotation_status']}</td></tr>"
        for m in get_machine_identities()
    )
    return render_page("IdP Machine Identities", f"<table><tr><th>ID</th><th>Name</th><th>Type</th><th>Owner</th><th>Risk</th><th>Rotation</th></tr>{rows}</table>")
