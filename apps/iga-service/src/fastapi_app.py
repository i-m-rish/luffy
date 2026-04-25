from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from repository import (
    get_accounts,
    get_application_access_summary,
    get_applications,
    get_assignments,
    get_correlation_results,
    get_entitlements,
    get_governance_dashboard,
    get_high_risk_access,
    get_identities,
    get_identity_access,
    get_identity_access_summaries,
    get_orphan_accounts,
)

app = FastAPI(
    title="Luffy IGA Service",
    description="Read-only IGA governance API over normalized sample data.",
    version="0.2.1",
)


def badge(text: object, css_class: str = "") -> str:
    return f'<span class="badge {css_class}">{text}</span>'


def table(headers: list[str], rows: list[str]) -> str:
    header_html = "".join(f"<th>{header}</th>" for header in headers)
    return f"<table><tr>{header_html}</tr>{''.join(rows)}</table>"


def render_page(title: str, body: str, subtitle: str = "") -> HTMLResponse:
    subtitle_html = f"<p class='subtitle'>{subtitle}</p>" if subtitle else ""
    html = f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{title}</title>
        <style>
          :root {{ --bg:#f6f8fa; --card:#ffffff; --ink:#17202a; --muted:#64748b; --line:#e5e7eb; --nav:#0f172a; }}
          body {{ font-family: Arial, sans-serif; margin: 0; background: var(--bg); color: var(--ink); }}
          header {{ background: var(--nav); color: white; padding: 20px 28px; }}
          header h1 {{ margin: 0 0 8px 0; }}
          main {{ padding: 24px 28px; }}
          nav a {{ color: #dbeafe; margin-right: 16px; text-decoration: none; font-size: 14px; }}
          .subtitle {{ color: #dbeafe; margin: 0 0 12px 0; }}
          .section-title {{ margin: 28px 0 12px 0; }}
          .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 16px; }}
          .card {{ background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 16px; box-shadow: 0 1px 2px rgba(0,0,0,.05); }}
          .metric {{ font-size: 32px; font-weight: 800; margin-top: 8px; }}
          .muted {{ color: var(--muted); font-size: 13px; }}
          table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; }}
          th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; font-size: 14px; vertical-align: top; }}
          th {{ background: #f3f4f6; font-size: 12px; text-transform: uppercase; letter-spacing: .03em; color: #475569; }}
          a {{ color: #2563eb; }}
          .badge {{ display: inline-block; padding: 3px 8px; border-radius: 999px; background: #e5e7eb; font-size: 12px; font-weight: 700; }}
          .risk-HIGH, .risk-CRITICAL, .status-ORPHAN {{ background: #fee2e2; color: #991b1b; }}
          .risk-MEDIUM, .status-PARTIAL {{ background: #fef3c7; color: #92400e; }}
          .risk-LOW, .status-MATCHED {{ background: #dcfce7; color: #166534; }}
          .status-ACTIVE {{ background: #dcfce7; color: #166534; }}
          .status-TERMINATED, .status-DISABLED {{ background: #fee2e2; color: #991b1b; }}
          .callout {{ background: #fff7ed; border: 1px solid #fed7aa; border-radius: 14px; padding: 14px 16px; margin: 18px 0; }}
          .callout ul {{ margin: 8px 0 0 18px; }}
        </style>
      </head>
      <body>
        <header>
          <h1>{title}</h1>
          {subtitle_html}
          <nav>
            <a href="/ui">Dashboard</a>
            <a href="/ui/applications">Applications</a>
            <a href="/ui/identities">Identities</a>
            <a href="/ui/accounts">Accounts</a>
            <a href="/ui/entitlements">Entitlements</a>
            <a href="/ui/correlation-results">Correlation</a>
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


@app.get("/dashboard")
def dashboard() -> dict[str, object]:
    return get_governance_dashboard()


@app.get("/applications")
def applications() -> list[dict[str, object]]:
    return get_applications()


@app.get("/application-access-summary")
def application_access_summary() -> list[dict[str, object]]:
    return get_application_access_summary()


@app.get("/identities")
def identities() -> list[dict[str, object]]:
    return get_identities()


@app.get("/identity-access-summary")
def identity_access_summary() -> list[dict[str, object]]:
    return get_identity_access_summaries()


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


def render_application_summary_table() -> str:
    rows = []
    for application in get_application_access_summary():
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


@app.get("/ui", response_class=HTMLResponse)
def ui_dashboard() -> HTMLResponse:
    data = get_governance_dashboard()
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
    card_html = "".join(
        f'<div class="card"><div class="muted">{label}</div><div class="metric">{value}</div></div>'
        for label, value in cards.items()
    )
    risk_html = "".join(f"<li>{risk}</li>" for risk in top_risks)
    body = f"""
      <section class="grid">{card_html}</section>
      <div class="callout"><strong>Governance focus</strong><ul>{risk_html}</ul></div>
      <h2 class="section-title">Application access summary</h2>
      {render_application_summary_table()}
    """
    return render_page("Luffy IGA Dashboard", body, "Governance visibility over identities, accounts, entitlements, risk, and correlation.")


@app.get("/ui/applications", response_class=HTMLResponse)
def ui_applications() -> HTMLResponse:
    return render_page("IGA Applications", render_application_summary_table())


@app.get("/ui/identities", response_class=HTMLResponse)
def ui_identities() -> HTMLResponse:
    rows = []
    for identity in get_identity_access_summaries():
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
    return render_page(
        "IGA Identities",
        table(["ID", "Name", "Employee ID", "LAN ID", "Status", "Accounts", "Assignments", "High Risk"], rows),
    )


@app.get("/ui/identity/{identity_id}/access", response_class=HTMLResponse)
def ui_identity_access(identity_id: str) -> HTMLResponse:
    access = get_identity_access(identity_id)
    if access is None:
        return render_page("Identity Not Found", f"<div class='card'>No identity found for {identity_id}</div>")

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
    return render_page("IGA Identity Access", body)


@app.get("/ui/accounts", response_class=HTMLResponse)
def ui_accounts() -> HTMLResponse:
    rows = []
    for account in get_accounts():
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
    return render_page("IGA Accounts", table(["ID", "Application", "LAN ID", "Email", "Status", "Correlation"], rows))


@app.get("/ui/entitlements", response_class=HTMLResponse)
def ui_entitlements() -> HTMLResponse:
    rows = []
    for entitlement in get_entitlements():
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
    return render_page("IGA Entitlements", table(["ID", "Application", "Name", "Description", "Risk"], rows))


@app.get("/ui/correlation-results", response_class=HTMLResponse)
def ui_correlation_results() -> HTMLResponse:
    rows = []
    for result in get_correlation_results():
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
    return render_page(
        "IGA Correlation Results",
        table(["ID", "Account", "Identity", "Result", "Match Attribute", "Confidence", "Reason"], rows),
    )


@app.get("/ui/orphan-accounts", response_class=HTMLResponse)
def ui_orphan_accounts() -> HTMLResponse:
    rows = []
    for item in get_orphan_accounts():
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
    return render_page("IGA Orphan Accounts", table(["Account", "Application", "LAN ID", "Email", "Reason"], rows))


@app.get("/ui/high-risk-access", response_class=HTMLResponse)
def ui_high_risk_access() -> HTMLResponse:
    rows = []
    for item in get_high_risk_access():
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
    return render_page("IGA High-Risk Access", table(["LAN ID", "Application", "Entitlement", "Risk", "Assigned By"], rows))
