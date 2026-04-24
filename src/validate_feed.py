import csv
from collections import Counter
from pathlib import Path

REQUIRED_COLUMNS = [
    "employee_id",
    "lan_id",
    "email",
    "account_name",
    "entitlement",
    "application_name",
    "owner",
]


def read_csv(file_path):
    with open(file_path, mode="r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader), reader.fieldnames or []


def check_required_columns(headers):
    return [column for column in REQUIRED_COLUMNS if column not in headers]


def check_missing_values(rows):
    issues = []
    for index, row in enumerate(rows, start=2):
        for column in REQUIRED_COLUMNS:
            if not row.get(column, "").strip():
                issues.append({
                    "row": index,
                    "column": column,
                    "issue": "Missing required value",
                })
    return issues


def check_duplicate_accounts(rows):
    account_keys = [
        (row.get("application_name", "").strip().lower(), row.get("account_name", "").strip().lower())
        for row in rows
        if row.get("application_name", "").strip() and row.get("account_name", "").strip()
    ]
    counts = Counter(account_keys)
    return [key for key, count in counts.items() if count > 1]


def check_account_name_casing(rows):
    issues = []
    for index, row in enumerate(rows, start=2):
        account_name = row.get("account_name", "").strip()
        if account_name and account_name != account_name.upper():
            issues.append({
                "row": index,
                "account_name": account_name,
                "issue": "Account name is not uppercase",
            })
    return issues


def calculate_score(missing_columns, missing_values, duplicate_accounts, casing_issues, total_rows):
    score = 100
    score -= len(missing_columns) * 20
    score -= len(missing_values) * 5
    score -= len(duplicate_accounts) * 10
    score -= len(casing_issues) * 3
    if total_rows == 0:
        score = 0
    return max(score, 0)


def generate_report(file_path, output_path):
    rows, headers = read_csv(file_path)

    missing_columns = check_required_columns(headers)
    missing_values = check_missing_values(rows)
    duplicate_accounts = check_duplicate_accounts(rows)
    casing_issues = check_account_name_casing(rows)
    score = calculate_score(
        missing_columns,
        missing_values,
        duplicate_accounts,
        casing_issues,
        len(rows),
    )

    report = []
    report.append("# IAM Access Feed Validation Report\n")
    report.append(f"Input file: `{file_path}`\n")
    report.append(f"Total rows reviewed: **{len(rows)}**\n")
    report.append(f"Feed quality score: **{score}/100**\n")

    report.append("## Missing required columns\n")
    if missing_columns:
        for column in missing_columns:
            report.append(f"- `{column}`")
    else:
        report.append("- None")

    report.append("\n## Missing required values\n")
    if missing_values:
        for issue in missing_values:
            report.append(f"- Row {issue['row']}: `{issue['column']}` is missing")
    else:
        report.append("- None")

    report.append("\n## Duplicate account entries\n")
    if duplicate_accounts:
        for application_name, account_name in duplicate_accounts:
            report.append(f"- Application `{application_name}`, account `{account_name}` appears multiple times")
    else:
        report.append("- None")

    report.append("\n## Account name casing issues\n")
    if casing_issues:
        for issue in casing_issues:
            report.append(f"- Row {issue['row']}: `{issue['account_name']}` should be uppercase")
    else:
        report.append("- None")

    report.append("\n## Suggested questions for app team\n")
    report.append("- Can you confirm the authoritative account identifier for correlation: LAN ID, email, or application account name?")
    report.append("- Can you confirm whether account names will always be sent in the same format and casing?")
    report.append("- Can you confirm the complete list of application entitlements and their business descriptions?")
    report.append("- Can you confirm the owner responsible for feed accuracy and remediation?")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(report), encoding="utf-8")
    return output_path


if __name__ == "__main__":
    input_file = Path("sample-data/access-feed-sample.csv")
    output_file = Path("reports/access-feed-validation-report.md")
    report_path = generate_report(input_file, output_file)
    print(f"Report generated: {report_path}")
