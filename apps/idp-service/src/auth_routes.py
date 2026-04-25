from __future__ import annotations

from urllib.parse import urlencode

from fastapi import APIRouter, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse

from auth import (
    ACCESS_TOKENS,
    AUTHORIZATION_CODES,
    IDP_USERS,
    REGISTERED_CLIENTS,
    authenticate_user,
    create_authorization_code,
    exchange_code_for_token,
    get_userinfo,
    validate_client,
)

router = APIRouter(tags=["IdP Authentication"])


def login_page(client_id: str, redirect_uri: str, state: str, error: str = "") -> str:
    error_html = f"<div class='error'>{error}</div>" if error else ""
    demo_rows = "".join(
        f"<tr><td>{user.username}</td><td>{user.role}</td><td>{user.username}123</td></tr>"
        for user in IDP_USERS.values()
    )
    return f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Luffy IdP Login</title>
        <style>
          body {{ font-family: Arial, sans-serif; background: #111827; display: grid; place-items: center; min-height: 100vh; margin: 0; }}
          .shell {{ width: min(940px, 94vw); display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
          .card {{ background: white; border-radius: 16px; padding: 24px; box-shadow: 0 18px 45px rgba(0,0,0,.25); }}
          label {{ display: block; margin: 12px 0 6px; font-weight: 700; }}
          input {{ width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 10px; box-sizing: border-box; }}
          button {{ margin-top: 16px; width: 100%; padding: 11px; border: 0; border-radius: 10px; background: #2563eb; color: white; font-weight: 700; cursor: pointer; }}
          table {{ width: 100%; border-collapse: collapse; }}
          th,td {{ border-bottom: 1px solid #e5e7eb; padding: 8px; text-align: left; font-size: 13px; }}
          th {{ background: #f8fafc; }}
          .muted {{ color: #64748b; }}
          .error {{ background: #fee2e2; color: #991b1b; padding: 10px; border-radius: 10px; margin-bottom: 10px; }}
        </style>
      </head>
      <body>
        <div class="shell">
          <section class="card">
            <h1>Luffy IdP Login</h1>
            <p class="muted">Authenticate once with IdP. IGA receives local demo claims and applies RBAC.</p>
            {error_html}
            <form method="post" action="/oauth/authorize">
              <input type="hidden" name="client_id" value="{client_id}" />
              <input type="hidden" name="redirect_uri" value="{redirect_uri}" />
              <input type="hidden" name="state" value="{state}" />
              <label>Username</label>
              <input name="username" autocomplete="username" required />
              <label>Password</label>
              <input name="password" type="password" autocomplete="current-password" required />
              <button type="submit">Sign in and continue</button>
            </form>
          </section>
          <section class="card">
            <h2>Demo IdP users</h2>
            <p class="muted">Local demo only. IGA uses the returned role claim for RBAC.</p>
            <table><tr><th>User</th><th>Role Claim</th><th>Password</th></tr>{demo_rows}</table>
          </section>
        </div>
      </body>
    </html>
    """


@router.get("/.well-known/openid-configuration")
def openid_configuration() -> dict[str, object]:
    return {
        "issuer": "http://127.0.0.1:8002",
        "authorization_endpoint": "http://127.0.0.1:8002/oauth/authorize",
        "token_endpoint": "http://127.0.0.1:8002/oauth/token",
        "userinfo_endpoint": "http://127.0.0.1:8002/oauth/userinfo",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "claims_supported": ["sub", "preferred_username", "name", "email", "role"],
        "scopes_supported": ["openid", "profile", "email"],
    }


@router.get("/oauth/status")
def oauth_status() -> dict[str, object]:
    return {
        "issuer": "http://127.0.0.1:8002",
        "registered_client_count": len(REGISTERED_CLIENTS),
        "demo_user_count": len(IDP_USERS),
        "active_authorization_code_count": len(AUTHORIZATION_CODES),
        "active_access_token_count": len(ACCESS_TOKENS),
        "supported_flow": "authorization_code_demo",
        "token_format": "opaque_demo_token",
        "status": "operational",
    }


@router.get("/oauth/clients")
def oauth_clients() -> list[dict[str, object]]:
    return [
        {
            "client_id": client_id,
            "client_name": client["client_name"],
            "redirect_uri": client["redirect_uri"],
            "allowed_roles": client["allowed_roles"],
        }
        for client_id, client in REGISTERED_CLIENTS.items()
    ]


@router.get("/oauth/authorize", response_class=HTMLResponse)
def authorize_form(
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    state: str = Query(default=""),
) -> HTMLResponse:
    if not validate_client(client_id, redirect_uri):
        raise HTTPException(status_code=400, detail="Invalid client_id or redirect_uri")
    return HTMLResponse(login_page(client_id, redirect_uri, state))


@router.post("/oauth/authorize")
def authorize_submit(
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    state: str = Form(default=""),
    username: str = Form(...),
    password: str = Form(...),
) -> HTMLResponse | RedirectResponse:
    if not validate_client(client_id, redirect_uri):
        raise HTTPException(status_code=400, detail="Invalid client_id or redirect_uri")

    user = authenticate_user(username, password)
    if user is None:
        return HTMLResponse(login_page(client_id, redirect_uri, state, "Invalid username or password"), status_code=401)

    code = create_authorization_code(client_id, redirect_uri, user)
    query = urlencode({"code": code, "state": state})
    return RedirectResponse(url=f"{redirect_uri}?{query}", status_code=303)


@router.post("/oauth/token")
def token(
    code: str = Form(...),
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
) -> dict[str, object]:
    token_response = exchange_code_for_token(code, client_id, redirect_uri)
    if token_response is None:
        raise HTTPException(status_code=400, detail="Invalid or expired authorization code")
    return token_response


@router.get("/oauth/userinfo")
def userinfo(access_token: str = Query(...)) -> dict[str, object]:
    claims = get_userinfo(access_token)
    if claims is None:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    return claims
