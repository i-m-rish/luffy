# IdP Service UI Decision

## Decision

No full UI in Milestone 1.

## Reason

`idp-service` is currently focused on identity, group, app registration, machine identity, and GraphQL model design.

The first milestone should focus on:

```text
identity model
group model
app registration model
machine identity model
GraphQL contract
sample data
validation tests
```

## Optional future UI

A minimal IdP admin UI may be added later.

Possible screens:

```text
Identities
Groups
Group memberships
Application registrations
App assignments
Machine identities
Login/token simulation view
```

## Restrictions for future UI

```text
No real passwords.
No real tokens.
No real secrets.
No real certificates.
Write actions must be audited.
Admin actions require authorization later.
High-risk group/app changes require explicit confirmation.
```
