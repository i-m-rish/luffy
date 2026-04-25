# HRMS Service Audit Events

## Milestone 1 audit model

Milestone 1 defines audit requirements but does not implement a runtime audit table yet.

## Future audit event types

```text
WORKER_CREATED
WORKER_UPDATED
WORKER_TERMINATED
WORKER_REHIRED
DEPARTMENT_CHANGED
MANAGER_CHANGED
POSITION_CHANGED
WORKER_TYPE_CHANGED
LIFECYCLE_EVENT_CREATED
LIFECYCLE_EVENT_PROCESSED
LIFECYCLE_EVENT_FAILED
```

## Audit event fields

```text
event_id
actor
source_service
target_resource_type
target_resource_id
action
old_value
new_value
decision
reason
risk_level
request_id
timestamp
```

## High-risk audit events

These should be treated as high-risk:

```text
WORKER_TERMINATED
WORKER_REHIRED
WORKER_TYPE_CHANGED
MANAGER_CHANGED
LIFECYCLE_EVENT_FAILED
```

## Events to send to SIEM later

```text
Worker terminated
Worker rehired
Manager changed
Worker type changed
Lifecycle event failed
Terminated worker still active in IdP/IGA later
```
