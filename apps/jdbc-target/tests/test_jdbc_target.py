from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = APP_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from run_sqlite import rebuild_database  # noqa: E402


def connect(db_file: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_file)
    connection.row_factory = sqlite3.Row
    return connection


def test_database_builds_successfully(tmp_path: Path) -> None:
    db_file = tmp_path / "jdbc-target-test.db"

    result = rebuild_database(db_file)

    assert result.exists()


def test_required_tables_exist(tmp_path: Path) -> None:
    db_file = rebuild_database(tmp_path / "jdbc-target-test.db")

    with connect(db_file) as connection:
        table_names = {
            row["name"]
            for row in connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table';
                """
            )
        }

    assert {"users", "roles", "user_roles"}.issubset(table_names)


def test_required_iam_views_exist(tmp_path: Path) -> None:
    db_file = rebuild_database(tmp_path / "jdbc-target-test.db")

    with connect(db_file) as connection:
        view_names = {
            row["name"]
            for row in connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'view';
                """
            )
        }

    assert {
        "vw_iam_accounts",
        "vw_iam_entitlements",
        "vw_iam_account_entitlements",
    }.issubset(view_names)


def test_seed_data_counts(tmp_path: Path) -> None:
    db_file = rebuild_database(tmp_path / "jdbc-target-test.db")

    with connect(db_file) as connection:
        user_count = connection.execute("SELECT COUNT(*) AS count FROM users;").fetchone()["count"]
        role_count = connection.execute("SELECT COUNT(*) AS count FROM roles;").fetchone()["count"]
        assignment_count = connection.execute("SELECT COUNT(*) AS count FROM user_roles;").fetchone()["count"]

    assert user_count == 5
    assert role_count == 5
    assert assignment_count == 5


def test_iam_accounts_view_contains_expected_columns(tmp_path: Path) -> None:
    db_file = rebuild_database(tmp_path / "jdbc-target-test.db")

    with connect(db_file) as connection:
        row = connection.execute("SELECT * FROM vw_iam_accounts LIMIT 1;").fetchone()

    assert set(row.keys()) == {
        "account_id",
        "employee_id",
        "lan_id",
        "email",
        "display_name",
        "department",
        "account_status",
        "active",
        "created_at",
        "updated_at",
    }


def test_critical_entitlement_is_available_for_governance(tmp_path: Path) -> None:
    db_file = rebuild_database(tmp_path / "jdbc-target-test.db")

    with connect(db_file) as connection:
        row = connection.execute(
            """
            SELECT entitlement_code, risk_level
            FROM vw_iam_entitlements
            WHERE entitlement_code = 'SYSTEM_ADMINISTRATOR';
            """
        ).fetchone()

    assert row is not None
    assert row["risk_level"] == "CRITICAL"


def test_orphan_style_account_exists_for_correlation_testing(tmp_path: Path) -> None:
    db_file = rebuild_database(tmp_path / "jdbc-target-test.db")

    with connect(db_file) as connection:
        row = connection.execute(
            """
            SELECT employee_id, lan_id, account_status
            FROM vw_iam_accounts
            WHERE lan_id = 'ORPHAN01';
            """
        ).fetchone()

    assert row is not None
    assert row["employee_id"] == "9001"
    assert row["account_status"] == "ACTIVE"


def test_account_entitlement_assignments_include_risk_level(tmp_path: Path) -> None:
    db_file = rebuild_database(tmp_path / "jdbc-target-test.db")

    with connect(db_file) as connection:
        rows = connection.execute(
            """
            SELECT account_id, entitlement_code, risk_level, assignment_status
            FROM vw_iam_account_entitlements;
            """
        ).fetchall()

    assert len(rows) == 5
    assert all(row["risk_level"] in {"LOW", "MEDIUM", "HIGH", "CRITICAL"} for row in rows)
    assert all(row["assignment_status"] == "ACTIVE" for row in rows)
