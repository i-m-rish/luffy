# Five-App IAM Lab - Best Practice Architecture

## Project concept

This project simulates a practical IAM onboarding lab with multiple integration patterns used in enterprise IGA/SailPoint programs.

The lab contains five components:

1. SCIM-enabled target application
2. DBMS/JDBC target application
3. Web Services API target application
4. Identity Provider application
5. SailPoint-like IGA application

The goal is to demonstrate how an IGA platform can govern different types of applications using standard integration patterns.

---

## High-level architecture

```text
                       +----------------------+
                       |      IdP App         |
                       | Entra/Okta Mock      |
                       | Identities + Tokens  |
                       +----------+-----------+
                                  |
                                  | Identity aggregation
                                  v
+----------------------+   +------+-------------------+   +----------------------+
| SCIM Target App      |   | SailPoint-like IGA App   |   | Web Services App     |
| /scim/v2/Users       |<->| Aggregation              |<->| REST APIs            |
| /scim/v2/Groups      |   | Correlation              |   | Users/Roles/Access   |
+----------------------+   | Access Request           |   +----------------------+
                           | Approval Workflow        |
+----------------------+   | Provisioning             |
| DBMS/JDBC App        |<->| Certification Reports    |
| Tables/Views         |   +--------------------------+
| Users/Roles Mapping  |
+----------------------+
```

---

## App 1: SCIM Target Application

### Purpose

Represents a modern SaaS application that supports SCIM 2.0 for user and group lifecycle management.

### Integration pattern

- Standard SCIM connector pattern
- User provisioning
- Group/entitlement provisioning
- Account and group aggregation

### Core APIs

```text
GET    /scim/v2/Users
POST   /scim/v2/Users
GET    /scim/v2/Users/{id}
PATCH  /scim/v2/Users/{id}
DELETE /scim/v2/Users/{id}

GET    /scim/v2/Groups
POST   /scim/v2/Groups
PATCH  /scim/v2/Groups/{id}
```

### Best practices

- Use stable immutable user IDs internally.
- Use email or LAN ID only as correlation attributes, not as database primary keys.
- Support PATCH for group membership changes.
- Return consistent SCIM schemas.
- Keep group display names business-readable.
- Avoid hard delete where possible; support active/inactive status.

---

## App 2: DBMS/JDBC Target Application

### Purpose

Represents an internally hosted or legacy application where access data is stored in database tables.

This is similar to apps where SailPoint connects using JDBC to read accounts, entitlements, and account-to-entitlement mappings.

### Integration pattern

- JDBC-style aggregation
- Read users/accounts from database tables or views
- Read roles/entitlements from database tables or views
- Read account-role mapping from join tables
- Optional write-back/provisioning through stored procedures or controlled SQL operations

### Recommended database design

```text
users
- user_id                 Primary key
- employee_id             Workforce identifier
- lan_id                  Correlation attribute
- email                   Correlation attribute
- display_name
- status                  ACTIVE / INACTIVE
- created_at
- updated_at

roles
- role_id                 Primary key
- role_name
- role_description
- risk_level              LOW / MEDIUM / HIGH
- status                  ACTIVE / INACTIVE

user_roles
- user_id                 Foreign key to users.user_id
- role_id                 Foreign key to roles.role_id
- assigned_at
- assigned_by
- assignment_status       ACTIVE / REVOKED
```

### SailPoint-style aggregation views

Best practice is to expose controlled database views instead of letting the IGA tool query raw transactional tables directly.

```text
vw_iam_accounts
- account_id
- employee_id
- lan_id
- email
- display_name
- account_status

vw_iam_entitlements
- entitlement_id
- entitlement_name
- entitlement_description
- risk_level
- entitlement_status

vw_iam_account_entitlements
- account_id
- entitlement_id
- assignment_status
```

### Best practices

- Prefer read-only database views for aggregation.
- Avoid direct access to core transactional tables.
- Use a least-privilege service account.
- Store credentials outside code using environment variables or secrets management.
- Use parameterized queries only; no string-concatenated SQL.
- Maintain audit columns such as created_at, updated_at, assigned_by, and assigned_at.
- Use soft delete/status flags instead of physical deletion.
- For provisioning, prefer stored procedures or application APIs over direct table updates.
- Use a stable account_id for account identity and correlation.
- Keep entitlement descriptions business-friendly for certification reviewers.

---

## App 3: Web Services API Target Application

### Purpose

Represents an application that does not support SCIM but exposes REST APIs for users, roles, and access assignments.

This is similar to a SailPoint Web Services connector pattern.

### Integration pattern

- REST API aggregation
- REST API provisioning
- OAuth2/API token authentication
- JSON payload transformation
- Pagination and error handling

### Core APIs

```text
GET    /api/v1/users
GET    /api/v1/users/{id}
POST   /api/v1/users
PATCH  /api/v1/users/{id}
DELETE /api/v1/users/{id}

GET    /api/v1/roles
GET    /api/v1/users/{id}/roles
POST   /api/v1/users/{id}/roles
DELETE /api/v1/users/{id}/roles/{roleId}
```

### Recommended response examples

#### User response

```json
{
  "id": "u-1001",
  "employeeId": "1001",
  "lanId": "RSINGH01",
  "email": "rishabh.singh@example.com",
  "displayName": "Rishabh Singh",
  "status": "ACTIVE"
}
```

#### Role response

```json
{
  "id": "role-admin",
  "name": "Application Administrator",
  "description": "Can manage application configuration and user access",
  "riskLevel": "HIGH"
}
```

### Best practices

- Use OAuth2 client credentials or signed API tokens; avoid Basic Auth unless required for lab simulation.
- Use HTTPS in real deployments.
- Implement pagination for list APIs.
- Use consistent HTTP status codes.
- Return machine-readable error responses.
- Keep APIs idempotent where possible.
- Support correlation attributes such as employeeId, lanId, and email.
- Separate authentication from authorization.
- Keep role IDs stable even if role display names change.
- Log provisioning transactions with request ID, actor, timestamp, and outcome.
- Do not expose secrets, passwords, or tokens in logs.

---

## App 4: Identity Provider App

### Purpose

Represents Entra ID, Okta, or a simplified corporate IdP.

### Responsibilities

- Store workforce identities
- Authenticate users
- Issue mock tokens
- Provide authoritative identity attributes

### Core APIs

```text
POST /auth/login
POST /auth/token
GET  /users
GET  /users/{id}
```

### Best practices

- Treat IdP as the source for workforce identity attributes.
- Do not treat app roles as identity attributes unless they are truly managed by the IdP.
- Keep authentication separate from application authorization.
- Use stable identity IDs.
- Maintain attributes required for correlation: employee ID, LAN ID, email, manager, department.

---

## App 5: SailPoint-like IGA Application

### Purpose

Represents the governance layer that connects to all target systems.

### Responsibilities

- Aggregate identities from IdP
- Aggregate accounts and entitlements from target apps
- Correlate accounts to identities
- Maintain entitlement catalog
- Create access requests
- Route approvals
- Provision access to target apps
- Generate certification/governance reports

### Connector patterns simulated

```text
SCIM connector      -> SCIM Target App
JDBC connector      -> DBMS/JDBC App
Web Services        -> Web Services API App
Identity source     -> IdP App
```

### Best practices

- Keep connector logic separate from governance logic.
- Normalize accounts and entitlements from different apps into a common internal model.
- Never assume email alone is enough for correlation; use fallback matching rules carefully.
- Maintain correlation confidence status: HIGH, MEDIUM, LOW, UNMATCHED.
- Log every aggregation and provisioning transaction.
- Prevent direct provisioning without approval workflow.
- Use entitlement descriptions and risk levels for certification usability.
- Keep request, approval, and provisioning events auditable.
- Support exception handling for failed provisioning.

---

## Normalized internal IGA model

The IGA app should convert every target system into a common model.

### Identity

```text
identity_id
employee_id
lan_id
email
display_name
manager_id
department
status
```

### Account

```text
account_id
application_name
native_account_id
correlation_key
account_status
identity_id
correlation_status
```

### Entitlement

```text
entitlement_id
application_name
native_entitlement_id
entitlement_name
description
risk_level
status
```

### Assignment

```text
assignment_id
account_id
entitlement_id
assignment_status
assigned_at
assigned_by
source_system
```

---

## Recommended folder structure

```text
luffy/
├── apps/
│   ├── scim-target-app/
│   ├── dbms-target-app/
│   ├── webservices-target-app/
│   ├── idp-app/
│   └── iga-app/
├── docs/
│   ├── project-plan.md
│   ├── three-app-architecture.md
│   └── five-app-iam-lab-best-practice-architecture.md
├── sample-data/
├── reports/
└── src/
```

---

## Build order

### Phase 1: DBMS/JDBC target app

Build database tables and seed data first because it teaches the clearest account-entitlement model.

### Phase 2: Web Services API target app

Build REST APIs for users, roles, and role assignment.

### Phase 3: SCIM target app

Build SCIM-style users and groups.

### Phase 4: IdP app

Build identity source and token simulation.

### Phase 5: IGA app

Build aggregation, correlation, request approval, and provisioning.

---

## Resume framing

Built a five-component IAM integration lab simulating SailPoint governance across SCIM, JDBC/DBMS, and REST Web Services connector patterns, including identity aggregation, account correlation, entitlement catalog normalization, approval workflow, and auditable provisioning.
