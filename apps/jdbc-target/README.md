# JDBC Target

## Purpose

`jdbc-target` simulates a database-backed security asset operations application.

It represents the type of legacy/internal application where an IGA platform such as SailPoint aggregates accounts, entitlements, and assignments using JDBC or database views.

## Integration pattern

```text
Integration type: JDBC / database aggregation
Primary data store: SQL database
IGA read path: IAM-safe database views
UI in milestone 1: No
```

## Why database-first

This service is database-first because the learning goal is to understand how application access is represented in database tables and exposed to IGA through controlled views.

The first milestone focuses on:

```text
users
roles
user_roles
vw_iam_accounts
vw_iam_entitlements
vw_iam_account_entitlements
```

## Folder structure

```text
apps/jdbc-target/
├── README.md
├── db/
│   ├── schema.sql
│   ├── seed.sql
│   └── views.sql
├── docs/
│   └── access-model.md
└── scripts/
    └── run-sqlite.sh
```

## Security model

The IGA service should not read raw transactional tables directly.

It should read only these IAM-safe views:

```text
vw_iam_accounts
vw_iam_entitlements
vw_iam_account_entitlements
```

## Sample app roles

```text
Asset Viewer
Asset Owner
Remediation Manager
Compliance Reviewer
System Administrator
```

## How this maps to SailPoint

| JDBC target object | IGA/SailPoint concept |
|---|---|
| `users` | Account source table |
| `roles` | Entitlement source table |
| `user_roles` | Account-entitlement assignment table |
| `vw_iam_accounts` | Account aggregation view |
| `vw_iam_entitlements` | Entitlement aggregation view |
| `vw_iam_account_entitlements` | Account-entitlement aggregation view |

## Run locally with SQLite

From the repository root:

```bash
cd apps/jdbc-target
bash scripts/run-sqlite.sh
```

This creates a local SQLite database at:

```text
apps/jdbc-target/jdbc-target.db
```

## UI decision

No full UI is needed in Milestone 1.

A view-only admin UI may be added later to display:

```text
Users
Roles
User-role assignments
IAM aggregation views
```
