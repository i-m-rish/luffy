from __future__ import annotations

from urllib.parse import urlencode

import httpx
from fastapi import FastAPI, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from domain import (
    AUDIT_EVENTS,
    CLIENT_ID,
    ELEVATION_REQUESTS,
    IDP_BASE_URL,
    LOCAL_USERS,
    REDIRECT_URI,
    SESSION_COOKIE_NAME,
    STATE_COOKIE_NAME,
    audit,
    create_auth_state,
    create_session,
    destroy_session,
    get_user_from_session,
    jit_provision_user,
    request_elevation,
)

app = FastAPI(
    title="Luffy ZSP JIT Enterprise App",
    description="Enterprise SaaS-style app with IdP login, JIT provisioning, RBAC, and temporary privilege elevation.",
    version="0.1.0",
)


def current_user(request: Request):
    return get_user_from_session(request.cookies.get(SESSION_COOKIE_NAME))


def require_user(request: Request):
    user = current_user(request)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def require_ui_user(request: Request):
    user = current_user(request)
    if user is None:
        return RedirectResponse(url="/login", status_code=303)
    return user


def badge(text: object, css_class: str = "") -> str:
    return f'<span class="badge {css_class}">{text}</span>'


def table(headers: list[str], rows: list[str]) -> str:
    return "<table><tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr>" + "".join(rows) + "</table>"


def page(title: str, body: str, subtitle: str = "") -> HTMLResponse:
    subtitle_html = f"<p class='subtitle'>{subtitle}</p>" if subtitle else ""
    html = f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{title}</title>
        <style>
          :root {{ --bg:#f8fafc; --ink:#0f172a; --muted:#64748b; --line:#e2e8f0; --nav:#172554; --accent:#2563eb; }}
          body {{ font-family: Arial, sans-serif; margin: 0; background: var(--bg); color: var(--ink); }}
          header {{ background: var(--nav); color: white; padding: 18px 28px; border-bottom: 4px solid #60a5fa; }}
          main {{ padding: 24px 28px; }}
          nav {{ display:flex; flex-wrap:wrap; gap:10px 16px; }}
          nav a {{ color:#dbeafe; text-decoration:none; font-size:14px; }}
          nav a:hover {{ color:white; text-decoration:underline; }}
          .subtitle {{ color:#dbeafe; margin-top:0; }}
          .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:16px; }}
          .card {{ background:white; border:1px solid var(--line); border-radius:14px; padding:16px; box-shadow:0 1px 2px rgba(0,0,0,.05); }}
          .metric {{ font-size:32px; font-weight:800; margin-top:8px; }}
          .muted {{ color:var(--muted); font-size:13px; }}
          table {{ width:100%; border-collapse:collapse; background:white; border-radius:12px; overflow:hidden; }}
          th,td {{ padding:10px 12px; border-bottom:1px solid var(--line); text-align:left; font-size:14px; vertical-align:top; }}
          th {{ background:#eff6ff; font-size:12px; text-transform:uppercase; color:#475569; }}
          .badge {{ display:inline-block; padding:3px 8px; border-radius:999px; background:#e5e7eb; font-size:12px; font-weight:700; }}
          .status-APPROVED, .role-ZSP_ADMIN {{ background:#dcfce7; color:#166534; }}
          .status-PENDING_APPROVAL {{ background:#fef3c7; color:#92400e; }}
          .role-ZSP_APPROVER {{ background:#e0f2fe; color:#075985; }}
          .role-ZSP_OPERATOR {{ background:#ede9fe; color:#5b21b6; }}
          .role-ZSP_VIEWER {{ background:#f1f5f9; color:#334155; }}
          a.button, button {{ display:inline-block; border:0; background:var(--accent); color:white; padding:10px 14px; border-radius:10px; text-decoration:none; font-weight:700; cursor:pointer; }}
          input, select {{ padding:9px; border:1px solid #cbd5e1; border-radius:10px; width:100%; box-sizing:border-box; }}
          label {{ display:block; margin:12px 0 6px; font-weight:700; }}
        </style>
      </head>
      <body>
        <header>
          <h1>{title}</h1>
          {subtitle_html}
          <nav>
            <a href="/">Home</a>
            <a href="/ui/profile">My Profile</a>
            <a href="/ui/elevation">JIT Elevation</a>
            <a href="/ui/requests">Requests</a>
            <a href="/ui/audit">Audit</a>
            <a href="/docs">API Docs</a>
            <a href="/logout">Logout</a>
          </nav>
        </header>
        <main>{body}</main>
      </body>
    </html>
    """
    return HTMLResponse(html)


@app.get("/health")
def health() -> dict[str, object]:
    return {"status": "ok", "service": "zsp-jit-app"}


@app.get("/login")
def login() -> RedirectResponse:
    state = create_auth_state()
    query = urlencode({"client_id": CLIENT_ID, "redirect_uri": REDIRECT_URI, "state": state})
    response = RedirectResponse(url=f"{IDP_BASE_URL}/oauth/authorize?{query}", status_code=303)
    response.set_cookie(STATE_COOKIE_NAME, state, httponly=True, samesite="lax", secure=False)
    return response


@app.get("/auth/callback")
def auth_callback(request: Request, code: str = Query(...), state: str = Query(default="")) -> RedirectResponse:
    expected_state = request.cookies.get(STATE_COOKIE_NAME)
    if not expected_state or state != expected_state:
        raise HTTPException(status_code=400, detail="Invalid authentication state")

    with httpx.Client(timeout=5.0) as client:
        token_response = client.post(
            f"{IDP_BASE_URL}/oauth/token",
            data={"code": code, "client_id": CLIENT_ID, "redirect_uri": REDIRECT_URI},
        )
    if token_response.status_code != 200:
        raise HTTPException(status_code=401, detail="Unable to exchange authorization code with IdP")

    claims = token_response.json().get("claims")
    if not isinstance(claims, dict):
        raise HTTPException(status_code=401, detail="Token response did not include claims")

    user = jit_provision_user(claims)
    session_id = create_session(user.username)
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(SESSION_COOKIE_NAME, session_id, httponly=True, samesite="lax", secure=False)
    response.delete_cookie(STATE_COOKIE_NAME)
    return response


@app.get("/logout")
def logout(request: Request) -> RedirectResponse:
    user = current_user(request)
    if user:
        audit("USER_LOGOUT", user.username, "User logged out")
    destroy_session(request.cookies.get(SESSION_COOKIE_NAME))
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(SESSION_COOKIE_NAME)
    response.delete_cookie(STATE_COOKIE_NAME)
    return response


@app.get("/api/me")
def api_me(request: Request) -> dict[str, object]:
    user = require_user(request)
    return user.as_dict()


@app.get("/api/users")
def api_users(request: Request) -> list[dict[str, object]]:
    user = require_user(request)
    if "ADMIN" not in user.permissions:
        raise HTTPException(status_code=403, detail="Admin permission required")
    return [u.as_dict() for u in LOCAL_USERS.values()]


@app.get("/api/elevation-requests")
def api_requests(request: Request) -> list[dict[str, object]]:
    require_user(request)
    return ELEVATION_REQUESTS


@app.post("/api/elevation-requests")
def api_request_elevation(request: Request, target_role: str = Form(...), reason: str = Form(...)) -> RedirectResponse:
    user = require_user(request)
    if "REQUEST_ELEVATION" not in user.permissions:
        raise HTTPException(status_code=403, detail="Elevation request permission required")
    request_elevation(user, target_role, reason)
    return RedirectResponse(url="/ui/requests", status_code=303)


@app.get("/api/audit")
def api_audit(request: Request) -> list[dict[str, object]]:
    user = require_user(request)
    if "VIEW_AUDIT" not in user.permissions:
        raise HTTPException(status_code=403, detail="Audit permission required")
    return AUDIT_EVENTS


@app.get("/", response_class=HTMLResponse, response_model=None)
def home(request: Request) -> Response:
    user = require_ui_user(request)
    if isinstance(user, RedirectResponse):
        return user
    cards = "".join(
        [
            f"<div class='card'><div class='muted'>Local Users</div><div class='metric'>{len(LOCAL_USERS)}</div></div>",
            f"<div class='card'><div class='muted'>Elevation Requests</div><div class='metric'>{len(ELEVATION_REQUESTS)}</div></div>",
            f"<div class='card'><div class='muted'>Audit Events</div><div class='metric'>{len(AUDIT_EVENTS)}</div></div>",
            f"<div class='card'><div class='muted'>Your App Role</div><div class='metric'>{user.app_role}</div></div>",
        ]
    )
    body = f"""
      <section class='grid'>{cards}</section>
      <h2>Enterprise functionality</h2>
      <div class='grid'>
        <div class='card'><strong>OIDC Login</strong><p class='muted'>Authentication delegated to IdP on port 8002.</p></div>
        <div class='card'><strong>JIT Provisioning</strong><p class='muted'>Local app user is created on first successful login.</p></div>
        <div class='card'><strong>Zero Standing Privilege</strong><p class='muted'>Privileged roles are requested temporarily instead of permanently assigned.</p></div>
        <div class='card'><strong>Audit Trail</strong><p class='muted'>Login, JIT provisioning, and elevation events are tracked.</p></div>
      </div>
    """
    return page("Secure Operations Portal", body, "Enterprise app with IdP authentication, JIT provisioning, RBAC, and temporary privilege elevation.")


@app.get("/ui/profile", response_class=HTMLResponse, response_model=None)
def profile(request: Request) -> Response:
    user = require_ui_user(request)
    if isinstance(user, RedirectResponse):
        return user
    rows = [f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in user.as_dict().items()]
    return page("My Profile", table(["Attribute", "Value"], rows), "Local account created from IdP claims.")


@app.get("/ui/elevation", response_class=HTMLResponse, response_model=None)
def elevation(request: Request) -> Response:
    user = require_ui_user(request)
    if isinstance(user, RedirectResponse):
        return user
    if "REQUEST_ELEVATION" not in user.permissions:
        return page("JIT Elevation", "<div class='card'>Your role can view the app but cannot request temporary privileged access.</div>")
    body = """
      <div class='card'>
        <form method='post' action='/api/elevation-requests'>
          <label>Target Temporary Role</label>
          <select name='target_role'>
            <option>ZSP_OPERATOR_ELEVATED</option>
            <option>ZSP_BREAK_GLASS_READER</option>
            <option>ZSP_SESSION_ADMIN</option>
          </select>
          <label>Business Justification</label>
          <input name='reason' required placeholder='Example: emergency remediation for production incident' />
          <p><button type='submit'>Request temporary access</button></p>
        </form>
      </div>
    """
    return page("JIT Elevation", body, "Request time-bound privilege instead of permanent standing access.")


@app.get("/ui/requests", response_class=HTMLResponse, response_model=None)
def requests_page(request: Request) -> Response:
    user = require_ui_user(request)
    if isinstance(user, RedirectResponse):
        return user
    rows = []
    for item in ELEVATION_REQUESTS:
        rows.append(
            "<tr>"
            f"<td>{item['request_id']}</td>"
            f"<td>{item['requester']}</td>"
            f"<td>{item['target_role']}</td>"
            f"<td>{badge(item['status'], 'status-' + item['status'])}</td>"
            f"<td>{item['reason']}</td>"
            "</tr>"
        )
    return page("Elevation Requests", table(["Request", "Requester", "Target Role", "Status", "Reason"], rows or ["<tr><td colspan='5'>No requests yet.</td></tr>"]))


@app.get("/ui/audit", response_class=HTMLResponse, response_model=None)
def audit_page(request: Request) -> Response:
    user = require_ui_user(request)
    if isinstance(user, RedirectResponse):
        return user
    if "VIEW_AUDIT" not in user.permissions:
        return page("Audit", "<div class='card'>Your role does not have audit visibility.</div>")
    rows = []
    for event in AUDIT_EVENTS:
        rows.append(
            "<tr>"
            f"<td>{event['event_type']}</td>"
            f"<td>{event['actor']}</td>"
            f"<td>{event['detail']}</td>"
            f"<td>{event['created_at']}</td>"
            "</tr>"
        )
    return page("Audit", table(["Event", "Actor", "Detail", "Time"], rows or ["<tr><td colspan='4'>No audit events yet.</td></tr>"]))
