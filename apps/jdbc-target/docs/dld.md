# JDBC Target DLD

## Detailed design

`jdbc-target` is implemented as a local SQLite-backed data model in Milestone 1.

## Modules

```text
db/schema.sql   -> creates raw app tables
db/seed.sql     -> inserts fake sample users, roles, and assignments
db/views.sql    -> creates IAM-safe aggregation views
scripts/run-sqlite.sh -> builds local database from SQL scripts
```

## Processing flow

```text
1. Run schema.sql.
2. Create users, roles, and user_roles tables.
3. Run seed.sql.
4. Insert fake sample account and entitlement data.
5. Run views.sql.
6. Create IAM-safe views.
7. Later, iga-service reads the IAM-safe views for aggregation.
```

## Validation rules

### users

```text
employee_id required and unique
lan_id required and unique
email required and unique
account_status must be ACTIVE, INACTIVE, LOCKED, or TERMINATED
```

### roles

```text
role_code required and unique
risk_level must be LOW, MEDIUM, HIGH, or CRITICAL
role_status must be ACTIVE or INACTIVE
```

### user_roles

```text
user_id must exist
role_id must exist
assignment_status must be ACTIVE or REVOKED
same user cannot have the same role twice
```

## Error handling

Milestone 1 relies on SQLite constraint errors.

Future improvements:

```text
pre-check seed data
add validation script
produce validation report
send invalid data findings to siem-detection-service
```

## Audit behavior

The table includes assignment metadata:

```text
assigned_by
assigned_at
revoked_by
revoked_at
assignment_reason
```

Future versions may add an explicit audit table.

## Security decision points

```text
IGA reads views only.
Raw tables are not intended for IGA aggregation.
High-risk roles are marked with risk_level.
Orphan-style account data is intentionally seeded for correlation testing.
```
