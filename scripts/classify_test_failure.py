from __future__ import annotations

import argparse
from pathlib import Path

FAILURE_PATTERNS: list[tuple[str, str, str]] = [
    (
        "IMPORT_ERROR",
        "importerror",
        "Python could not import a module. Check renamed files, sys.path, package paths, and duplicate module names.",
    ),
    (
        "MODULE_NOT_FOUND",
        "modulenotfounderror",
        "A module is missing or the import path is wrong. Check script names and test imports.",
    ),
    (
        "PYTEST_IMPORT_MISMATCH",
        "import file mismatch",
        "Pytest imported a module with the same name from a different folder. Rename duplicate modules or use packages.",
    ),
    (
        "ASSERTION_FAILURE",
        "assertionerror",
        "A test assertion failed. Check expected counts, expected values, or relationship assumptions.",
    ),
    (
        "FILE_NOT_FOUND",
        "filenotfounderror",
        "A required file is missing. Check data file paths, script paths, or renamed files.",
    ),
    (
        "JSON_ERROR",
        "jsondecodeerror",
        "A JSON file is malformed. Check commas, brackets, quotes, and null/boolean values.",
    ),
    (
        "VALUE_ERROR",
        "valueerror",
        "Validation failed. Check allowed values, required fields, duplicate IDs, and references.",
    ),
    (
        "SQLITE_ERROR",
        "sqlite3.",
        "SQLite failed. Check SQL syntax, constraints, seed data, views, or file paths.",
    ),
    (
        "COLLECTION_ERROR",
        "error collecting",
        "Pytest failed while discovering tests. Check import errors, syntax errors, or duplicate module names.",
    ),
    (
        "SYNTAX_ERROR",
        "syntaxerror",
        "Python syntax is invalid. Check the file and line number shown above.",
    ),
]


def classify(log_text: str) -> list[tuple[str, str]]:
    normalized = log_text.lower()
    matches: list[tuple[str, str]] = []

    for failure_type, pattern, explanation in FAILURE_PATTERNS:
        if pattern in normalized:
            matches.append((failure_type, explanation))

    if not matches:
        matches.append(
            (
                "UNKNOWN_FAILURE",
                "No known failure pattern matched. Read the pytest output above and add a new pattern if needed.",
            )
        )

    return matches


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify pytest failure logs for easier CI debugging.")
    parser.add_argument("log_file", help="Path to pytest log file")
    parser.add_argument("--suite", default="unknown", help="Name of the test suite")
    args = parser.parse_args()

    log_path = Path(args.log_file)
    if not log_path.exists():
        print(f"::error::Failure log not found: {log_path}")
        raise SystemExit(1)

    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    matches = classify(log_text)

    print("")
    print("==============================")
    print(f"Failure classification: {args.suite}")
    print("==============================")

    for failure_type, explanation in matches:
        print(f"::error title={failure_type}::{explanation}")
        print(f"- {failure_type}: {explanation}")

    print("")
    print("Next debug steps:")
    print("1. Open the failing service section above in the GitHub Actions log.")
    print("2. Check the first traceback, not only the final summary.")
    print("3. Fix the root file/import/data issue, then rerun the same service test locally.")


if __name__ == "__main__":
    main()
