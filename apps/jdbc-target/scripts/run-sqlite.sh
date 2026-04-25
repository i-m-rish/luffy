#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
DB_FILE="${APP_DIR}/jdbc-target.db"

SCHEMA_FILE="${APP_DIR}/db/schema.sql"
SEED_FILE="${APP_DIR}/db/seed.sql"
VIEWS_FILE="${APP_DIR}/db/views.sql"

if ! command -v sqlite3 >/dev/null 2>&1; then
  echo "sqlite3 is required but not installed."
  echo "Install SQLite first, then run this script again."
  exit 1
fi

echo "Rebuilding JDBC target database..."
rm -f "${DB_FILE}"

sqlite3 "${DB_FILE}" < "${SCHEMA_FILE}"
sqlite3 "${DB_FILE}" < "${SEED_FILE}"
sqlite3 "${DB_FILE}" < "${VIEWS_FILE}"

echo "Database created: ${DB_FILE}"
echo ""
echo "IAM accounts preview:"
sqlite3 -header -column "${DB_FILE}" "SELECT account_id, employee_id, lan_id, email, account_status FROM vw_iam_accounts;"

echo ""
echo "IAM entitlements preview:"
sqlite3 -header -column "${DB_FILE}" "SELECT entitlement_id, entitlement_code, entitlement_name, risk_level FROM vw_iam_entitlements;"

echo ""
echo "IAM account-entitlements preview:"
sqlite3 -header -column "${DB_FILE}" "SELECT account_id, lan_id, entitlement_code, risk_level, assignment_status FROM vw_iam_account_entitlements;"
