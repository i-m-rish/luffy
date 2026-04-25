from __future__ import annotations

import json
from pathlib import Path
from typing import Any

APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"

WORKER_TYPES = {"EMPLOYEE", "CONTRACTOR", "SERVICE", "INTERN"}
EMPLOYMENT_STATUSES = {"ACTIVE", "INACTIVE", "TERMINATED", "ON_LEAVE"}
DEPARTMENT_STATUSES = {"ACTIVE", "INACTIVE"}
POSITION_STATUSES = {"ACTIVE", "INACTIVE"}
RISK_CATEGORIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
LIFECYCLE_EVENT_TYPES = {
    "JOINER",
    "MOVER",
    "LEAVER",
    "MANAGER_CHANGE",
    "DEPARTMENT_CHANGE",
    "LOCATION_CHANGE",
    "WORKER_TYPE_CHANGE",
    "REHIRE",
    "TERMINATION_RESCIND",
}
LIFECYCLE_EVENT_STATUSES = {"PENDING", "PROCESSED", "CANCELLED", "FAILED"}


def load_json(file_name: str) -> list[dict[str, Any]]:
    file_path = DATA_DIR / file_name
    if not file_path.exists():
        raise FileNotFoundError(f"Missing HRMS data file: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(f"Expected list in {file_name}")

    return data


def require_fields(record: dict[str, Any], fields: set[str], record_type: str) -> None:
    missing = fields - record.keys()
    if missing:
        raise ValueError(f"{record_type} missing required fields: {sorted(missing)}")


def ensure_unique(records: list[dict[str, Any]], field: str, record_type: str) -> None:
    values = [record.get(field) for record in records]
    duplicates = {value for value in values if values.count(value) > 1}
    if duplicates:
        raise ValueError(f"Duplicate {field} values in {record_type}: {sorted(duplicates)}")


def validate_departments(departments: list[dict[str, Any]]) -> None:
    required = {"department_id", "department_name", "department_owner_employee_id", "cost_center", "status"}
    for department in departments:
        require_fields(department, required, "department")
        if department["status"] not in DEPARTMENT_STATUSES:
            raise ValueError(f"Invalid department status: {department['status']}")

    ensure_unique(departments, "department_id", "departments")


def validate_positions(positions: list[dict[str, Any]]) -> None:
    required = {"position_id", "job_title", "job_family", "risk_category", "status"}
    for position in positions:
        require_fields(position, required, "position")
        if position["risk_category"] not in RISK_CATEGORIES:
            raise ValueError(f"Invalid position risk_category: {position['risk_category']}")
        if position["status"] not in POSITION_STATUSES:
            raise ValueError(f"Invalid position status: {position['status']}")

    ensure_unique(positions, "position_id", "positions")


def validate_workers(
    workers: list[dict[str, Any]],
    departments: list[dict[str, Any]],
    positions: list[dict[str, Any]],
) -> None:
    required = {
        "worker_id",
        "employee_id",
        "first_name",
        "last_name",
        "display_name",
        "email",
        "worker_type",
        "employment_status",
        "department_id",
        "position_id",
        "manager_employee_id",
        "location",
        "start_date",
        "termination_date",
        "last_updated_at",
    }
    department_ids = {department["department_id"] for department in departments}
    position_ids = {position["position_id"] for position in positions}

    for worker in workers:
        require_fields(worker, required, "worker")
        if worker["worker_type"] not in WORKER_TYPES:
            raise ValueError(f"Invalid worker_type: {worker['worker_type']}")
        if worker["employment_status"] not in EMPLOYMENT_STATUSES:
            raise ValueError(f"Invalid employment_status: {worker['employment_status']}")
        if worker["department_id"] not in department_ids:
            raise ValueError(f"Unknown department_id on worker: {worker['department_id']}")
        if worker["position_id"] not in position_ids:
            raise ValueError(f"Unknown position_id on worker: {worker['position_id']}")
        if worker["employment_status"] == "TERMINATED" and not worker["termination_date"]:
            raise ValueError(f"Terminated worker missing termination_date: {worker['employee_id']}")

    ensure_unique(workers, "worker_id", "workers")
    ensure_unique(workers, "employee_id", "workers")
    ensure_unique(workers, "email", "workers")


def validate_lifecycle_events(
    lifecycle_events: list[dict[str, Any]],
    workers: list[dict[str, Any]],
) -> None:
    required = {
        "event_id",
        "employee_id",
        "event_type",
        "effective_date",
        "old_value",
        "new_value",
        "status",
        "created_at",
    }
    employee_ids = {worker["employee_id"] for worker in workers}

    for event in lifecycle_events:
        require_fields(event, required, "lifecycle_event")
        if event["employee_id"] not in employee_ids:
            raise ValueError(f"Lifecycle event references unknown employee_id: {event['employee_id']}")
        if event["event_type"] not in LIFECYCLE_EVENT_TYPES:
            raise ValueError(f"Invalid lifecycle event type: {event['event_type']}")
        if event["status"] not in LIFECYCLE_EVENT_STATUSES:
            raise ValueError(f"Invalid lifecycle event status: {event['status']}")

    ensure_unique(lifecycle_events, "event_id", "lifecycle_events")


def validate_all() -> dict[str, int]:
    departments = load_json("departments.json")
    positions = load_json("positions.json")
    workers = load_json("workers.json")
    lifecycle_events = load_json("lifecycle-events.json")

    validate_departments(departments)
    validate_positions(positions)
    validate_workers(workers, departments, positions)
    validate_lifecycle_events(lifecycle_events, workers)

    return {
        "departments": len(departments),
        "positions": len(positions),
        "workers": len(workers),
        "lifecycle_events": len(lifecycle_events),
    }


def main() -> None:
    counts = validate_all()
    print("HRMS sample data validation passed")
    for name, count in counts.items():
        print(f"{name}: {count}")


if __name__ == "__main__":
    main()
