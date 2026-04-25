# IGA Service UI Decision

## Decision

`iga-service` should become the first real UI later.

No full UI is implemented in Milestone 1, but IGA is the best candidate for the first meaningful user-facing interface.

## Reason

IGA is where governance actions happen:

```text
view applications
view identities
view accounts
view entitlements
view who has what access
review correlation results
request access later
approve access later
certify access later
```

## Milestone 1 UI scope

```text
No UI implementation.
Design-only UI decision.
GraphQL/data model first.
```

## Future UI screens

```text
Dashboard
Application catalog
Identities
Accounts
Entitlements
Assignments
Correlation results
Orphan accounts
High-risk access
Access requests
Approvals
Certifications
```

## Restrictions for future UI

```text
No silent provisioning.
High-risk access changes require confirmation.
Future AI suggestions must show evidence.
Approver and requester duties must be separated.
All write decisions must be audited.
```
