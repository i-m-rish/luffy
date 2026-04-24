# API Security Control Plane

## Purpose

The API security control plane checks whether API security is implemented correctly across the Luffy IAM Lab.

It is mainly an inspection, posture discovery, and security validation layer. It usually observes, validates, and reports. It can also enforce controls when configured to do so through allowlists, blocklists, rate limits, or policy rules.

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
What security posture does each app expose?
```

## New components

| Service | Type | Purpose |
|---|---|---|
| `api-gateway-waf` | API security inspection, posture scanning, and optional enforcement layer | Checks API requests, responses, protocol posture, headers, auth, and risky behavior |
| `siem-detection-service` | Event monitoring and detection layer | Collects events from all services and finds suspicious patterns |

## Component 1: api-gateway-waf

`api-gateway-waf` acts like an API security gateway and posture scanner.

It checks whether basic API security expectations are being followed.

It can work in three modes:

```text
DISCOVERY_MODE
  Scan app endpoint metadata and security posture
  Report protocol, TLS, auth, headers, exposed endpoints, and risky defaults

MONITOR_MODE
  Inspect live request/response traffic
  Record security findings
  Forward request even if issue exists

ENFORCE_MODE
  Inspect live request/response traffic
  Apply allowlist/blocklist/policy rules
  Stop request if rule requires blocking
```

## API security posture discovery

The gateway should be able to detect and record the security posture of each app.

### Protocol and transport checks

```text
Is the app using HTTP or HTTPS?
Which TLS/SSL protocol version is used?
Is TLS 1.2 or TLS 1.3 used?
Are deprecated protocols such as SSLv3, TLS 1.0, or TLS 1.1 exposed?
Is the certificate valid?
Is the certificate expired?
Is the certificate self-signed?
Does the certificate common name / SAN match the host?
Is weak cipher usage simulated or reported?
Is HSTS configured?
```

For the lab, this can initially be simulated through service metadata instead of real TLS scanning.

Example posture metadata:

```json
{
  "service": "pam-target",
  "base_url": "https://pam-target.local",
  "protocol": "HTTPS",
  "tls_version": "TLS1.2",
  "certificate_status": "VALID",
  "hsts_enabled": true
}
```

### API authentication checks

```text
Does the API require authentication?
Which auth type is used?
Bearer token?
API key?
Basic auth?
Mutual TLS?
No auth?
Are tokens required on protected endpoints?
Are admin endpoints protected?
Are service-to-service calls authenticated?
```

Supported simulated auth types:

```text
NONE
BASIC
API_KEY
BEARER_TOKEN
OAUTH2_CLIENT_CREDENTIALS
MTLS
```

### Authorization checks

```text
Is RBAC enforced?
Are high-risk endpoints role-protected?
Can normal users call admin endpoints?
Can a requester approve their own access?
Can unknown clients call PAM checkout APIs?
Can IGA provisioning APIs be called by non-IGA services?
```

### Security header checks

```text
Strict-Transport-Security
Content-Security-Policy
X-Content-Type-Options
X-Frame-Options
Referrer-Policy
Cache-Control
Pragma
```

### CORS checks

```text
Is CORS enabled?
Is wildcard origin allowed?
Are credentials allowed with wildcard origin?
Are allowed methods too broad?
Are allowed headers too broad?
```

### Endpoint exposure checks

```text
Are debug endpoints exposed?
Are admin endpoints exposed?
Are health endpoints leaking sensitive data?
Is API documentation exposed publicly?
Are dangerous HTTP methods enabled?
Are unauthenticated write endpoints exposed?
```

Dangerous methods to monitor:

```text
PUT
PATCH
DELETE
TRACE
OPTIONS
```

### Rate limit and abuse checks

```text
Is rate limiting configured?
Is brute-force protection configured?
Are repeated failed requests detected?
Are checkout attempts against pam-target rate-limited?
Are token requests rate-limited?
```

### Logging and audit checks

```text
Is request_id generated or required?
Is actor logged?
Is source service logged?
Is target service logged?
Is decision logged?
Are high-risk actions audited?
Are secrets excluded from logs?
```

### Data exposure checks

```text
Are passwords or secrets returned in responses?
Are tokens exposed in logs?
Are privileged account secrets exposed?
Are excessive user attributes returned?
Are internal errors returned to callers?
```

## Runtime request checks

### Inbound request checks

```text
Who is calling?
Which app are they calling?
Which endpoint are they calling?
Is the token present?
Is the token valid?
Is the method allowed?
Is the payload valid?
Is the request body too large?
Is the user allowed to call this endpoint?
Does the payload contain suspicious input?
Is the caller sending too many requests?
Is this a high-risk action?
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
Connection encryption enabled
Database audit logging enabled
```

## Posture score

The gateway should produce a simple API security posture score for every protected app.

Example categories:

```text
Transport security       20 points
Authentication           20 points
Authorization            20 points
Input validation         15 points
Security headers         10 points
Rate limiting            5 points
Audit logging            10 points
```

Example output:

```json
{
  "service": "webservices-target",
  "score": 72,
  "rating": "MEDIUM",
  "findings": [
    "Missing HSTS header",
    "No rate limit configured on token endpoint",
    "Admin endpoint allows OPTIONS method"
  ]
}
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

### Flow 5: Posture scan

```text
api-gateway-waf -> scim-target /security-metadata

Gateway checks:
- HTTPS enabled
- TLS version
- Auth type
- Security headers
- CORS policy
- Rate limit policy
- Exposed endpoints

Output:
API security posture score and findings
```

## API design

```text
POST /gateway/inspect-request
POST /gateway/inspect-response
POST /gateway/inspect-action
POST /gateway/scan-posture
GET  /gateway/posture-reports
GET  /gateway/policies
POST /gateway/policies
GET  /gateway/events
GET  /gateway/findings
```

## Example posture scan request

```json
{
  "service": "pam-target",
  "base_url": "https://pam-target.local",
  "scan_type": "METADATA_BASED"
}
```

## Example posture scan response

```json
{
  "service": "pam-target",
  "score": 86,
  "rating": "HIGH",
  "transport": {
    "protocol": "HTTPS",
    "tls_version": "TLS1.2",
    "certificate_status": "VALID",
    "hsts_enabled": true
  },
  "auth": {
    "auth_type": "OAUTH2_CLIENT_CREDENTIALS",
    "protected_endpoints": true
  },
  "findings": [
    {
      "severity": "MEDIUM",
      "title": "TLS 1.3 not enabled",
      "recommendation": "Enable TLS 1.3 where supported"
    }
  ]
}
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
Weak API security posture on critical apps
TLS downgrade or weak protocol posture
Protected endpoint called without required security headers
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
DET-011: Critical app has weak API security posture score
DET-012: Deprecated TLS protocol detected
```

## Updated architecture

```text
                           Optional gateway mode
                                  |
                                  v
                         +----------------------+
                         |   api-gateway-waf    |
                         | API security checks  |
                         | Posture scan         |
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
  Discovers API security posture.
  Checks SSL/TLS, protocol, auth, headers, CORS, endpoint exposure, payloads, and runtime traffic.
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
