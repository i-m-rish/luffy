from __future__ import annotations

from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from auth import (
    IDP_BASE_URL,
    IDP_STATE_COOKIE_NAME,
    IGA_CLIENT_ID,
    IGA_REDIRECT_URI,
    SESSION_COOKIE_NAME,
    create_auth_state,
    create_session_from_claims,
    destroy_session,
    get_current_user,
)

router = APIRouter(tags=["IGA Auth"])


@router.get("/login")
def login() -> RedirectResponse:
    state = create_auth_state()
    query = urlencode(
        {
            "client_id": IGA_CLIENT_ID,
            "redirect_uri": IGA_REDIRECT_URI,
            "state": state,
        }
    )
    response = RedirectResponse(url=f"{IDP_BASE_URL}/oauth/authorize?{query}", status_code=303)
    response.set_cookie(
        key=IDP_STATE_COOKIE_NAME,
        value=state,
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return response


@router.get("/auth/callback")
def auth_callback(request: Request, code: str = Query(...), state: str = Query(default="")) -> RedirectResponse:
    expected_state = request.cookies.get(IDP_STATE_COOKIE_NAME)
    if not expected_state or state != expected_state:
        raise HTTPException(status_code=400, detail="Invalid authentication state")

    with httpx.Client(timeout=5.0) as client:
        token_response = client.post(
            f"{IDP_BASE_URL}/oauth/token",
            data={
                "code": code,
                "client_id": IGA_CLIENT_ID,
                "redirect_uri": IGA_REDIRECT_URI,
            },
        )

    if token_response.status_code != 200:
        raise HTTPException(status_code=401, detail="Unable to exchange IdP authorization code")

    token_payload = token_response.json()
    claims = token_payload.get("claims")
    if not isinstance(claims, dict):
        raise HTTPException(status_code=401, detail="IdP token response did not include claims")

    session_id = create_session_from_claims(claims)
    response = RedirectResponse(url="/ui", status_code=303)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        samesite="lax",
        secure=False,
    )
    response.delete_cookie(IDP_STATE_COOKIE_NAME)
    return response


@router.get("/logout")
def logout(request: Request) -> RedirectResponse:
    destroy_session(request.cookies.get(SESSION_COOKIE_NAME))
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(SESSION_COOKIE_NAME)
    response.delete_cookie(IDP_STATE_COOKIE_NAME)
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
