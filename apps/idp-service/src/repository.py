from __future__ import annotations

import json
from pathlib import Path
from typing import Any

APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"


def load_json(file_name: str) -> list[dict[str, Any]]:
    file_path = DATA_DIR / file_name
    if not file_path.exists():
        raise FileNotFoundError(f"Missing IdP data file: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(f"Expected list in {file_name}")

    return data


def find_by_id(records: list[dict[str, Any]], key: str, value: str) -> dict[str, Any] | None:
    return next((record for record in records if record.get(key) == value), None)


def get_identities() -> list[dict[str, Any]]:
    return load_json("identities.json")


def get_groups() -> list[dict[str, Any]]:
    return load_json("groups.json")


def get_group_memberships() -> list[dict[str, Any]]:
    return load_json("group-memberships.json")


def get_app_registrations() -> list[dict[str, Any]]:
    return load_json("app-registrations.json")


def get_app_assignments() -> list[dict[str, Any]]:
    return load_json("app-assignments.json")


def get_machine_identities() -> list[dict[str, Any]]:
    return load_json("machine-identities.json")


def get_identity_profile(identity_id: str) -> dict[str, Any] | None:
    identities = get_identities()
    groups = get_groups()
    memberships = get_group_memberships()
    app_registrations = get_app_registrations()
    app_assignments = get_app_assignments()

    identity = find_by_id(identities, "identity_id", identity_id)
    if identity is None:
        return None

    identity_memberships = [
        membership for membership in memberships if membership["identity_id"] == identity_id
    ]
    identity_group_ids = {membership["group_id"] for membership in identity_memberships}
    identity_groups = [group for group in groups if group["group_id"] in identity_group_ids]

    login_apps: list[dict[str, Any]] = []
    for assignment in app_assignments:
        if assignment["group_id"] not in identity_group_ids:
            continue
        app = find_by_id(
            app_registrations,
            "app_registration_id",
            assignment["app_registration_id"],
        )
        if app is not None:
            login_apps.append({"app_registration": app, "assignment": assignment})

    return {
        "identity": identity,
        "groups": identity_groups,
        "login_applications": login_apps,
    }


def get_dashboard() -> dict[str, Any]:
    identities = get_identities()
    groups = get_groups()
    apps = get_app_registrations()
    machines = get_machine_identities()

    return {
        "identity_count": len(identities),
        "active_identity_count": len(
            [identity for identity in identities if identity["identity_status"] == "ACTIVE"]
        ),
        "disabled_identity_count": len(
            [identity for identity in identities if identity["identity_status"] == "DISABLED"]
        ),
        "group_count": len(groups),
        "app_registration_count": len(apps),
        "machine_identity_count": len(machines),
        "high_risk_group_count": len(
            [group for group in groups if group["risk_level"] in {"HIGH", "CRITICAL"}]
        ),
        "overdue_machine_identity_count": len(
            [machine for machine in machines if machine["rotation_status"] == "OVERDUE"]
        ),
    }
