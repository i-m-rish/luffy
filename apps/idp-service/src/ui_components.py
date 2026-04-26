from __future__ import annotations

from html import escape

from fastapi.responses import HTMLResponse


def badge(text: object, css_class: str = "") -> str:
    return f'<span class="badge {css_class}">{escape(str(text))}</span>'


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
          :root {{ --bg:#f3f6fb; --panel:#fff; --ink:#0f172a; --muted:#64748b; --line:#dbe3ef; --accent:#2563eb; --shadow:0 16px 38px rgba(15,23,42,.10); }}
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
