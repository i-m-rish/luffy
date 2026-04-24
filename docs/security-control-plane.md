# Security Control Plane

## Purpose

The security control plane adds defensive services that inspect what is going into and coming out of the Luffy IAM Lab applications.

The goal is to simulate how cybersecurity platforms check requests, responses, events, and privileged actions before allowing them to continue.

## Core idea

```text
Request comes in
      ↓
Inspect the request
      ↓
Check identity, token, payload, role, risk, and behavior
      ↓
Allow / block / rate-limit / require approval / log
      ↓
Forward to target app only if allowed
      ↓
Inspect important outbound events and responses
      ↓
Send event to detection service
```

## New components

| Service | Type | Purpose |
|---|---|---|
| `api-gateway-waf` | Inline inspection and enforcement service | Checks traffic before it reaches apps and can stop risky requests |
| `siem-detection-service` | Event monitoring and detection service | Checks events/logs across apps and raises alerts |

## Component 1: api-gateway-waf

`api-gateway-waf` is the inline control point.

It acts like a mix of:

```text
API Gateway
WAF
Policy enforcement point
Request inspection service
Traffic guard
```

It sits between callers and protected apps.

Protected apps:

```text
iga-service
scim-target
webservices-target
pam-target
```

It can also inspect sensitive calls from `iga-service` to target apps.

## What api-gateway-waf checks

### Inbound request checks

```text
Who is calling?
Which app are they calling?
Which endpoint are they calling?
Is the token present?
Is the token valid?
Is the method allowed?
Is the payload valid?
Is the request too large?
Is the user allowed to call this endpoint?
Does the payload contain suspicious input?
Is the caller sending too many requests?
Is this a high-risk action?
```

### Outbound/action checks

```text
What action is being sent to the target app?
Which user/account/role is being changed?
Is this a privileged entitlement?
Was approval completed?
Is the provisioning request coming from iga-service?
Is the same actor requesting and approving?
Is the action outside normal time?
Should this action require step-up approval?
```

## Decisions

The gateway can return these decisions:

```text
ALLOW
BLOCK
RATE_LIMIT
REQUIRE_APPROVAL
REQUIRE_STEP_UP
LOG_ONLY
```

## Examples

### Example 1: Missing token

```text
Request: POST /api/v1/users/u-1001/roles
Problem: No Authorization header
Decision: BLOCK
Reason: Missing authentication token
```

### Example 2: Suspicious payload

```text
Request: POST /api/v1/users
Problem: Payload contains script-like input
Decision: BLOCK
Reason: Suspicious input pattern
```

### Example 3: High-risk PAM access

```text
Request: POST /pam/v1/checkout-requests
Problem: User requested emergency privileged access
Decision: REQUIRE_STEP_UP
Reason: Emergency access requires additional approval
```

### Example 4: Approved provisioning

```text
Request: POST /scim/v2/Groups/{id}
Problem: No issue found
Decision: ALLOW
Reason: Approved IGA provisioning request
```

## API design

```text
POST /gateway/inspect-request
POST /gateway/inspect-action
GET  /gateway/policies
POST /gateway/policies
GET  /gateway/events
```

## Example inspection request

```json
{
  "source_service": "iga-service",
  "target_service": "pam-target",
  "actor": "RSINGH01",
  "method": "POST",
  "path": "/pam/v1/checkout-requests",
  "action_type": "PAM_CHECKOUT_REQUEST",
  "risk_level": "CRITICAL",
  "approval_status": "PENDING"
}
```

## Example inspection response

```json
{
  "decision": "REQUIRE_STEP_UP",
  "reason": "Critical PAM checkout requires additional approval",
  "event_id": "evt-1001"
}
```

## Component 2: siem-detection-service

`siem-detection-service` is the monitoring and detection layer.

It does not normally block the first request inline. Instead, it collects events and detects patterns across time and across apps.

It receives events from:

```text
idp-service
iga-service
scim-target
jdbc-target
webservices-target
pam-target
api-gateway-waf
```

## What siem-detection-service checks

```text
Repeated blocked requests
Repeated failed login attempts
High-risk role assigned without approval
PAM checkout outside business hours
Emergency access used without follow-up review
Same user requested and approved their own access
Orphan account still has active entitlement
Privileged account accessed by unmatched identity
Multiple privilege escalations in short time
Dormant account still active in target app
```

## Detection examples

```text
DET-001: Multiple failed login attempts
DET-002: High-risk entitlement assigned without required approval
DET-003: PAM checkout outside approved time window
DET-004: Orphan account has active entitlement
DET-005: Same identity requested and approved own access
DET-006: Repeated blocked API requests from same actor
DET-007: Emergency access used without follow-up review
DET-008: Critical role provisioned outside change window
```

## SIEM APIs

```text
POST /events
GET  /events
POST /detections/run
GET  /alerts
POST /alerts/{alertId}/close
```

## Updated architecture

```text
                         +----------------------+
                         |   api-gateway-waf    |
                         | Inline inspection    |
                         | Allow / block / step |
                         +----------+-----------+
                                    |
                                    v
+-------------+          +----------+----------+          +-------------------+
| idp-service |--------->|     iga-service     |<-------->| scim-target       |
+-------------+          | Governance engine   |          +-------------------+
                         | Request / approval  |<-------->| jdbc-target       |
                         | Provisioning        |          +-------------------+
                         | Certification       |<-------->| webservices-target|
                         +----------+----------+          +-------------------+
                                    |                     | pam-target        |
                                    |                     +-------------------+
                                    v
                         +----------------------+
                         | siem-detection-      |
                         | service              |
                         | Events / detections  |
                         | Alerts / audit       |
                         +----------------------+
```

## Final role of both services

```text
api-gateway-waf
  Checks what is coming in and going out.
  Can stop the action before it reaches the target app.

siem-detection-service
  Checks what happened across all apps.
  Finds suspicious patterns and creates alerts.
```

## Build recommendation

Build these after the main apps have basic functionality.

Recommended order:

```text
1. jdbc-target
2. webservices-target
3. scim-target
4. pam-target
5. idp-service
6. iga-service
7. api-gateway-waf
8. siem-detection-service
```
