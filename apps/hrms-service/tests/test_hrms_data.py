from __future__ import annotations

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = APP_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from validate_hrms_data import load_json, validate_all  # noqa: E402


def test_hrms_sample_data_validation_passes() -> None:
    counts = validate_all()

    assert counts == {
        "departments": 4,
        "positions": 5,
        "workers": 6,
        "lifecycle_events": 6,
    }


def test_workers_have_unique_employee_ids_and_emails() -> None:
    workers = load_json("workers.json")

    employee_ids = [worker["employee_id"] for worker in workers]
    emails = [worker["email"] for worker in workers]

    assert len(employee_ids) == len(set(employee_ids))
    assert len(emails) == len(set(emails))


def test_hrms_contains_required_lifecycle_event_types() -> None:
    lifecycle_events = load_json("lifecycle-events.json")
    event_types = {event["event_type"] for event in lifecycle_events}

    assert "JOINER" in event_types
    assert "DEPARTMENT_CHANGE" in event_types
    assert "MANAGER_CHANGE" in event_types
    assert "LEAVER" in event_types


def test_terminated_worker_has_leaver_event() -> None:
    workers = load_json("workers.json")
    lifecycle_events = load_json("lifecycle-events.json")

    terminated_employee_ids = {
        worker["employee_id"] for worker in workers if worker["employment_status"] == "TERMINATED"
    }
    leaver_employee_ids = {
        event["employee_id"] for event in lifecycle_events if event["event_type"] == "LEAVER"
    }

    assert terminated_employee_ids
    assert terminated_employee_ids.issubset(leaver_employee_ids)


def test_contractor_worker_exists_for_worker_type_governance() -> None:
    workers = load_json("workers.json")

    contractors = [worker for worker in workers if worker["worker_type"] == "CONTRACTOR"]

    assert len(contractors) == 1
    assert contractors[0]["employment_status"] == "ACTIVE"


def test_workers_reference_valid_departments_and_positions() -> None:
    workers = load_json("workers.json")
    departments = load_json("departments.json")
    positions = load_json("positions.json")

    department_ids = {department["department_id"] for department in departments}
    position_ids = {position["position_id"] for position in positions}

    assert all(worker["department_id"] in department_ids for worker in workers)
    assert all(worker["position_id"] in position_ids for worker in workers)


def test_critical_position_exists_for_high_risk_access_governance() -> None:
    positions = load_json("positions.json")

    critical_positions = [position for position in positions if position["risk_category"] == "CRITICAL"]

    assert len(critical_positions) == 1
    assert critical_positions[0]["position_id"] == "POS-SEC-ADMIN"
