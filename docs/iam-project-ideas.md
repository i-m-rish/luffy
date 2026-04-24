# IAM Project Ideas Research Map

## Purpose

This document captures practical IAM/cybersecurity project categories that can influence the Luffy IAM Lab.

The goal is not to copy existing projects. The goal is to identify learning patterns and rebuild smaller versions inside Luffy.

## Public project patterns observed

Searches around open-source IAM commonly surface projects in these categories:

```text
Identity Provider / SSO
SCIM identity management
IAM home lab
Access gateway
Directory and federation
Policy-based authorization
```

Examples of public IAM-style repositories found through GitHub search include:

```text
casdoor/casdoor
casgate/casgate
osiam/osiam
GluuFederation/gluu4
0xrajneesh/Open-Source-IAM-Home-Lab
```

These are useful mainly for learning categories, not for direct copying.

## Project categories to learn and rebuild

### 1. Identity Provider / SSO project

What it teaches:

```text
Users
Groups
Login
Tokens
Applications
Clients
Sessions
Authentication vs authorization
```

Build in Luffy:

```text
idp-service
```

MVP features:

```text
User store
Login mock
Token mock
Application/client registry
Group membership
Identity lifecycle status
```

---

### 2. IGA / SailPoint-style project

What it teaches:

```text
Identity aggregation
Account aggregation
Entitlement aggregation
Correlation
Access requests
Approvals
Provisioning
Certification reports
Orphan account review
High-risk access review
```

Build in Luffy:

```text
iga-service
```

MVP features:

```text
Aggregate identities
Aggregate accounts
Aggregate entitlements
Correlate accounts
Request access
Approve access
Provision access
Generate access review report
```

---

### 3. SCIM server project

What it teaches:

```text
SCIM Users
SCIM Groups
User lifecycle provisioning
Group membership provisioning
PATCH behavior
SaaS app onboarding pattern
```

Build in Luffy:

```text
scim-target
```

MVP features:

```text
GET /scim/v2/Users
POST /scim/v2/Users
PATCH /scim/v2/Users/{id}
GET /scim/v2/Groups
PATCH /scim/v2/Groups/{id}
```

---

### 4. JDBC / database-backed IAM project

What it teaches:

```text
Accounts in database tables
Roles in database tables
User-role mappings
Aggregation views
Read-only IAM access
Least privilege DB user
```

Build in Luffy:

```text
jdbc-target
```

MVP features:

```text
users table
roles table
user_roles table
vw_iam_accounts
vw_iam_entitlements
vw_iam_account_entitlements
```

---

### 5. REST Web Services connector project

What it teaches:

```text
Custom API integration
Users API
Roles API
Role assignment API
Pagination
Error handling
JSON payload mapping
API provisioning
```

Build in Luffy:

```text
webservices-target
```

MVP features:

```text
GET /api/v1/users
GET /api/v1/roles
POST /api/v1/users/{id}/roles
DELETE /api/v1/users/{id}/roles/{roleId}
```

---

### 6. PAM / privileged access project

What it teaches:

```text
Safes / vaults
Privileged accounts
Safe membership
Credential checkout
JIT access
Emergency access
Session audit
Privileged access review
```

Build in Luffy:

```text
pam-target
```

MVP features:

```text
Safes
Privileged accounts
Safe members
Checkout requests
Checkout approvals
Privileged sessions
Audit events
```

---

### 7. API security posture project

What it teaches:

```text
HTTP vs HTTPS
TLS posture
Certificate checks
Auth checks
Security headers
CORS checks
Rate limiting
Endpoint exposure
Payload validation
Allowlist/blocklist
Monitor vs enforce mode
```

Build in Luffy:

```text
api-gateway-waf
```

MVP features:

```text
Posture scan
Request inspection
Response inspection
Security findings
API security score
Gateway monitor mode
Gateway enforce mode
```

---

### 8. SIEM / detection project

What it teaches:

```text
Security events
Detection rules
Alerting
Event correlation
IAM misuse detection
PAM abuse detection
API security finding correlation
```

Build in Luffy:

```text
siem-detection-service
```

MVP features:

```text
Event ingestion
Detection rules
Alert generation
Alert lifecycle
Audit investigation
```

---

### 9. Policy engine / authorization project

What it teaches:

```text
RBAC
ABAC
Policy decisions
Permit / deny
Context-based access
Risk-based access
```

Build later in Luffy:

```text
policy-engine
```

Possible future features:

```text
Evaluate access request policy
Evaluate high-risk access policy
Evaluate PAM checkout policy
Evaluate API gateway allow/block policy
```

Do not build this first. Add it after the core services work.

---

### 10. Access review / certification project

What it teaches:

```text
User access review
Manager certification
Application owner certification
High-risk access certification
Revocation workflow
Evidence tracking
```

Build inside:

```text
iga-service
```

MVP features:

```text
Generate review campaign
List access by identity
Approve or revoke access
Track reviewer decision
Generate certification report
```

## Best project order for Luffy

```text
1. jdbc-target
2. webservices-target
3. scim-target
4. pam-target
5. idp-service
6. iga-service
7. api-gateway-waf
8. siem-detection-service
9. certification module inside iga-service
10. policy-engine later
```

## Final recommendation

Do not try to build a full IAM product first.

Build target apps first, then build IGA around them.

The strongest learning path is:

```text
Target app access model
    ↓
Aggregation
    ↓
Correlation
    ↓
Access request
    ↓
Approval
    ↓
Provisioning
    ↓
API security posture
    ↓
SIEM detection
    ↓
Certification report
```
