from __future__ import annotations

from html import escape

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from auth import require_permission, require_ui_permission
from ui.components import badge, page_shell, table

router = APIRouter(tags=["IGA Sandbox"])

SANDBOX_CHANGES: list[dict[str, object]] = []
PROMOTED_CHANGES: list[dict[str, object]] = []


def validate_change(change_type: str, target: str, risk_level: str, summary: str) -> list[str]:
    findings: list[str] = []
    if not target.strip():
        findings.append("Target object is required.")
    if not summary.strip():
        findings.append("Summary is required.")
    if risk_level in {"HIGH", "CRITICAL"}:
        findings.append("High-risk change requires approval and certification impact review.")
    if change_type == "SOURCE_ONBOARDING":
        findings.append("Validate connector type, authentication method, account schema, entitlement schema, and correlation rule before promotion.")
    if change_type == "ACCESS_MODEL_CHANGE":
        findings.append("Review affected entitlements, owners, requestability, and existing assignments before promotion.")
    if change_type == "SOD_POLICY_CHANGE":
        findings.append("Run SOD simulation and review violation population before promotion.")
    if change_type == "CERTIFICATION_CHANGE":
        findings.append("Validate campaign scope, reviewer population, exclusion logic, and due dates before activation.")
    if not findings:
        findings.append("Sandbox validation passed with no blocking finding.")
    return findings


def rows_for(changes: list[dict[str, object]], include_promote: bool) -> list[str]:
    rows: list[str] = []
    for change in changes:
        promote_form = ""
        if include_promote:
            promote_form = (
                "<form method='post' action='/ui/sandbox/promote'>"
                f"<input type='hidden' name='change_id' value='{escape(str(change['change_id']))}' />"
                "<button type='submit'>Promote</button></form>"
            )
        findings = "<br />".join(escape(str(item)) for item in change.get("findings", []))
        rows.append(
            "<tr>"
            f"<td>{escape(str(change['change_id']))}</td>"
            f"<td>{escape(str(change['change_type']))}</td>"
            f"<td>{escape(str(change['target']))}</td>"
            f"<td>{badge(change['risk_level'], 'risk-' + str(change['risk_level']))}</td>"
            f"<td>{badge(change['status'], 'status-' + str(change['status']))}</td>"
            f"<td>{findings}</td>"
            f"<td>{promote_form}</td>"
            "</tr>"
        )
    return rows


@router.get("/ui/sandbox", response_class=HTMLResponse, response_model=None)
def ui_sandbox(request: Request) -> Response:
    result = require_ui_permission(request, "CREATE_RESOURCE_REQUEST")
    if isinstance(result, RedirectResponse):
        return result
    form = """
    <div class='card'>
      <h2 style='margin-top:0'>Create Sandbox Change Set</h2>
      <form class='form-card' method='post' action='/ui/sandbox'>
        <label>Change Type</label>
        <select name='change_type'>
          <option>SOURCE_ONBOARDING</option>
          <option>ACCESS_MODEL_CHANGE</option>
          <option>SOD_POLICY_CHANGE</option>
          <option>GOVERNANCE_POLICY_CHANGE</option>
          <option>CERTIFICATION_CHANGE</option>
          <option>IDP_APP_REGISTRATION_CHANGE</option>
        </select>
        <label>Target Object</label><input name='target' required placeholder='Example: zsp-jit-app or IGA-ENT-ZSP-ADMIN' />
        <label>Risk Level</label><select name='risk_level'><option>LOW</option><option>MEDIUM</option><option>HIGH</option><option>CRITICAL</option></select>
        <label>Summary</label><textarea name='summary' required placeholder='What is changing and why?'></textarea>
        <button type='submit'>Create and validate in sandbox</button>
      </form>
    </div>
    """
    draft_rows = rows_for(SANDBOX_CHANGES, include_promote=True)
    promoted_rows = rows_for(PROMOTED_CHANGES, include_promote=False)
    body = form
    body += "<h2 class='section-title'>Draft / Sandbox Changes</h2>"
    body += table(["Change", "Type", "Target", "Risk", "Status", "Validation Findings", "Action"], draft_rows or ["<tr><td colspan='7'>No sandbox changes yet.</td></tr>"])
    body += "<h2 class='section-title'>Promoted to Main</h2>"
    body += table(["Change", "Type", "Target", "Risk", "Status", "Validation Findings", "Action"], promoted_rows or ["<tr><td colspan='7'>No promoted changes yet.</td></tr>"])
    return HTMLResponse(page_shell("Sandbox / Change Sets", body, "Draft, validate, and promote IGA changes before they become active."))


@router.post("/ui/sandbox")
def ui_create_change(request: Request, change_type: str = Form(...), target: str = Form(...), risk_level: str = Form(...), summary: str = Form(...)) -> RedirectResponse:
    require_permission(request, "CREATE_RESOURCE_REQUEST")
    findings = validate_change(change_type, target, risk_level, summary)
    change = {
        "change_id": f"IGA-CS-{len(SANDBOX_CHANGES) + len(PROMOTED_CHANGES) + 1:04d}",
        "change_type": change_type,
        "target": target,
        "risk_level": risk_level,
        "summary": summary,
        "status": "VALIDATED_WITH_WARNINGS" if risk_level in {"HIGH", "CRITICAL"} else "VALIDATED",
        "findings": findings,
    }
    SANDBOX_CHANGES.insert(0, change)
    return RedirectResponse(url="/ui/sandbox", status_code=303)


@router.post("/ui/sandbox/promote")
def ui_promote_change(request: Request, change_id: str = Form(...)) -> RedirectResponse:
    require_permission(request, "CREATE_RESOURCE_REQUEST")
    for change in list(SANDBOX_CHANGES):
        if change["change_id"] == change_id:
            SANDBOX_CHANGES.remove(change)
            change["status"] = "PROMOTED_TO_MAIN"
            PROMOTED_CHANGES.insert(0, change)
            break
    return RedirectResponse(url="/ui/sandbox", status_code=303)


@router.get("/api/sandbox/changes")
def api_sandbox_changes(request: Request) -> dict[str, object]:
    require_permission(request, "CREATE_RESOURCE_REQUEST")
    return {"sandbox_changes": SANDBOX_CHANGES, "promoted_changes": PROMOTED_CHANGES}


@router.post("/api/sandbox/changes")
def api_create_sandbox_change(request: Request, change_type: str = Form(...), target: str = Form(...), risk_level: str = Form(...), summary: str = Form(...)) -> dict[str, object]:
    require_permission(request, "CREATE_RESOURCE_REQUEST")
    change = {
        "change_id": f"IGA-CS-{len(SANDBOX_CHANGES) + len(PROMOTED_CHANGES) + 1:04d}",
        "change_type": change_type,
        "target": target,
        "risk_level": risk_level,
        "summary": summary,
        "status": "VALIDATED_WITH_WARNINGS" if risk_level in {"HIGH", "CRITICAL"} else "VALIDATED",
        "findings": validate_change(change_type, target, risk_level, summary),
    }
    SANDBOX_CHANGES.insert(0, change)
    return change
