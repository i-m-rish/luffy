from __future__ import annotations

from fastapi import APIRouter, Form, HTTPException

from access_model import assign_app_role, list_app_role_assignments, remove_app_role

router = APIRouter(tags=["IdP Access Provisioning"])


@router.get("/api/access/assignments")
def api_access_assignments() -> list[dict[str, object]]:
    return list_app_role_assignments()


@router.post("/api/access/assignments")
def api_assign_access(username: str = Form(...), client_id: str = Form(...), app_role: str = Form(...)) -> dict[str, object]:
    try:
        return assign_app_role(username, client_id, app_role)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/api/access/assignments")
def api_remove_access(username: str = Form(...), client_id: str = Form(...)) -> dict[str, object]:
    return remove_app_role(username, client_id)
