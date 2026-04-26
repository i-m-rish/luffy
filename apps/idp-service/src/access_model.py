from __future__ import annotations

from typing import Any

APP_CLIENTS: dict[str, dict[str, Any]] = {
    "luffy-iga": {
        "client_name": "Luffy IGA Service",
        "redirect_uri": "http://127.0.0.1:8001/auth/callback",
        "allowed_app_roles": ["IGA_ADMIN", "ACCESS_REVIEWER", "APP_OWNER", "READ_ONLY"],
    },
    "luffy-zsp": {
        "client_name": "Luffy ZSP Secure Operations Portal",
        "redirect_uri": "http://127.0.0.1:8003/auth/callback",
        "allowed_app_roles": ["ZSP_ADMIN", "ZSP_APPROVER", "ZSP_OPERATOR", "ZSP_VIEWER"],
    },
}

APP_ROLE_ASSIGNMENTS: dict[str, dict[str, str]] = {
    "admin": {"luffy-zsp": "ZSP_ADMIN"},
    "reviewer": {"luffy-zsp": "ZSP_APPROVER"},
    "owner": {"luffy-zsp": "ZSP_OPERATOR"},
    "reader": {"luffy-zsp": "ZSP_VIEWER"},
}


def get_client(client_id: str) -> dict[str, Any] | None:
    return APP_CLIENTS.get(client_id)


def assign_app_role(username: str, client_id: str, app_role: str) -> dict[str, Any]:
    client = APP_CLIENTS.get(client_id)
    if client is None:
        raise ValueError(f"Unknown client: {client_id}")
    if app_role not in client["allowed_app_roles"]:
        raise ValueError(f"Role {app_role} is not valid for {client_id}")
    APP_ROLE_ASSIGNMENTS.setdefault(username, {})[client_id] = app_role
    return {"username": username, "client_id": client_id, "app_role": app_role, "status": "ASSIGNED"}


def remove_app_role(username: str, client_id: str) -> dict[str, Any]:
    APP_ROLE_ASSIGNMENTS.setdefault(username, {}).pop(client_id, None)
    return {"username": username, "client_id": client_id, "status": "REMOVED"}


def get_app_roles(username: str) -> dict[str, str]:
    return dict(APP_ROLE_ASSIGNMENTS.get(username, {}))


def list_app_role_assignments() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for username, assignments in APP_ROLE_ASSIGNMENTS.items():
        for client_id, app_role in assignments.items():
            client = APP_CLIENTS.get(client_id, {})
            rows.append(
                {
                    "username": username,
                    "client_id": client_id,
                    "client_name": client.get("client_name", client_id),
                    "app_role": app_role,
                }
            )
    return rows
