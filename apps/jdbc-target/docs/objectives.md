# JDBC Target Objectives

## Service name

`jdbc-target`

## Simulated platform type

Database-backed security asset operations application.

This app represents a legacy or internal enterprise system where users, roles, and role assignments are stored in database tables.

## Primary learning objective

Learn how an IGA platform such as SailPoint aggregates accounts, entitlements, and account-entitlement assignments from a database-backed application using JDBC-style views.

## What this service teaches

```text
Account source tables
Entitlement source tables
Account-entitlement mapping
IAM-safe database views
Read-only aggregation model
Least-privilege database access
Orphan account testing
High-risk entitlement modeling
```

## Milestone 1 scope

Milestone 1 creates:

```text
users table
roles table
user_roles table
vw_iam_accounts
vw_iam_entitlements
vw_iam_account_entitlements
sample seed data
access model documentation
```

## Out of scope for Milestone 1

```text
Full web UI
REST API
Write-back provisioning
Stored procedures
Production database deployment
Real employee data
Real secrets
```

## Future scope

Later versions may add:

```text
Optional view-only admin UI
SQLite to PostgreSQL migration
Provisioning simulation
Stored procedure-based write-back
IGA aggregation script
Certification report integration
```
