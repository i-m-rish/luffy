# JDBC Target UI Decision

## Decision

No full UI in Milestone 1.

## Reason

`jdbc-target` is meant to teach database/JDBC-style integration.

The first milestone should focus on:

```text
Database schema
Seed data
IAM-safe views
Access model
Aggregation readiness
```

## Optional future UI

A small view-only UI may be added later.

Possible screens:

```text
Users
Roles
User-role assignments
IAM accounts view
IAM entitlements view
IAM account-entitlements view
```

## Restrictions for future UI

```text
Read-only by default.
No direct production-style admin actions.
No secrets.
No real personal data.
Any write action must be audited.
```
