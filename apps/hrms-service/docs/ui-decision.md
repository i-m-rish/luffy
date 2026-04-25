# HRMS Service UI Decision

## Decision

No full UI in Milestone 1.

## Reason

`hrms-service` is currently a lifecycle data source.

The first milestone should focus on:

```text
worker data model
department data model
position data model
lifecycle event model
sample data
identity lifecycle flow
```

## Optional future UI

A minimal HR admin UI may be added later.

Possible screens:

```text
Workers
Departments
Positions
Lifecycle events
Joiner event simulation
Mover event simulation
Leaver event simulation
```

## Restrictions for future UI

```text
Fake/sample data only.
No salary or sensitive HR fields.
Write actions must be audited.
Leaver and rehire actions require confirmation.
High-impact events should be visible to IGA/SIEM later.
```
