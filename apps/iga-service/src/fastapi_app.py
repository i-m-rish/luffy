from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from repository import (
    get_accounts,
    get_applications,
    get_assignments,
    get_correlation_results,
    get_entitlements,
    get_high_risk_access,
    get_identities,
    get_identity_access,
    get_orphan_accounts,
)

app = FastAPI(
    title="Luffy IGA Service",
    description="Read-only IGA governance API over normalized sample data.",
    version="0.1.0",
)


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
          header {{ background: #0f172a; color: white; padding: 18px 28px; }}
          main {{ padding: 24px 28px; }}
          nav a {{ color: #dbeafe; margin-right: 16px; text-decoration: none; }}
          .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 16px; }}
          .card {{ background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; box-shadow: 0 1px 2px rgba(0,0,0,.05); }}
          .metric {{ font-size: 30px; font-weight: 700; margin-top: 8px; }}
          table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; }}
          th, td {{ padding: 10px 12px; border-bottom: 1px solid #e5e7eb; text-align: left; font-size: 14px; vertical-align: top; }}
          th {{ background: #f3f4f6; }}
          .badge {{ display: inline-block; padding: 3px 8px; border-radius: 999px; background: #e5e7eb; font-size: 12px; }}
          .risk-HIGH, .risk-CRITICAL, .status-ORPHAN {{ background: #fee2e2; color: #991b1b; }}
          .risk-MEDIUM, .status-PARTIAL {{ background: #fef3c7; color: #92400e; }}
          .risk-LOW, .status-MATCHED {{ background: #dcfce7; color: #166534; }}
        </style>
      </head>
      <body>
        <header>
          <h1>{title}</h1>
          <nav>
            <a href="/ui">Dashboard</a>
            <a href="/ui/applications">Applications</a>
            <a href="/ui/identities">Identities</a>
            <a href="/ui/accounts">Accounts</a>
            <a href="/ui/entitlements">Entitlements</a>
            <a href="/ui/orphan-accounts">Orphans</a>
            <a href="/ui/high-risk-access">High Risk</a>
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
    return {"status": "ok", "service": "iga-service"}


@app.get("/applications")
def applications() -> list[dict[str, object]]:
    return get_applications()


@app.get("/identities")
def identities() -> list[dict[str, object]]:
    return get_identities()


@app.get("/accounts")
def accounts() -> list[dict[str, object]]:
    return get_accounts()


@app.get("/entitlements")
def entitlements() -> list[dict[str, object]]:
    return get_entitlements()


@app.get("/assignments")
def assignments() -> list[dict[str, object]]:
    return get_assignments()


@app.get("/correlation-results")
def correlation_results() -> list[dict[str, object]]:
    return get_correlation_results()


@app.get("/governance/orphan-accounts")
def orphan_accounts() -> list[dict[str, object]]:
    return get_orphan_accounts()


@app.get("/governance/high-risk-access")
def high_risk_access() -> list[dict[str, object]]:
    return get_high_risk_access()


@app.get("/governance/identity/{identity_id}/access")
def identity_access(identity_id: str) -> dict[str, object]:
    result = get_identity_access(identity_id)
    if result is None:
        raise HTTPException(status_code=404, detail={"error": "identity_not_found", "identity_id": identity_id})
    return result


@app.get("/ui", response_class=HTMLResponse)
def ui_dashboard() -> HTMLResponse:
    cards = {
        "Applications": len(get_applications()),
        "Identities": len(get_identities()),
        "Accounts": len(get_accounts()),
        "Entitlements": len(get_entitlements()),
        "Assignments": len(get_assignments()),
        "Correlation Results": len(get_correlation_results()),
        "Orphan Accounts": len(get_orphan_accounts()),
        "High-Risk Access": len(get_high_risk_access()),
    }
    body = "".join(
        f'<div class="card"><div>{label}</div><div class="metric">{value}</div></div>'
        for label, value in cards.items()
    )
    return render_page("Luffy IGA Dashboard", f'<section class="grid">{body}</section>')


@app.get("/ui/applications", response_class=HTMLResponse)
def ui_applications() -> HTMLResponse:
    rows = "".join(
        f"<tr><td>{a['application_id']}</td><td>{a['application_name']}</td><td>{a['application_type']}</td><td>{a['integration_pattern']}</td><td><span class='badge risk-{a['risk_level']}'>{a['risk_level']}</span></td><td>{a['status']}</td></tr>"
        for a in get_applications()
    )
    return render_page("IGA Applications", f"<table><tr><th>ID</th><th>Name</th><th>Type</th><th>Pattern</th><th>Risk</th><th>Status</th></tr>{rows}</table>")


@app.get("/ui/identities", response_class=HTMLResponse)
def ui_identities() -> HTMLResponse:
    rows = "".join(
        f"<tr><td>{i['identity_id']}</td><td>{i['display_name']}</td><td>{i['employee_id']}</td><td>{i['lan_id']}</td><td>{i['identity_status']}</td></tr>"
        for i in get_identities()
    )
    return render_page("IGA Identities", f"<table><tr><th>ID</th><th>Name</th><th>Employee ID</th><th>LAN ID</th><th>Status</th></tr>{rows}</table>")


@app.get("/ui/accounts", response_class=HTMLResponse)
def ui_accounts() -> HTMLResponse:
    rows = "".join(
        f"<tr><td>{a['account_id']}</td><td>{a['application_id']}</td><td>{a['lan_id']}</td><td>{a['email']}</td><td><span class='badge status-{a['correlation_status']}'>{a['correlation_status']}</span></td></tr>"
        for a in get_accounts()
    )
    return render_page("IGA Accounts", f"<table><tr><th>ID</th><th>Application</th><th>LAN ID</th><th>Email</th><th>Correlation</th></tr>{rows}</table>")


@app.get("/ui/entitlements", response_class=HTMLResponse)
def ui_entitlements() -> HTMLResponse:
    rows = "".join(
        f"<tr><td>{e['entitlement_id']}</td><td>{e['application_id']}</td><td>{e['entitlement_name']}</td><td>{e['entitlement_description']}</td><td><span class='badge risk-{e['risk_level']}'>{e['risk_level']}</span></td></tr>"
        for e in get_entitlements()
    )
    return render_page("IGA Entitlements", f"<table><tr><th>ID</th><th>Application</th><th>Name</th><th>Description</th><th>Risk</th></tr>{rows}</table>")


@app.get("/ui/orphan-accounts", response_class=HTMLResponse)
def ui_orphan_accounts() -> HTMLResponse:
    rows = "".join(
        f"<tr><td>{item['account']['account_id']}</td><td>{item['application']['application_name']}</td><td>{item['account']['lan_id']}</td><td>{item['account']['email']}</td><td>{item['correlation_result']['reason']}</td></tr>"
        for item in get_orphan_accounts()
    )
    return render_page("IGA Orphan Accounts", f"<table><tr><th>Account</th><th>Application</th><th>LAN ID</th><th>Email</th><th>Reason</th></tr>{rows}</table>")


@app.get("/ui/high-risk-access", response_class=HTMLResponse)
def ui_high_risk_access() -> HTMLResponse:
    rows = "".join(
        f"<tr><td>{item['account']['lan_id']}</td><td>{item['application']['application_name']}</td><td>{item['entitlement']['entitlement_name']}</td><td><span class='badge risk-{item['entitlement']['risk_level']}'>{item['entitlement']['risk_level']}</span></td><td>{item['assignment']['assigned_by']}</td></tr>"
        for item in get_high_risk_access()
    )
    return render_page("IGA High-Risk Access", f"<table><tr><th>LAN ID</th><th>Application</th><th>Entitlement</th><th>Risk</th><th>Assigned By</th></tr>{rows}</table>")
