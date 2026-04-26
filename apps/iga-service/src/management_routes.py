from __future__ import annotations

from html import escape

from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from auth import require_permission, require_ui_permission
from services.governance_service import governance_service
from ui.components import badge, page_shell, table

router = APIRouter(tags=["IGA Management"])

SOD_POLICIES: list[dict[str, object]] = [
    {"policy_id": "SOD-ZSP-001", "name": "ZSP Admin conflicts with temporary session admin", "left_role": "ZSP Administrator", "right_role": "Temporary Session Administrator", "severity": "CRITICAL", "status": "ACTIVE"}
]
GOVERNANCE_POLICIES: list[dict[str, object]] = [
    {"policy_id": "POL-ORPHAN-001", "name": "Orphan accounts require owner review", "policy_type": "ORPHAN_ACCOUNT", "severity": "HIGH", "status": "ACTIVE"},
    {"policy_id": "POL-ZSP-001", "name": "Temporary privilege requires certification", "policy_type": "TEMPORARY_PRIVILEGE", "severity": "CRITICAL", "status": "ACTIVE"},
]
CERTIFICATION_CAMPAIGNS: list[dict[str, object]] = [
    {"campaign_id": "CERT-Q2-ZSP", "name": "Q2 ZSP temporary privilege review", "scope": "zsp-jit-app critical entitlements", "owner": "Security Admin", "status": "DRAFT", "items": 2}
]
MANAGED_IDENTITIES: list[dict[str, object]] = []
MANAGED_SOURCES: list[dict[str, object]] = []
ACCESS_REQUESTS: list[dict[str, object]] = []


def object_link(label: object, href: str) -> str:
    return f"<a href='{escape(href)}'>{escape(str(label))}</a>"


def admin_redirect(request: Request) -> RedirectResponse | None:
    result = require_ui_permission(request, "CREATE_RESOURCE_REQUEST")
    if isinstance(result, RedirectResponse):
        return result
    return None


def render_options(records: list[dict[str, object]], value_key: str, label_key: str, secondary_key: str | None = None) -> str:
    parts = []
    for record in records:
        value = str(record[value_key])
        label = str(record[label_key])
        if secondary_key:
            label = f"{label} / {record[secondary_key]}"
        parts.append(f"<option value='{escape(value)}'>{escape(label)}</option>")
    return "".join(parts)


@router.get("/ui/search", response_class=HTMLResponse, response_model=None)
def ui_search(request: Request, q: str = Query(default="")) -> Response:
    result = require_ui_permission(request, "VIEW_DASHBOARD")
    if isinstance(result, RedirectResponse):
        return result
    rows = [
        f"<tr><td>{badge(item['type'])}</td><td>{object_link(item['name'], item['href'])}</td><td>{escape(item['id'])}</td></tr>"
        for item in governance_service.search(q)
    ]
    return HTMLResponse(page_shell("Global Search", table(["Type", "Name", "Object ID"], rows or ["<tr><td colspan='3'>Enter a search term.</td></tr>"]), f"Search results for: {q}" if q else "Search identities, sources, accounts, and entitlements."))


@router.get("/ui/requests/access", response_class=HTMLResponse, response_model=None)
def ui_access_requests(request: Request) -> Response:
    result = require_ui_permission(request, "VIEW_DASHBOARD")
    if isinstance(result, RedirectResponse):
        return result

    identity_options = render_options(governance_service.identities(), "identity_id", "display_name", "identity_id")
    entitlement_options = render_options(governance_service.entitlements(), "entitlement_id", "entitlement_name", "application_id")
    rows = []
    for item in ACCESS_REQUESTS:
        identity_id = str(item["target_identity_id"])
        entitlement_id = str(item["entitlement_id"])
        rows.append(
            "<tr>"
            f"<td>{escape(str(item['request_id']))}</td>"
            f"<td>{escape(str(item['requester']))}</td>"
            f"<td>{object_link(identity_id, f'/ui/identity/{identity_id}/access')}</td>"
            f"<td>{object_link(entitlement_id, f'/ui/entitlement/{entitlement_id}')}</td>"
            f"<td>{escape(str(item['access_type']))}</td>"
            f"<td>{badge(item['status'], 'status-' + str(item['status']))}</td>"
            f"<td>{escape(str(item['justification']))}</td>"
            "</tr>"
        )
    form = f"""
    <div class='card'><h2 style='margin-top:0'>Create Access Request</h2>
    <form class='form-card' method='post' action='/ui/requests/access'>
      <label>Target Identity</label><select name='target_identity_id'>{identity_options}</select>
      <label>Requested Entitlement</label><select name='entitlement_id'>{entitlement_options}</select>
      <label>Access Type</label><select name='access_type'><option>ADD_ACCESS</option><option>REMOVE_ACCESS</option><option>MODIFY_ACCESS</option></select>
      <label>Business Justification</label><textarea name='justification' required></textarea>
      <button type='submit'>Submit access request</button>
    </form></div>
    """
    body = form + "<h2 class='section-title'>Access Request Queue</h2>" + table(["Request", "Requester", "Identity", "Entitlement", "Type", "Status", "Justification"], rows or ["<tr><td colspan='7'>No access requests yet.</td></tr>"])
    return HTMLResponse(page_shell("Access Request", body, "Request, remove, or modify access like a SailPoint request center."))


@router.post("/ui/requests/access")
def ui_create_access_request(request: Request, target_identity_id: str = Form(...), entitlement_id: str = Form(...), access_type: str = Form(...), justification: str = Form(...)) -> RedirectResponse:
    user = require_permission(request, "CREATE_RESOURCE_REQUEST")
    item = {
        "request_id": f"AR-{len(ACCESS_REQUESTS) + 1:04d}",
        "requester": user.username,
        "target_identity_id": target_identity_id,
        "entitlement_id": entitlement_id,
        "access_type": access_type,
        "justification": justification,
        "status": "SUBMITTED",
    }
    ACCESS_REQUESTS.insert(0, item)
    governance_service.create_resource_request(user.username, access_type, "Entitlement", entitlement_id, f"{target_identity_id}: {justification}")
    return RedirectResponse(url="/ui/requests/access", status_code=303)


@router.get("/api/requests/access")
def api_access_requests(request: Request) -> list[dict[str, object]]:
    require_permission(request, "VIEW_DASHBOARD")
    return ACCESS_REQUESTS


@router.post("/api/requests/access")
def api_create_access_request(request: Request, target_identity_id: str = Form(...), entitlement_id: str = Form(...), access_type: str = Form(...), justification: str = Form(...)) -> dict[str, object]:
    user = require_permission(request, "CREATE_RESOURCE_REQUEST")
    item = {
        "request_id": f"AR-{len(ACCESS_REQUESTS) + 1:04d}",
        "requester": user.username,
        "target_identity_id": target_identity_id,
        "entitlement_id": entitlement_id,
        "access_type": access_type,
        "justification": justification,
        "status": "SUBMITTED",
    }
    ACCESS_REQUESTS.insert(0, item)
    return item


@router.get("/ui/requests/resources", response_class=HTMLResponse, response_model=None)
def ui_resource_requests(request: Request) -> Response:
    result = require_ui_permission(request, "VIEW_DASHBOARD")
    if isinstance(result, RedirectResponse):
        return result
    rows = [f"<tr><td>{escape(str(item['request_id']))}</td><td>{escape(str(item['requester']))}</td><td>{escape(str(item['request_type']))}</td><td>{escape(str(item['target_type']))}</td><td>{escape(str(item['target_id']))}</td><td>{badge(item['status'], 'status-' + str(item['status']))}</td><td>{escape(str(item['justification']))}</td></tr>" for item in governance_service.resource_requests()]
    form = """
    <div class='card'><h2 style='margin-top:0'>Create Resource Request</h2>
    <form class='form-card' method='post' action='/ui/requests/resources'>
      <label>Request Type</label><select name='request_type'><option>CREATE_SOURCE</option><option>CREATE_ENTITLEMENT</option><option>DEPROVISION_ACCESS</option></select>
      <label>Target Type</label><select name='target_type'><option>Identity</option><option>Source</option><option>Account</option><option>Entitlement</option></select>
      <label>Target ID</label><input name='target_id' required />
      <label>Justification</label><textarea name='justification' required></textarea>
      <button type='submit'>Submit request</button>
    </form></div>
    """
    body = form + "<h2 class='section-title'>Request Queue</h2>" + table(["Request", "Requester", "Type", "Target Type", "Target", "Status", "Justification"], rows or ["<tr><td colspan='7'>No requests yet.</td></tr>"])
    return HTMLResponse(page_shell("Resource Request Center", body, "Create and track non-access resource requests."))


@router.post("/ui/requests/resources")
def ui_create_resource_request(request: Request, request_type: str = Form(...), target_type: str = Form(...), target_id: str = Form(...), justification: str = Form(...)) -> RedirectResponse:
    user = require_permission(request, "CREATE_RESOURCE_REQUEST")
    governance_service.create_resource_request(user.username, request_type, target_type, target_id, justification)
    return RedirectResponse(url="/ui/requests/resources", status_code=303)


@router.get("/ui/manage/users", response_class=HTMLResponse, response_model=None)
def ui_manage_users(request: Request) -> Response:
    redirect = admin_redirect(request)
    if redirect:
        return redirect
    rows = [f"<tr><td>{escape(str(u['identity_id']))}</td><td>{escape(str(u['display_name']))}</td><td>{escape(str(u['lan_id']))}</td><td>{escape(str(u['email']))}</td><td>{badge(u['status'], 'status-' + str(u['status']))}</td></tr>" for u in MANAGED_IDENTITIES]
    form = """
    <div class='card'><h2 style='margin-top:0'>Create Identity</h2><form class='form-card' method='post' action='/ui/manage/users'>
      <label>Display Name</label><input name='display_name' required />
      <label>Employee ID</label><input name='employee_id' required />
      <label>LAN ID</label><input name='lan_id' required />
      <label>Email</label><input name='email' required />
      <label>Status</label><select name='status'><option>ACTIVE</option><option>STAGED</option><option>DISABLED</option><option>TERMINATED</option></select>
      <button type='submit'>Create identity</button>
    </form></div>
    """
    return HTMLResponse(page_shell("Create Users", form + table(["Identity", "Name", "LAN ID", "Email", "Status"], rows or ["<tr><td colspan='5'>No created identities yet.</td></tr>"]), "Create lab identity records."))


@router.post("/ui/manage/users")
def ui_create_user(request: Request, display_name: str = Form(...), employee_id: str = Form(...), lan_id: str = Form(...), email: str = Form(...), status: str = Form(...)) -> RedirectResponse:
    require_permission(request, "CREATE_RESOURCE_REQUEST")
    MANAGED_IDENTITIES.insert(0, {"identity_id": f"IGA-IDENTITY-{employee_id}", "display_name": display_name, "employee_id": employee_id, "lan_id": lan_id, "email": email, "status": status})
    return RedirectResponse(url="/ui/manage/users", status_code=303)


@router.get("/ui/manage/applications", response_class=HTMLResponse, response_model=None)
def ui_manage_applications(request: Request) -> Response:
    redirect = admin_redirect(request)
    if redirect:
        return redirect
    rows = [f"<tr><td>{escape(str(a['application_id']))}</td><td>{escape(str(a['application_name']))}</td><td>{escape(str(a['connector_type']))}</td><td>{badge(a['risk_level'], 'risk-' + str(a['risk_level']))}</td><td>{badge(a['status'], 'status-' + str(a['status']))}</td></tr>" for a in MANAGED_SOURCES]
    form = """
    <div class='card'><h2 style='margin-top:0'>Create Source</h2><form class='form-card' method='post' action='/ui/manage/applications'>
      <label>Application ID</label><input name='application_id' required />
      <label>Application Name</label><input name='application_name' required />
      <label>Connector Type</label><select name='connector_type'><option>SCIM 2.0</option><option>REST Web Services</option><option>JDBC</option><option>OIDC JIT</option><option>Manual Feed</option></select>
      <label>Risk</label><select name='risk_level'><option>LOW</option><option>MEDIUM</option><option>HIGH</option><option>CRITICAL</option></select>
      <label>Status</label><select name='status'><option>DESIGN</option><option>ACTIVE</option><option>INACTIVE</option></select>
      <button type='submit'>Create source</button>
    </form></div>
    """
    return HTMLResponse(page_shell("Create Apps", form + table(["Source", "Name", "Connector", "Risk", "Status"], rows or ["<tr><td colspan='5'>No created sources yet.</td></tr>"]), "Create lab source onboarding records."))


@router.post("/ui/manage/applications")
def ui_create_application(request: Request, application_id: str = Form(...), application_name: str = Form(...), connector_type: str = Form(...), risk_level: str = Form(...), status: str = Form(...)) -> RedirectResponse:
    require_permission(request, "CREATE_RESOURCE_REQUEST")
    MANAGED_SOURCES.insert(0, {"application_id": application_id, "application_name": application_name, "connector_type": connector_type, "risk_level": risk_level, "status": status})
    return RedirectResponse(url="/ui/manage/applications", status_code=303)
