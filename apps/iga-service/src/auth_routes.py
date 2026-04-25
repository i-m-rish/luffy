from __future__ import annotations

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from auth import (
    DEMO_USERS,
    SESSION_COOKIE_NAME,
    authenticate_user,
    create_session,
    destroy_session,
    get_current_user,
)

router = APIRouter(tags=["IGA Auth"])


def login_page(error: str = "") -> str:
    error_html = f"<div class='error'>{error}</div>" if error else ""
    demo_rows = "".join(
        f"<tr><td>{user.username}</td><td>{user.role}</td><td>{user.username}123</td></tr>"
        for user in DEMO_USERS.values()
    )
    return f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Luffy IGA Login</title>
        <style>
          body {{ font-family: Arial, sans-serif; background: #0f172a; display: grid; place-items: center; min-height: 100vh; margin: 0; color: #17202a; }}
          .shell {{ width: min(920px, 94vw); display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
          .card {{ background: white; border-radius: 16px; padding: 24px; box-shadow: 0 18px 45px rgba(0,0,0,.25); }}
          h1 {{ margin-top: 0; }}
          label {{ display: block; margin: 12px 0 6px; font-weight: 700; }}
          input {{ width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 10px; }}
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
            <h1>Luffy IGA Login</h1>
            <p class="muted">Local demo authentication for role-based IGA access.</p>
            {error_html}
            <form method="post" action="/login">
              <label>Username</label>
              <input name="username" autocomplete="username" required />
              <label>Password</label>
              <input name="password" type="password" autocomplete="current-password" required />
              <button type="submit">Sign in</button>
            </form>
          </section>
          <section class="card">
            <h2>Demo users</h2>
            <p class="muted">These are local sample users only. No real secrets.</p>
            <table><tr><th>User</th><th>Role</th><th>Password</th></tr>{demo_rows}</table>
          </section>
        </div>
      </body>
    </html>
    """


@router.get("/login", response_class=HTMLResponse)
def login_form() -> HTMLResponse:
    return HTMLResponse(login_page())


@router.post("/login")
def login(username: str = Form(...), password: str = Form(...)) -> RedirectResponse:
    user = authenticate_user(username, password)
    if user is None:
        return HTMLResponse(login_page("Invalid username or password"), status_code=401)

    session_id = create_session(user.username)
    response = RedirectResponse(url="/ui", status_code=303)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return response


@router.get("/logout")
def logout(request: Request) -> RedirectResponse:
    destroy_session(request.cookies.get(SESSION_COOKIE_NAME))
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response


@router.get("/me")
def me(request: Request) -> dict[str, object]:
    user = get_current_user(request)
    if user is None:
        return {"authenticated": False}
    return {"authenticated": True, "user": user.public_profile()}


@router.get("/forbidden", response_class=HTMLResponse)
def forbidden(request: Request) -> HTMLResponse:
    user = get_current_user(request)
    role = user.role if user else "anonymous"
    return HTMLResponse(
        f"""
        <!doctype html>
        <html lang="en">
          <head><meta charset="utf-8" /><title>Forbidden</title></head>
          <body style="font-family:Arial,sans-serif;padding:32px;">
            <h1>403 - Access denied</h1>
            <p>Your current role <strong>{role}</strong> does not have permission for this page.</p>
            <p><a href="/ui">Back to dashboard</a> · <a href="/logout">Logout</a></p>
          </body>
        </html>
        """,
        status_code=403,
    )
