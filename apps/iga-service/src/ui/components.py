from __future__ import annotations


def badge(text: object, css_class: str = "") -> str:
    return f'<span class="badge {css_class}">{text}</span>'


def metric_card(label: str, value: object) -> str:
    return f'<div class="card"><div class="muted">{label}</div><div class="metric">{value}</div></div>'


def table(headers: list[str], rows: list[str]) -> str:
    header_html = "".join(f"<th>{header}</th>" for header in headers)
    return f"<table><tr>{header_html}</tr>{''.join(rows)}</table>"


def callout(title: str, items: list[str]) -> str:
    item_html = "".join(f"<li>{item}</li>" for item in items)
    return f'<div class="callout"><strong>{title}</strong><ul>{item_html}</ul></div>'


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
