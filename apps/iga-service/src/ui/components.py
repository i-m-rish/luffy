from __future__ import annotations


def badge(text: object, css_class: str = "") -> str:
    return f'<span class="badge {css_class}">{text}</span>'


def metric_card(label: str, value: object, hint: str = "") -> str:
    hint_html = f'<div class="muted">{hint}</div>' if hint else ""
    return f'<div class="card"><div class="muted">{label}</div><div class="metric">{value}</div>{hint_html}</div>'


def table(headers: list[str], rows: list[str]) -> str:
    header_html = "".join(f"<th>{header}</th>" for header in headers)
    return f'<div class="table-wrap"><table><tr>{header_html}</tr>{"".join(rows)}</table></div>'


def callout(title: str, items: list[str]) -> str:
    item_html = "".join(f"<li>{item}</li>" for item in items)
    return f'<div class="callout"><strong>{title}</strong><ul>{item_html}</ul></div>'


def action_tile(title: str, description: str, href: str) -> str:
    return f"""
    <a class="tile" href="{href}">
      <span class="tile-kicker">Open workspace</span>
      <strong>{title}</strong>
      <span>{description}</span>
    </a>
    """


def page_shell(title: str, body: str, subtitle: str = "") -> str:
    subtitle_html = f"<p class='subtitle'>{subtitle}</p>" if subtitle else ""
    return f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{title}</title>
        <style>
          :root {{ --bg:#eef2f7; --card:#ffffff; --ink:#0f172a; --muted:#64748b; --line:#dbe3ef; --nav:#07111f; --accent:#2563eb; --accent2:#7c3aed; --shadow:0 16px 40px rgba(15,23,42,.10); }}
          * {{ box-sizing:border-box; }}
          body {{ font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; margin:0; background:var(--bg); color:var(--ink); }}
          .layout {{ min-height:100vh; display:grid; grid-template-columns:292px 1fr; }}
          aside {{ background:linear-gradient(180deg,#07111f 0%,#111827 55%,#172554 100%); color:white; padding:24px 18px; position:sticky; top:0; height:100vh; overflow:auto; }}
          .brand {{ display:flex; align-items:center; gap:12px; margin-bottom:24px; }}
          .brand-mark {{ width:42px; height:42px; border-radius:14px; background:linear-gradient(135deg,#38bdf8,#8b5cf6); display:grid; place-items:center; font-weight:900; }}
          .brand small {{ display:block; color:#93c5fd; margin-top:2px; }}
          .side-section {{ color:#93c5fd; font-size:11px; letter-spacing:.09em; text-transform:uppercase; font-weight:900; margin:18px 10px 8px; }}
          nav {{ display:flex; flex-direction:column; gap:5px; }}
          nav a {{ color:#dbeafe; text-decoration:none; font-size:14px; padding:10px 12px; border-radius:11px; display:flex; justify-content:space-between; }}
          nav a:hover {{ background:rgba(255,255,255,.09); color:white; }}
          .nav-pill {{ color:#bfdbfe; font-size:11px; }}
          .content {{ min-width:0; }}
          header {{ background:radial-gradient(circle at top left,#dbeafe 0,#ffffff 44%,#f8fafc 100%); padding:22px 34px 26px; border-bottom:1px solid var(--line); }}
          .topbar {{ display:flex; gap:14px; align-items:center; justify-content:space-between; margin-bottom:18px; }}
          .search-box {{ display:flex; gap:8px; flex:1; max-width:720px; }}
          .search-box input {{ width:100%; padding:11px 12px; border:1px solid #cbd5e1; border-radius:12px; background:white; }}
          .search-box button, button, .button {{ border:0; background:var(--accent); color:white; padding:10px 14px; border-radius:12px; font-weight:800; text-decoration:none; cursor:pointer; }}
          .session-card {{ background:white; border:1px solid var(--line); border-radius:14px; padding:9px 12px; font-size:13px; color:#334155; white-space:nowrap; }}
          .eyebrow {{ color:#0369a1; text-transform:uppercase; letter-spacing:.12em; font-size:12px; font-weight:900; margin-bottom:8px; }}
          header h1 {{ margin:0; font-size:32px; line-height:1.15; }}
          .subtitle {{ color:#475569; margin:10px 0 0 0; max-width:940px; }}
          .status-strip {{ display:flex; flex-wrap:wrap; gap:10px; margin-top:16px; }}
          .status-chip {{ background:white; border:1px solid var(--line); border-radius:999px; padding:7px 11px; color:#334155; font-size:13px; }}
          main {{ padding:28px 34px 44px; }}
          .section-title {{ margin:30px 0 12px; font-size:20px; }}
          .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:16px; }}
          .tile-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:16px; margin:18px 0; }}
          .tile {{ display:block; min-height:128px; background:linear-gradient(180deg,#ffffff,#f8fafc); border:1px solid var(--line); border-radius:18px; padding:18px; text-decoration:none; color:var(--ink); box-shadow:var(--shadow); transition:transform .16s ease,border-color .16s ease; }}
          .tile:hover {{ transform:translateY(-2px); border-color:var(--accent); }}
          .tile strong {{ display:block; margin:8px 0 7px; font-size:17px; }}
          .tile span {{ color:var(--muted); font-size:13px; line-height:1.45; }}
          .tile-kicker {{ color:#0369a1 !important; text-transform:uppercase; letter-spacing:.08em; font-weight:900; font-size:11px !important; }}
          .card {{ background:var(--card); border:1px solid var(--line); border-radius:18px; padding:18px; box-shadow:var(--shadow); }}
          .metric {{ font-size:32px; font-weight:900; margin-top:8px; letter-spacing:-.03em; }}
          .muted {{ color:var(--muted); font-size:13px; }}
          .table-wrap {{ border:1px solid var(--line); border-radius:18px; overflow:auto; box-shadow:var(--shadow); background:white; }}
          table {{ width:100%; border-collapse:collapse; min-width:780px; }}
          th,td {{ padding:13px 14px; border-bottom:1px solid var(--line); text-align:left; font-size:14px; vertical-align:top; }}
          th {{ background:#f8fafc; font-size:11px; text-transform:uppercase; letter-spacing:.06em; color:#475569; }}
          tr:hover td {{ background:#f8fafc; }}
          a {{ color:#1d4ed8; }}
          .badge {{ display:inline-block; padding:4px 9px; border-radius:999px; background:#e5e7eb; font-size:12px; font-weight:800; }}
          .risk-HIGH,.risk-CRITICAL,.status-ORPHAN {{ background:#fee2e2; color:#991b1b; }}
          .risk-MEDIUM,.status-PARTIAL,.status-TEMPORARY_ACTIVE,.status-SUBMITTED,.status-DRAFT {{ background:#fef3c7; color:#92400e; }}
          .risk-LOW,.status-MATCHED,.status-ACTIVE,.status-OPEN {{ background:#dcfce7; color:#166534; }}
          .status-TERMINATED,.status-DISABLED {{ background:#fee2e2; color:#991b1b; }}
          .callout {{ background:linear-gradient(90deg,#fff7ed,#ffffff); border:1px solid #fed7aa; border-radius:18px; padding:16px 18px; margin:20px 0; box-shadow:0 10px 28px rgba(251,146,60,.10); }}
          .callout ul {{ margin:8px 0 0 18px; }}
          form.form-card {{ display:grid; gap:12px; max-width:760px; }}
          label {{ font-weight:800; font-size:13px; color:#334155; }}
          input,select,textarea {{ width:100%; padding:10px 12px; border:1px solid #cbd5e1; border-radius:12px; background:white; }}
          textarea {{ min-height:90px; }}
          @media(max-width:900px) {{ .layout {{ grid-template-columns:1fr; }} aside {{ position:relative; height:auto; }} nav {{ flex-direction:row; flex-wrap:wrap; }} .topbar {{ flex-direction:column; align-items:stretch; }} header,main {{ padding-left:20px; padding-right:20px; }} }}
        </style>
      </head>
      <body>
        <div class="layout">
          <aside>
            <div class="brand"><div class="brand-mark">IGA</div><div><strong>Luffy Identity Security</strong><small>SailPoint-style console</small></div></div>
            <nav>
              <div class="side-section">Overview</div>
              <a href="/ui">Dashboard <span class="nav-pill">Home</span></a>
              <a href="/ui/search">Global Search <span class="nav-pill">Find</span></a>
              <a href="/ui/requests/resources">Request Center <span class="nav-pill">Workflow</span></a>
              <div class="side-section">Governance</div>
              <a href="/ui/identities">Identity Warehouse <span class="nav-pill">People</span></a>
              <a href="/ui/applications">Sources <span class="nav-pill">Apps</span></a>
              <a href="/ui/accounts">Accounts <span class="nav-pill">Aggregation</span></a>
              <a href="/ui/entitlements">Entitlements <span class="nav-pill">Catalog</span></a>
              <a href="/ui/correlation-results">Correlation <span class="nav-pill">Matches</span></a>
              <div class="side-section">Controls</div>
              <a href="/ui/access-reviews">Access Reviews <span class="nav-pill">Certify</span></a>
              <a href="/ui/certifications">Certification Mgmt <span class="nav-pill">Campaigns</span></a>
              <a href="/ui/sod-policies">SOD Policies <span class="nav-pill">Conflicts</span></a>
              <a href="/ui/governance-policies">Governance Policies <span class="nav-pill">Rules</span></a>
              <a href="/ui/policy-violations">Policy Violations <span class="nav-pill">Findings</span></a>
              <a href="/ui/orphan-accounts">Orphan Accounts <span class="nav-pill">Risk</span></a>
              <a href="/ui/high-risk-access">High Risk <span class="nav-pill">Critical</span></a>
              <div class="side-section">Administration</div>
              <a href="/ui/manage/users">Create Users <span class="nav-pill">Admin</span></a>
              <a href="/ui/manage/applications">Create Apps <span class="nav-pill">Admin</span></a>
              <a href="/docs">API Docs <span class="nav-pill">OpenAPI</span></a>
            </nav>
          </aside>
          <section class="content">
            <header>
              <div class="topbar">
                <form class="search-box" method="get" action="/ui/search">
                  <input name="q" placeholder="Search identities, accounts, sources, entitlements, policies..." />
                  <button type="submit">Search</button>
                </form>
                <div class="session-card"><a href="/me">Session</a> · <a href="/logout">Logout</a></div>
              </div>
              <div class="eyebrow">Identity governance and administration</div>
              <h1>{title}</h1>
              {subtitle_html}
              <div class="status-strip">
                <span class="status-chip">IdP-backed login</span>
                <span class="status-chip">RBAC enforced</span>
                <span class="status-chip">Object model</span>
                <span class="status-chip">Workflow simulation</span>
              </div>
            </header>
            <main>{body}</main>
          </section>
        </div>
      </body>
    </html>
    """
