from __future__ import annotations

from html import escape

from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from ui_components import badge, render_page, table

router = APIRouter(tags=["IdP Management"])

DRAFT_OBJECTS: list[dict[str, object]] = []
PROMOTED_OBJECTS: list[dict[str, object]] = []


def validate_draft(object_type: str, payload: dict[str, object]) -> list[str]:
    findings: list[str] = []
    if object_type == "USER" and not str(payload.get("email", "")).endswith("@example.com"):
        findings.append("Demo tenant expects example.com email addresses.")
    if object_type == "GROUP" and payload.get("risk_level") in {"HIGH", "CRITICAL"}:
        findings.append("High-risk group should be reviewed before assignment.")
    if object_type == "APP_REGISTRATION":
        redirect_uri = str(payload.get("redirect_uri", ""))
        if not redirect_uri.startswith("http://127.0.0.1"):
            findings.append("Local lab redirect URI should use http://127.0.0.1.")
    if object_type == "OAUTH_CLIENT":
        if not str(payload.get("redirect_uri", "")).startswith("http://127.0.0.1"):
            findings.append("OAuth client redirect URI is outside the local lab host.")
    if object_type == "CONDITIONAL_ACCESS" and payload.get("mode") == "OFF":
        findings.append("Policy is created in OFF mode and will not enforce controls.")
    if not findings:
        findings.append("Draft validation passed.")
    return findings


def create_draft(object_type: str, payload: dict[str, object]) -> dict[str, object]:
    draft = {
        "draft_id": f"IDP-DR-{len(DRAFT_OBJECTS) + len(PROMOTED_OBJECTS) + 1:04d}",
        "object_type": object_type,
        "payload": payload,
        "status": "VALIDATED",
        "findings": validate_draft(object_type, payload),
    }
    if any("should" in finding or "outside" in finding or "OFF" in finding for finding in draft["findings"]):
        draft["status"] = "VALIDATED_WITH_WARNINGS"
    DRAFT_OBJECTS.insert(0, draft)
    return draft


def object_rows(objects: list[dict[str, object]], promote: bool) -> list[str]:
    rows = []
    for item in objects:
        payload = item["payload"]
        name = payload.get("name") or payload.get("display_name") or payload.get("client_name") or payload.get("app_name") or payload.get("policy_name")
        findings = "<br />".join(escape(str(finding)) for finding in item.get("findings", []))
        action = ""
        if promote:
            action = (
                "<form method='post' action='/ui/idp-management/promote'>"
                f"<input type='hidden' name='draft_id' value='{escape(str(item['draft_id']))}' />"
                "<button type='submit'>Promote</button></form>"
            )
        rows.append(
            "<tr>"
            f"<td>{escape(str(item['draft_id']))}</td>"
            f"<td>{escape(str(item['object_type']))}</td>"
            f"<td>{escape(str(name))}</td>"
            f"<td>{badge(item['status'], 'status-' + str(item['status']))}</td>"
            f"<td>{findings}</td>"
            f"<td>{action}</td>"
            "</tr>"
        )
    return rows


@router.get("/ui/idp-management", response_class=HTMLResponse, response_model=None)
def ui_idp_management() -> Response:
    draft_rows = object_rows(DRAFT_OBJECTS, promote=True)
    promoted_rows = object_rows(PROMOTED_OBJECTS, promote=False)
    body = """
    <div class='grid'>
      <a class='card' href='/ui/idp-management/users'><strong>Create user</strong><p class='muted'>Draft a directory user before promotion.</p></a>
      <a class='card' href='/ui/idp-management/groups'><strong>Create group</strong><p class='muted'>Draft a security group / role group.</p></a>
      <a class='card' href='/ui/idp-management/app-registrations'><strong>Create app registration</strong><p class='muted'>Draft redirect URI and protocol settings.</p></a>
      <a class='card' href='/ui/idp-management/oauth-clients'><strong>Create OAuth client</strong><p class='muted'>Draft relying-party client settings.</p></a>
      <a class='card' href='/ui/idp-management/conditional-access'><strong>Create CA policy</strong><p class='muted'>Draft policy posture before enforcement.</p></a>
    </div>
    """
    body += "<h2 class='section-title'>Draft Objects</h2>" + table(["Draft", "Type", "Name", "Status", "Findings", "Action"], draft_rows or ["<tr><td colspan='6'>No drafts yet.</td></tr>"])
    body += "<h2 class='section-title'>Promoted Objects</h2>" + table(["Draft", "Type", "Name", "Status", "Findings", "Action"], promoted_rows or ["<tr><td colspan='6'>No promoted objects yet.</td></tr>"])
    return render_page("IdP Draft Management", body, "Create, validate, and promote IdP objects like users, groups, app registrations, OAuth clients, and conditional access policies.")


@router.post("/ui/idp-management/promote")
def ui_promote_idp_draft(draft_id: str = Form(...)) -> RedirectResponse:
    for draft in list(DRAFT_OBJECTS):
        if draft["draft_id"] == draft_id:
            DRAFT_OBJECTS.remove(draft)
            draft["status"] = "PROMOTED_TO_ACTIVE"
            PROMOTED_OBJECTS.insert(0, draft)
            break
    return RedirectResponse(url="/ui/idp-management", status_code=303)


@router.get("/ui/idp-management/users", response_class=HTMLResponse, response_model=None)
def ui_create_user() -> Response:
    form = """
    <div class='card'><form class='form-card' method='post' action='/ui/idp-management/users'>
      <label>Display Name</label><input name='display_name' required />
      <label>Username</label><input name='username' required />
      <label>Email</label><input name='email' required />
      <label>Role Claim</label><select name='role'><option>IGA_ADMIN</option><option>ACCESS_REVIEWER</option><option>APP_OWNER</option><option>READ_ONLY</option></select>
      <button type='submit'>Create draft user</button>
    </form></div>
    """
    return render_page("Create Draft User", form, "Draft a user before promoting it to the active directory model.")


@router.post("/ui/idp-management/users")
def ui_post_user(display_name: str = Form(...), username: str = Form(...), email: str = Form(...), role: str = Form(...)) -> RedirectResponse:
    create_draft("USER", {"display_name": display_name, "username": username, "email": email, "role": role})
    return RedirectResponse(url="/ui/idp-management", status_code=303)


@router.get("/ui/idp-management/groups", response_class=HTMLResponse, response_model=None)
def ui_create_group() -> Response:
    form = """
    <div class='card'><form class='form-card' method='post' action='/ui/idp-management/groups'>
      <label>Group Name</label><input name='name' required />
      <label>Group Type</label><select name='group_type'><option>SECURITY</option><option>APP_ROLE</option><option>DYNAMIC</option></select>
      <label>Risk Level</label><select name='risk_level'><option>LOW</option><option>MEDIUM</option><option>HIGH</option><option>CRITICAL</option></select>
      <button type='submit'>Create draft group</button>
    </form></div>
    """
    return render_page("Create Draft Group", form, "Draft an Entra-style group before promotion.")


@router.post("/ui/idp-management/groups")
def ui_post_group(name: str = Form(...), group_type: str = Form(...), risk_level: str = Form(...)) -> RedirectResponse:
    create_draft("GROUP", {"name": name, "group_type": group_type, "risk_level": risk_level})
    return RedirectResponse(url="/ui/idp-management", status_code=303)


@router.get("/ui/idp-management/app-registrations", response_class=HTMLResponse, response_model=None)
def ui_create_app_registration() -> Response:
    form = """
    <div class='card'><form class='form-card' method='post' action='/ui/idp-management/app-registrations'>
      <label>App Name</label><input name='app_name' required />
      <label>Protocol</label><select name='auth_protocol'><option>OIDC</option><option>SAML</option></select>
      <label>Redirect URI</label><input name='redirect_uri' required value='http://127.0.0.1:' />
      <button type='submit'>Create draft app registration</button>
    </form></div>
    """
    return render_page("Create Draft App Registration", form, "Draft app registration and redirect URI settings before active use.")


@router.post("/ui/idp-management/app-registrations")
def ui_post_app_registration(app_name: str = Form(...), auth_protocol: str = Form(...), redirect_uri: str = Form(...)) -> RedirectResponse:
    create_draft("APP_REGISTRATION", {"app_name": app_name, "auth_protocol": auth_protocol, "redirect_uri": redirect_uri})
    return RedirectResponse(url="/ui/idp-management", status_code=303)


@router.get("/ui/idp-management/oauth-clients", response_class=HTMLResponse, response_model=None)
def ui_create_oauth_client() -> Response:
    form = """
    <div class='card'><form class='form-card' method='post' action='/ui/idp-management/oauth-clients'>
      <label>Client Name</label><input name='client_name' required />
      <label>Client ID</label><input name='client_id' required />
      <label>Redirect URI</label><input name='redirect_uri' required value='http://127.0.0.1:' />
      <label>Allowed Roles</label><input name='allowed_roles' required value='READ_ONLY' />
      <button type='submit'>Create draft OAuth client</button>
    </form></div>
    """
    return render_page("Create Draft OAuth Client", form, "Draft OAuth client settings before active use.")


@router.post("/ui/idp-management/oauth-clients")
def ui_post_oauth_client(client_name: str = Form(...), client_id: str = Form(...), redirect_uri: str = Form(...), allowed_roles: str = Form(...)) -> RedirectResponse:
    create_draft("OAUTH_CLIENT", {"client_name": client_name, "client_id": client_id, "redirect_uri": redirect_uri, "allowed_roles": allowed_roles})
    return RedirectResponse(url="/ui/idp-management", status_code=303)


@router.get("/ui/idp-management/conditional-access", response_class=HTMLResponse, response_model=None)
def ui_create_conditional_access() -> Response:
    form = """
    <div class='card'><form class='form-card' method='post' action='/ui/idp-management/conditional-access'>
      <label>Policy Name</label><input name='policy_name' required />
      <label>Scope</label><input name='scope' required />
      <label>Mode</label><select name='mode'><option>REPORT_ONLY</option><option>ENABLED</option><option>OFF</option></select>
      <button type='submit'>Create draft conditional access policy</button>
    </form></div>
    """
    return render_page("Create Draft Conditional Access Policy", form, "Draft a conditional access policy before enforcement.")


@router.post("/ui/idp-management/conditional-access")
def ui_post_conditional_access(policy_name: str = Form(...), scope: str = Form(...), mode: str = Form(...)) -> RedirectResponse:
    create_draft("CONDITIONAL_ACCESS", {"policy_name": policy_name, "scope": scope, "mode": mode})
    return RedirectResponse(url="/ui/idp-management", status_code=303)


@router.get("/api/idp-management/drafts")
def api_idp_drafts() -> dict[str, object]:
    return {"drafts": DRAFT_OBJECTS, "promoted": PROMOTED_OBJECTS}


@router.post("/api/idp-management/drafts")
def api_create_idp_draft(object_type: str = Form(...), name: str = Form(...), redirect_uri: str = Form(default=""), risk_level: str = Form(default="LOW")) -> dict[str, object]:
    payload = {"name": name, "redirect_uri": redirect_uri, "risk_level": risk_level}
    return create_draft(object_type, payload)
