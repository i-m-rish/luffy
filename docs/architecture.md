# Luffy IAM Lab Architecture

## Purpose

Luffy is a practical cybersecurity IAM integration lab that simulates how an IGA platform such as SailPoint governs different application integration patterns, including privileged access management.

The lab focuses on six components:

1. Identity Provider service
2. SailPoint-like IGA service
3. SCIM target application
4. JDBC/DBMS target application
5. Web Services target application
6. PAM target application

## Architecture

```text
                       +----------------------+
                       |      idp-service     |
                       | Identity source      |
                       | Login + tokens       |
                       +----------+-----------+
                                  |
                                  | Identity aggregation
                                  v
+----------------------+   +------+-------------------+   +----------------------+
| scim-target          |   |      iga-service         |   | webservices-target   |
| Endpoint security    |<->| Aggregation              |<->| Risk + incident APIs |
| SCIM provisioning    |   | Correlation              |   | API provisioning     |
+----------------------+   | Access request           |   +----------------------+
                           | Approval workflow        |
+----------------------+   | Provisioning             |   +----------------------+
| jdbc-target          |<->| Privileged governance    |<->| pam-target           |
| Security assets DB   |   | Governance reports       |   | Vaults + sessions    |
| Users/roles mapping  |   +--------------------------+   | Checkout + audit     |
+----------------------+                                  +----------------------+
```

## Components

### idp-service

Simulates an enterprise Identity Provider such as Entra ID or Okta.

Responsibilities:

- Store workforce identities
- Provide identity attributes for aggregation
- Issue mock tokens
- Maintain employee ID, LAN ID, email, department, manager, and status

### iga-service

Simulates a SailPoint-like governance service.

Responsibilities:

- Aggregate identities from `idp-service`
- Aggregate accounts and entitlements from target systems
- Correlate accounts to identities
- Maintain entitlement catalog
- Handle access requests and approvals
- Provision approved access
- Govern privileged access
- Generate governance and certification-style reports

### scim-target

Simulates a modern endpoint security platform with SCIM 2.0-style APIs.

Responsibilities:

- Expose `/scim/v2/Users`
- Expose `/scim/v2/Groups`
- Support user lifecycle operations
- Support group membership provisioning

### jdbc-target

Simulates a database-backed security asset operations platform.

Responsibilities:

- Store users, roles, and user-role mappings
- Expose IAM-safe views for aggregation
- Demonstrate JDBC-style account and entitlement reads

Recommended views:

```text
vw_iam_accounts
vw_iam_entitlements
vw_iam_account_entitlements
```

### webservices-target

Simulates a security risk and incident platform that exposes REST APIs instead of SCIM.

Responsibilities:

- Expose users APIs
- Expose roles APIs
- Expose role assignment APIs
- Demonstrate Web Services connector-style aggregation and provisioning

### pam-target

Simulates a CyberArk-like Privileged Access Management platform.

Responsibilities:

- Store privileged safes/vaults
- Store privileged accounts
- Manage safe membership
- Support privileged credential checkout requests
- Support approval for privileged access
- Record privileged sessions
- Generate PAM audit events

## Normalized IGA model

The IGA service should convert every source system into these common objects:

```text
Identity
Account
Entitlement
Assignment
AccessRequest
Approval
ProvisioningEvent
PrivilegedSafe
PrivilegedAccount
CheckoutRequest
PrivilegedSession
AuditEvent
```

## Build order

1. `jdbc-target` - simplest way to understand accounts, roles, and mappings
2. `webservices-target` - custom REST API integration pattern
3. `scim-target` - standard SCIM provisioning pattern
4. `pam-target` - privileged access, vault, checkout, and audit pattern
5. `idp-service` - authoritative identity source
6. `iga-service` - aggregation, correlation, request, approval, provisioning, and governance
