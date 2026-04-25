# JDBC Target Audit Events

## Milestone 1 audit model

Milestone 1 does not implement a runtime audit table.

However, assignment history fields are modeled in `user_roles`:

```text
assigned_by
assigned_at
revoked_by
revoked_at
assignment_reason
```

## Future audit events

Future versions can add explicit audit events.

Recommended event types:

```text
USER_CREATED
USER_STATUS_CHANGED
ROLE_CREATED
ROLE_STATUS_CHANGED
ROLE_ASSIGNED
ROLE_REVOKED
IAM_VIEW_READ
IGA_AGGREGATION_STARTED
IGA_AGGREGATION_COMPLETED
IGA_AGGREGATION_FAILED
```

## Audit event fields

```text
event_id
actor
source_service
target_service
action
target_resource_type
target_resource_id
decision
reason
risk_level
request_id
timestamp
```

## Events to send to SIEM later

```text
Critical role assignment
Role revoked
Inactive account with active role
Orphan account detected
IGA aggregation failure
```
