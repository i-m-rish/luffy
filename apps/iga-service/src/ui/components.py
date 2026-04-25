from __future__ import annotations


def badge(text: object, css_class: str = "") -> str:
    return f'<span class="badge {css_class}">{text}</span>'


def metric_card(label: str, value: object, hint: str = "") -> str:
    hint_html = f'<div class="muted">{hint}</div>' if hint else ""
    return f'<div class="card"><div class="muted">{label}</div><div class="metric">{value}</div>{hint_html}</div>'


def table(headers: list[str], rows: list[str]) -> str:
    header_html = "".join(f"<th>{header}</th>" for header in headers)
    return f"<table><tr>{header_html}</tr>{''.join(rows)}</table>"


def callout(title: str, items: list[str]) -> str:
    item_html = "".join(f"<li>{item}</li>" for item in items)
    return f'<div class="callout"><strong>{title}</strong><ul>{item_html}</ul></div>'


def action_tile(title: str, description: str, href: str) -> str:
    return f"""
    <a class="tile" href="{href}">
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
          :root {{ --bg:#f8fafc; --card:#ffffff; --ink:#0f172a; --muted:#64748b; --line:#e2e8f0; --nav:#111827; --accent:#2563eb; }}
          body {{ font-family: Arial, sans-serif; margin: 0; background: var(--bg); color: var(--ink); }}
          header {{ background: var(--nav); color: white; padding: 18px 28px; border-bottom: 4px solid var(--accent); }}
          header h1 {{ margin: 0 0 8px 0; }}
          main {{ padding: 24px 28px; }}
          nav {{ display: flex; flex-wrap: wrap; gap: 10px 16px; }}
          nav a {{ color: #dbeafe; text-decoration: none; font-size: 14px; }}
          nav a:hover {{ color: white; text-decoration: underline; }}
          .subtitle {{ color: #dbeafe; margin: 0 0 12px 0; }}
          .section-title {{ margin: 28px 0 12px 0; }}
          .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 16px; }}
          .tile-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 14px; margin: 18px 0; }}
          .tile {{ display:block; background: white; border: 1px solid var(--line); border-radius: 14px; padding: 16px; text-decoration:none; color: var(--ink); box-shadow: 0 1px 2px rgba(0,0,0,.04); }}
          .tile strong {{ display:block; margin-bottom: 6px; }}
          .tile span {{ color: var(--muted); font-size: 13px; }}
          .tile:hover {{ border-color: var(--accent); box-shadow: 0 4px 14px rgba(37,99,235,.12); }}
          .card {{ background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 16px; box-shadow: 0 1px 2px rgba(0,0,0,.05); }}
          .metric {{ font-size: 32px; font-weight: 800; margin-top: 8px; }}
          .muted {{ color: var(--muted); font-size: 13px; }}
          table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; }}
          th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; font-size: 14px; vertical-align: top; }}
          th {{ background: #f1f5f9; font-size: 12px; text-transform: uppercase; letter-spacing: .03em; color: #475569; }}
          a {{ color: var(--accent); }}
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
            <a href="/ui">Home</a>
            <a href="/ui/identities">Identity Warehouse</a>
            <a href="/ui/applications">Sources</a>
            <a href="/ui/accounts">Accounts</a>
            <a href="/ui/entitlements">Entitlements</a>
            <a href="/ui/correlation-results">Correlation</a>
            <a href="/ui/access-reviews">Access Reviews</a>
            <a href="/ui/policy-violations">Policy Violations</a>
            <a href="/ui/orphan-accounts">Orphan Accounts</a>
            <a href="/ui/high-risk-access">High Risk</a>
            <a href="/docs">API Docs</a>
          </nav>
        </header>
        <main>{body}</main>
      </body>
    </html>
    """
