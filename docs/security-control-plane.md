# API Security Control Plane

## Purpose

The API security control plane checks whether API security is implemented correctly across the Luffy IAM Lab.

It is mainly an inspection and security posture layer. It usually observes, validates, and reports. It can also enforce controls when configured to do so through allowlists, blocklists, or policy rules.

## Core idea

Every protected app should support two routing modes:

```text
DIRECT_MODE
  Caller -> Target app

GATEWAY_MODE
  Caller -> api-gateway-waf -> Target app
```

This allows the lab to compare:

```text
What happens when traffic goes directly to the app?
What happens when traffic is inspected by the API security layer first?
```

## New components

| Service | Type | Purpose |
|---|---|---|
| `api-gateway-waf` | API security inspection and optional enforcement layer | Checks API requests/responses and can allow, log, warn, rate-limit, or block |
| `siem-detection-service` | Event monitoring and detection layer | Collects events from all services and finds suspicious patterns |

## Component 1: api-gateway-waf

`api-gateway-waf` acts like an API security gateway.

It checks whether basic API security expectations are being followed.

It can work in two modes:

```text
MONITOR_MODE
  Inspect request
  Record security finding
  Forward request even if issue exists

ENFORCE_MODE
  Inspect request
  Apply allowlist/blocklist/policy rules
  Stop request if rule requires blocking
```

## What api-gateway-waf checks

### API security posture checks

```text
Is authentication required?
Is Authorization header present?
Is token format valid?
Is the endpoint public or protected?
Is the HTTP method allowed?
Is the content type valid?
Is the payload schema valid?
Is the request body too large?
Are sensitive fields exposed?
Are unsafe query parameters used?
Are admin endpoints protected?
Are high-risk actions approved?
Is the caller allowed to invoke this API?
Are rate limits being respected?
```

### Injection and suspicious input checks

This lab should simulate defensive detection for unsafe input patterns.

```text
SQL-like suspicious input
Script-like suspicious input
Command-like suspicious input
Path traversal-like suspicious input
Unexpected JSON structure
Unexpected nested payload depth
Oversized payload
Repeated malformed requests
```

The goal is defensive learning: identify risky input and stop or report it.

### Outbound/action checks

The gateway can also inspect sensitive actions going from one service to another.

```text
Is iga-service provisioning the access?
Was approval completed before provisioning?
Is the entitlement high-risk or critical?
Is PAM checkout being requested?
Is emergency access being used?
Is the caller on the allowlist?
Is the caller on the blocklist?
Should this action be logged only or blocked?
```

## Allowlist and blocklist model

### Allowlist

Used for trusted service-to-service calls.

Example:

```text
ALLOW iga-service -> scim-target POST /scim/v2/Groups/*
ALLOW iga-service -> webservices-target POST /api/v1/users/*/roles
ALLOW iga-service -> pam-target POST /pam/v1/safes/*/members
```

### Blocklist

Used to stop known bad or disallowed traffic.

Example:

```text
BLOCK unknown-client -> pam-target POST /pam/v1/checkout-requests
BLOCK any -> iga-service POST /api/v1/admin/debug
BLOCK any request containing suspicious injection pattern
```

### Policy rule decision values

```text
ALLOW
ALLOW_WITH_FINDING
LOG_ONLY
WARN
RATE_LIMIT
BLOCK
REQUIRE_APPROVAL
REQUIRE_STEP_UP
```

## App-level routing option

Every app should have a configuration option to choose whether requests go through the gateway.

Example environment variables:

```text
API_SECURITY_MODE=direct
API_SECURITY_MODE=gateway-monitor
API_SECURITY_MODE=gateway-enforce
```

Recommended behavior:

```text
direct
  App accepts requests directly.
  Useful for baseline testing.

gateway-monitor
  Requests go through api-gateway-waf.
  Gateway logs findings but usually allows traffic.

gateway-enforce
  Requests go through api-gateway-waf.
  Gateway can block, rate-limit, or require step-up approval.
```

## Protected apps

These apps should support direct mode and gateway mode:

```text
iga-service
scim-target
webservices-target
pam-target
```

`jdbc-target` is database-backed, so it is not normally protected through HTTP gateway for direct DB reads. For JDBC, inspection should focus on:

```text
Database query allowlist
Read-only IAM views
Least-privilege DB user
No raw table access from IGA
No unsafe dynamic SQL
```

## Example flows

### Flow 1: Direct mode

```text
iga-service -> scim-target

No gateway inspection.
Target app handles the request directly.
```

### Flow 2: Gateway monitor mode

```text
iga-service -> api-gateway-waf -> scim-target

Gateway checks request.
Finding: missing request_id header.
Decision: ALLOW_WITH_FINDING.
Request continues.
Finding is sent to siem-detection-service.
```

### Flow 3: Gateway enforce mode

```text
unknown-client -> api-gateway-waf -> pam-target

Gateway checks request.
Finding: caller not allowlisted for PAM checkout.
Decision: BLOCK.
Request does not reach pam-target.
```

### Flow 4: High-risk action

```text
iga-service -> api-gateway-waf -> pam-target

Action: grant PAM Emergency Access.
Gateway checks approval status.
Decision: REQUIRE_STEP_UP.
Request pauses until additional approval is completed.
```

## API design

```text
POST /gateway/inspect-request
POST /gateway/inspect-response
POST /gateway/inspect-action
GET  /gateway/policies
POST /gateway/policies
GET  /gateway/events
GET  /gateway/findings
```

## Example inspection request

```json
{
  "source_service": "iga-service",
  "target_service": "pam-target",
  "actor": "RSINGH01",
  "method": "POST",
  "path": "/pam/v1/checkout-requests",
  "headers": {
    "authorization_present": true,
    "content_type": "application/json",
    "request_id": "req-1001"
  },
  "action_type": "PAM_CHECKOUT_REQUEST",
  "risk_level": "CRITICAL",
  "approval_status": "PENDING"
}
```

## Example inspection response

```json
{
  "decision": "REQUIRE_STEP_UP",
  "finding_id": "finding-1001",
  "reason": "Critical PAM checkout requires additional approval",
  "forward_request": false
}
```

## Component 2: siem-detection-service

`siem-detection-service` checks what happened across all apps.

It receives findings and events from:

```text
idp-service
iga-service
scim-target
jdbc-target
webservices-target
pam-target
api-gateway-waf
```

## What siem-detection-service detects

```text
Repeated API security findings
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
DET-009: Protected API called without required security headers
DET-010: Multiple injection-like payloads from same source
```

## Updated architecture

```text
                           Optional gateway mode
                                  |
                                  v
                         +----------------------+
                         |   api-gateway-waf    |
                         | API security checks  |
                         | Monitor / enforce    |
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
                         | Findings / events    |
                         | Alerts / audit       |
                         +----------------------+
```

## Final role of both services

```text
api-gateway-waf
  Checks API security for inbound and outbound traffic.
  Usually monitors and reports.
  Can enforce through allowlists, blocklists, rate limits, and policy rules.

siem-detection-service
  Checks events and findings across all apps.
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
