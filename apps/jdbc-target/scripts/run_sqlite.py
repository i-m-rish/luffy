from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

APP_DIR = Path(__file__).resolve().parents[1]
DB_FILE = APP_DIR / "jdbc-target.db"
SCHEMA_FILE = APP_DIR / "db" / "schema.sql"
SEED_FILE = APP_DIR / "db" / "seed.sql"
VIEWS_FILE = APP_DIR / "db" / "views.sql"


def execute_sql_file(connection: sqlite3.Connection, file_path: Path) -> None:
    if not file_path.exists():
        raise FileNotFoundError(f"SQL file not found: {file_path}")

    sql = file_path.read_text(encoding="utf-8")
    connection.executescript(sql)


def rebuild_database(db_file: Path = DB_FILE) -> Path:
    if db_file.exists():
        db_file.unlink()

    with sqlite3.connect(db_file) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")
        execute_sql_file(connection, SCHEMA_FILE)
        execute_sql_file(connection, SEED_FILE)
        execute_sql_file(connection, VIEWS_FILE)
        connection.commit()

    return db_file


def fetch_rows(connection: sqlite3.Connection, query: str) -> list[sqlite3.Row]:
    connection.row_factory = sqlite3.Row
    cursor = connection.execute(query)
    return cursor.fetchall()


def print_rows(title: str, rows: Iterable[sqlite3.Row]) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    for row in rows:
        print(dict(row))


def preview_database(db_file: Path = DB_FILE) -> None:
    with sqlite3.connect(db_file) as connection:
        connection.row_factory = sqlite3.Row

        print_rows(
            "IAM accounts preview",
            fetch_rows(
                connection,
                """
                SELECT account_id, employee_id, lan_id, email, account_status
                FROM vw_iam_accounts
                ORDER BY account_id;
                """,
            ),
        )

        print_rows(
            "IAM entitlements preview",
            fetch_rows(
                connection,
                """
                SELECT entitlement_id, entitlement_code, entitlement_name, risk_level
                FROM vw_iam_entitlements
                ORDER BY entitlement_id;
                """,
            ),
        )

        print_rows(
            "IAM account-entitlements preview",
            fetch_rows(
                connection,
                """
                SELECT account_id, lan_id, entitlement_code, risk_level, assignment_status
                FROM vw_iam_account_entitlements
                ORDER BY assignment_id;
                """,
            ),
        )


def main() -> None:
    db_file = rebuild_database()
    print(f"Database created: {db_file}")
    preview_database(db_file)


if __name__ == "__main__":
    main()
