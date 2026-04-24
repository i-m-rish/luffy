# Luffy Architecture

## Purpose

Luffy is a cybersecurity IAM learning lab that simulates how identity, governance, target applications, privileged access, API security, detection, machine identity, and future AI agents can work together.

The goal is not to clone any enterprise product. The goal is to rebuild smaller safe versions of the important IAM and cybersecurity concepts.

## Correct architecture principle

Use the right pattern in the right place:

```text
HRMS                 -> REST + database later
IdP                  -> GraphQL + REST login
IGA                  -> GraphQL
JDBC target          -> SQL/JDBC
Web Services target  -> REST + cloud DB later
SCIM target          -> SCIM 2.0 SaaS pattern
PAM target           -> REST/PAM-style APIs
API gateway/WAF      -> REST posture and inspection APIs
SIEM detection       -> event ingestion APIs
Desktop agent        -> desktop/client app later
AI agents            -> later, after clean data exists
```

## High-level flow

```text
hrms-service
  -> source of worker lifecycle
  -> joiner / mover / leaver

idp-service
  -> digital identity
  -> groups, app registrations, tokens, machine identities

iga-service
  -> aggregation, correlation, access request, approval, provisioning, certification

Target apps
  -> jdbc-target
  -> webservices-target
  -> scim-target
  -> pam-target

Security layer
  -> api-gateway-waf
  -> siem-detection-service

Endpoint layer later
  -> desktop-agent-app

AI layer later
  -> IAM review, onboarding, API security, certification, and machine identity agents
```

## Architecture diagram

```text
+----------------+      +----------------+      +----------------+
| hrms-service   | ---> | idp-service    | ---> | iga-service    |
| Workers/JML    |      | GraphQL + auth |      | GraphQL IGA    |
+----------------+      +----------------+      +-------+--------+
                                                        |
                                                        |
                 +--------------------------------------+--------------------------------+
                 |                                      |                                |
                 v                                      v                                v
        +----------------+                    +--------------------+             +----------------+
        | jdbc-target    |                    | webservices-target |             | scim-target    |
        | SQL/JDBC       |                    | REST + cloud DB    |             | SaaS + SCIM    |
        +----------------+                    +--------------------+             +----------------+
                 |
                 |                                      +----------------+
                 +------------------------------------> | pam-target     |
                                                        | PAM + audit    |
                                                        +----------------+

                         +----------------------+
                         | api-gateway-waf      |
                         | posture/monitor/block|
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | siem-detection       |
                         | events/alerts        |
                         +----------------------+
```

## Services

### hrms-service

Acts like Workday, SAP SuccessFactors, Oracle HCM, or PeopleSoft.

Responsibilities:

```text
Workers
Departments
Positions
Managers
Joiner/mover/leaver events
Employment status
Worker type
```

Purpose:

```text
Authoritative employee lifecycle source.
```

### idp-service

Acts like Entra ID or Okta.

Use GraphQL for connected identity data and REST for login/token simulation.

Responsibilities:

```text
Digital identities
Groups
App registrations
SSO metadata
Tokens
Machine identities
OAuth clients
Service principals
Certificates later
```

Purpose:

```text
Authentication, app registration, digital identity, and machine identity source.
```

### iga-service

Acts like SailPoint-style IGA.

Use GraphQL because IGA data is highly connected.

Responsibilities:

```text
Application catalog
Identity aggregation
Account aggregation
Entitlement aggregation
Correlation
Access requests
Approvals
Provisioning events
Certification reports
PAM governance
Machine identity governance later
```

Purpose:

```text
Governance layer that answers who has what access, why, who approved it, whether it is risky, and whether it should be revoked.
```

### jdbc-target

Acts like a database-backed security asset operations platform.

Pattern:

```text
SQL database
JDBC-style aggregation
IAM-safe views
```

Core objects:

```text
users
roles
user_roles
vw_iam_accounts
vw_iam_entitlements
vw_iam_account_entitlements
```

### webservices-target

Acts like a custom cloud security risk or incident application.

Pattern:

```text
REST APIs
Cloud database later
Users, roles, role assignments
```

Purpose:

```text
Learn Web Services connector-style onboarding.
```

### scim-target

Acts like a SaaS endpoint security console.

Pattern:

```text
SCIM 2.0
Tenant-aware SaaS app
Users
Groups
Roles through group membership
```

Purpose:

```text
Learn modern SaaS SCIM onboarding.
```

### pam-target

Acts like a CyberArk-like PAM system.

Pattern:

```text
REST/PAM-style APIs
Safes
Privileged accounts
Safe members
Checkout requests
Approvals
Privileged sessions
Audit events
```

Purpose:

```text
Learn privileged access governance, JIT access, checkout approval, and session audit.
```

### api-gateway-waf

Acts like API security posture and optional enforcement layer.

Pattern:

```text
REST APIs
Discovery mode
Monitor mode
Enforce mode
Allowlist/blocklist
```

Checks:

```text
HTTP vs HTTPS
TLS/SSL version
Certificate status
Auth type
Security headers
CORS
Rate limiting
Endpoint exposure
Payload issues
Suspicious input
```

### siem-detection-service

Acts like SIEM/detection engineering layer.

Pattern:

```text
Event ingestion API
Detection rules
Alerts
Investigations
```

Detects:

```text
Orphan accounts
High-risk access without approval
PAM checkout outside business hours
Weak API posture
Repeated blocked requests
Suspicious access patterns
```

### desktop-agent-app

Acts like an endpoint desktop agent later.

Pattern:

```text
Desktop/client app
Device heartbeat
Device posture
Local event reporting
Machine identity/certificate later
```

Purpose:

```text
Learn endpoint identity, device posture, and machine identity concepts.
```

## GraphQL decision

Use GraphQL in:

```text
idp-service
iga-service
```

Do not force GraphQL into:

```text
jdbc-target
webservices-target
scim-target
pam-target
api-gateway-waf
siem-detection-service
```

Reason:

```text
IdP and IGA need flexible relationship queries.
Target apps should preserve realistic integration patterns.
```

## Machine identity plan

Machine identity should be introduced after human identity and app access work.

Objects:

```text
MachineIdentity
ServiceAccount
OAuthClient
ServicePrincipal
Certificate
Secret
Token
Owner
RotationStatus
RiskLevel
```

Example questions:

```text
Who owns this service account?
Which app uses this OAuth client?
When was the secret last rotated?
Is this certificate expired?
Is this machine identity orphaned?
```

## AI agent plan

Agents come after data, APIs, and reports exist.

Future agents:

```text
IAM review agent
App onboarding agent
API security agent
Certification recommendation agent
Machine identity risk agent
```

Agents should explain, recommend, summarize, and flag risk. They should not silently provision or revoke access in the first version.

## Build order

### Milestone 1 - Foundation

```text
1. jdbc-target
2. hrms-service
3. idp-service with basic GraphQL
4. iga-service with basic GraphQL
```

### Milestone 2 - Additional target patterns

```text
5. webservices-target
6. scim-target as SaaS app
7. pam-target
```

### Milestone 3 - API security and detection

```text
8. api-gateway-waf
9. siem-detection-service
```

### Milestone 4 - Endpoint and machine identity

```text
10. desktop-agent-app
11. machine identity governance
```

### Milestone 5 - AI agents

```text
12. agent layer
```
