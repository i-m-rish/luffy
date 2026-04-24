# API and Authentication Standards

## Purpose

This document defines the API, authentication, authorization, cryptography, and identity security baseline for Luffy.

The goal is to keep the lab aligned with modern security practices and established standards such as NIST digital identity guidance, NIST zero trust principles, secure software development practices, OWASP API security guidance, OAuth/OIDC patterns, and secure-by-design engineering.

This document should be reviewed periodically because security standards evolve.

## Standards baseline

Use these as guiding references:

```text
NIST SP 800-63 series        Digital identity, authentication, federation
NIST SP 800-53               Security and privacy controls
NIST SP 800-207              Zero Trust Architecture
NIST SP 800-218              Secure Software Development Framework
NIST SP 800-57               Key management guidance
NIST SP 800-92               Log management guidance
NIST SP 800-61               Incident handling guidance
OWASP API Security Top 10    API risk categories
OWASP ASVS                   Application security verification
OAuth 2.0 / OIDC             Token-based authentication and federation
SCIM 2.0                     Identity provisioning for SaaS-style apps
```

## Project-level API rules

Every API-based service should follow these rules:

```text
Use HTTPS in realistic deployments.
Use TLS 1.2 minimum; prefer TLS 1.3 where supported.
Do not use SSLv2, SSLv3, TLS 1.0, or TLS 1.1.
Use authentication by default for protected endpoints.
Use authorization checks at object/action level.
Validate all input.
Return safe error messages.
Do not expose secrets in responses.
Do not log tokens or passwords.
Use request_id and audit_id for traceability.
Use rate limits on sensitive endpoints.
Use pagination on list endpoints.
Use consistent status codes and error formats.
```

## Authentication standards

### Human users

Use simulated OIDC/OAuth-style flows for user login.

Recommended pattern:

```text
idp-service issues token
client calls protected service
protected service validates token claims
service checks authorization before returning data
```

Minimum token claims to model:

```text
sub
email
employee_id
lan_id
groups
roles
issuer
audience
issued_at
expires_at
```

### Service-to-service calls

Use service identities instead of shared human accounts.

Recommended patterns:

```text
OAuth2 client credentials
Mutual TLS later
Signed service token later
```

Avoid:

```text
Hardcoded shared passwords
Long-lived static tokens
One token reused by all services
Anonymous service-to-service calls
```

### Machine identities

Machine identities should be first-class governed objects.

Examples:

```text
OAuth client
Service principal
API integration account
SCIM connector token
Certificate identity
Desktop agent device certificate
Automation service account
```

Governance attributes:

```text
machine_identity_id
name
type
owner
owning_team
used_by_service
risk_level
created_at
last_used_at
secret_rotation_due_at
certificate_expiry_date
status
```

## Authorization standards

Authentication proves who/what is calling. Authorization decides what they can do.

Required checks:

```text
Role-based access control for admin functions.
Object-level authorization for identity/account data.
High-risk action checks for PAM and admin access.
Requester cannot approve own access.
Only iga-service can call provisioning endpoints in target apps.
Only authorized services can ingest detection events.
Only security admins can change gateway enforcement policies.
```

Access decision output should include:

```text
decision
reason
policy_id
actor
target_resource
action
risk_level
```

## API design standards

### Versioning

Use versioned APIs:

```text
/api/v1/...
/hrms/v1/...
/pam/v1/...
/scim/v2/...
```

### Pagination

List APIs should support pagination:

```text
limit
offset
next_cursor
```

### Filtering

Use explicit filters:

```text
status
application_id
identity_id
risk_level
updated_after
```

### Error format

Use consistent error responses:

```json
{
  "error_code": "ACCESS_DENIED",
  "message": "The caller is not allowed to perform this action.",
  "request_id": "req-1001",
  "details": []
}
```

### Safe errors

Do not return:

```text
Stack traces
Database errors
Raw SQL errors
Secrets
Internal hostnames
Token contents
```

## GraphQL security standards

GraphQL will be used in:

```text
idp-service
iga-service
```

Controls:

```text
Limit query depth.
Limit query complexity.
Limit page sizes.
Apply object-level authorization.
Use allowlisted operations later for sensitive environments.
Disable unrestricted introspection outside local/dev mode.
Do not expose secrets, tokens, or private keys.
Log high-risk GraphQL operations.
Use field-level authorization for sensitive identity and access data.
```

GraphQL should never allow a user to query another user's sensitive access data unless policy allows it.

## SCIM security standards

For `scim-target`:

```text
Require bearer token or OAuth client credential simulation.
Protect /scim/v2/Users and /scim/v2/Groups.
Validate SCIM schemas.
Use stable immutable IDs.
Support active/inactive state instead of hard delete by default.
Audit create, update, deactivate, and group membership changes.
Do not expose secrets in SCIM responses.
```

## PAM security standards

For `pam-target`:

```text
PAM safe membership is high risk.
Credential checkout requires approval.
Emergency access requires follow-up review.
Session start/end must be audited.
Privileged account secrets must never be returned in plain text.
Password rotation is simulated only; no real secrets.
Critical PAM roles require additional approval.
```

## API security gateway standards

For `api-security-gateway`:

Modes:

```text
DISCOVERY_MODE
MONITOR_MODE
ENFORCE_MODE
```

Checks:

```text
TLS version
Certificate status
Authentication required
Authorization checks
Security headers
CORS configuration
Rate limiting
Payload size
Suspicious input patterns
Exposed debug/admin endpoints
Dangerous HTTP methods
Sensitive data in responses
```

The gateway may enforce:

```text
allowlist
blocklist
rate limit
step-up approval
human approval requirement
```

Default recommendation:

```text
Start in MONITOR_MODE.
Move selected high-risk actions to ENFORCE_MODE later.
```

## Zero trust alignment

Assume no service is trusted just because it is inside the lab.

Rules:

```text
Verify every caller.
Authorize every action.
Use least privilege.
Log important decisions.
Do not rely only on network location.
Use service identity for service-to-service calls.
Continuously evaluate risk through SIEM findings and gateway posture reports.
```

## Secure software development baseline

Before adding implementation code:

```text
Use dependency pinning later.
Add linting.
Add unit tests.
Add secret scanning later.
Add dependency scanning later.
Avoid copying unreviewed code.
Keep sample data fake.
Document assumptions.
```

## Required security metadata per service

Every API service should expose or maintain security metadata for posture scanning.

Example:

```json
{
  "service": "webservices-target",
  "protocol": "HTTPS",
  "tls_version": "TLS1.2",
  "auth_required": true,
  "auth_type": "OAUTH2_CLIENT_CREDENTIALS",
  "rbac_enabled": true,
  "rate_limit_enabled": true,
  "security_headers_enabled": true,
  "cors_policy": "RESTRICTED",
  "audit_logging_enabled": true
}
```

## Minimum implementation checklist

Before a service is considered acceptable, it should define:

```text
API endpoints
Authentication type
Authorization model
Audit events
Sensitive data rules
Logging rules
Rate-limit expectations
Error format
Security metadata
Threat model
```

## Final rule

No API should be added as just a working endpoint.

Every API should answer:

```text
Who can call it?
What can they do?
What data can they see?
What is logged?
What happens if the request is invalid?
How is abuse detected?
Can the security gateway inspect it?
Can IGA govern access to it?
```
