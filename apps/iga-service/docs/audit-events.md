# IGA Service Audit Events

## Milestone 1 audit model

Milestone 1 defines audit requirements but does not implement runtime audit storage yet.

## Future audit event types

```text
APPLICATION_ONBOARDED
AGGREGATION_STARTED
AGGREGATION_COMPLETED
AGGREGATION_FAILED
IDENTITY_NORMALIZED
ACCOUNT_NORMALIZED
ENTITLEMENT_NORMALIZED
ASSIGNMENT_NORMALIZED
CORRELATION_MATCHED
CORRELATION_PARTIAL
CORRELATION_ORPHAN
ACCESS_REQUEST_CREATED
ACCESS_REQUEST_APPROVED
ACCESS_REQUEST_REJECTED
PROVISIONING_TRIGGERED
CERTIFICATION_DECISION_SUBMITTED
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
orphan account detected
critical entitlement assignment detected
terminated identity with active account detected
access request approved for critical entitlement
provisioning triggered
certification revoke decision submitted
```

## Events to send to SIEM later

```text
Correlation orphan
High-risk assignment
Aggregation failure
Terminated identity active account
Provisioning failure
Certification overdue
```
