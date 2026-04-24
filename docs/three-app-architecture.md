# Three-App IAM Lab Architecture

## Project concept

This project will simulate a real IAM onboarding flow using three separate applications/components.

The goal is to understand how SailPoint, an Identity Provider, and a SCIM-enabled target application interact during access provisioning and governance.

## Component 1: SCIM Target Application

This app represents a business application that supports SCIM APIs.

### Responsibilities

- Store users
- Store groups/roles/entitlements
- Expose SCIM-style APIs
- Accept provisioning requests from the SailPoint-like app
- Return users, groups, and membership data for aggregation

### Example APIs

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

### What this teaches

- SCIM user schema
- SCIM group schema
- Provisioning
- De-provisioning
- Entitlement assignment
- Aggregation

## Component 2: Identity Provider App

This app represents an IdP such as Entra ID, Okta, or a simplified corporate identity provider.

### Responsibilities

- Authenticate users
- Issue tokens
- Store workforce identities
- Maintain identity attributes such as employee ID, LAN ID, email, department, and manager
- Later support SSO-like login simulation

### Example APIs

```text
POST /auth/login
POST /auth/token
GET  /users
GET  /users/{id}
```

### What this teaches

- Authentication vs authorization
- Identity source concepts
- Token-based access
- Workforce identity attributes
- IdP role in application access

## Component 3: SailPoint-like Governance App

This app represents a simplified SailPoint/IGA system.

### Responsibilities

- Connect to the IdP for identity data
- Connect to the SCIM app for accounts and entitlements
- Aggregate users and groups
- Correlate app accounts to identities
- Create access requests
- Approve/reject requests
- Provision approved access to the SCIM app
- Generate governance reports

### Example modules

```text
Identity Aggregation
Account Aggregation
Correlation Engine
Access Request Engine
Approval Workflow
Provisioning Engine
Certification Report Generator
```

### Example APIs

```text
POST /aggregate/identities
POST /aggregate/accounts
POST /correlate
POST /access-requests
POST /access-requests/{id}/approve
POST /provision
GET  /reports/governance
```

### What this teaches

- Identity governance lifecycle
- Account correlation
- Entitlement catalog
- Access request flow
- Approval workflow
- Provisioning through SCIM
- Governance reporting

## End-to-end flow

```text
1. IdP stores workforce identities.
2. SCIM app stores application accounts and groups.
3. SailPoint-like app aggregates identities from IdP.
4. SailPoint-like app aggregates accounts/groups from SCIM app.
5. SailPoint-like app correlates SCIM accounts with IdP identities.
6. User requests access in SailPoint-like app.
7. Manager/app owner approves request.
8. SailPoint-like app provisions group membership to SCIM app.
9. SailPoint-like app generates governance report.
```

## Recommended tech stack

Start with Python and FastAPI for all three components.

```text
luffy/
├── apps/
│   ├── scim-target-app/
│   ├── idp-app/
│   └── iga-app/
├── docs/
├── sample-data/
└── reports/
```

## MVP build order

### Step 1: Build SCIM target app

- Create users endpoint
- Create groups endpoint
- Support adding user to group

### Step 2: Build IdP app

- Create identity records
- Add simple login/token mock

### Step 3: Build SailPoint-like app

- Pull identities from IdP
- Pull accounts/groups from SCIM app
- Match identity email/LAN ID to app account
- Create access request
- Provision approved access into SCIM app

## Resume framing

Designed and built a three-component IAM lab simulating SailPoint IGA, an IdP, and a SCIM-enabled target application to demonstrate identity aggregation, account correlation, access request approval, and SCIM-based provisioning workflows.
