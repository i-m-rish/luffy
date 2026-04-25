# IdP Service Audit Events

## Milestone 1 audit model

Milestone 1 defines audit requirements but does not implement runtime audit storage yet.

## Future audit event types

```text
IDENTITY_CREATED
IDENTITY_UPDATED
IDENTITY_DISABLED
GROUP_CREATED
GROUP_UPDATED
GROUP_MEMBERSHIP_ADDED
GROUP_MEMBERSHIP_REMOVED
APP_REGISTERED
APP_DISABLED
APP_ASSIGNMENT_CREATED
APP_ASSIGNMENT_REMOVED
MACHINE_IDENTITY_CREATED
MACHINE_IDENTITY_UPDATED
MACHINE_IDENTITY_ROTATION_STATUS_CHANGED
LOGIN_SUCCESS
LOGIN_FAILED
TOKEN_ISSUED
```

## Audit event fields

```text
event_id
actor
source_service
target_resource_type
target_resource_id
action
decision
reason
risk_level
request_id
timestamp
```

## High-risk audit events

```text
ADMIN group membership added
APP assignment changed for high-risk app
MACHINE_IDENTITY status changed
MACHINE_IDENTITY rotation overdue
LOGIN_FAILED spike later
IDENTITY_DISABLED
```

## Events to send to SIEM later

```text
Repeated failed login
Admin group change
High-risk app assignment
Machine identity owner missing
Machine identity rotation overdue
Disabled identity still has app assignment
```
