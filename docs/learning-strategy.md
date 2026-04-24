# Learning Strategy

## Core idea

Luffy is a learning-by-rebuilding cybersecurity IAM lab.

The goal is not to copy enterprise products. The goal is to understand the core access governance concepts used by major IAM, IGA, PAM, endpoint security, risk, and operations platforms, then build smaller safe versions of those concepts.

## Learning method

For each platform type:

```text
1. Study what the real product category does.
2. Identify the IAM-relevant objects.
3. Identify how users get access.
4. Identify how access is approved.
5. Identify how access is provisioned.
6. Identify how access is reviewed or audited.
7. Build a simplified version in Luffy.
```

## Platform types to learn

| Luffy service | Real-world platform type | What to learn |
|---|---|---|
| `idp-service` | Entra ID / Okta-style IdP | Identity source, attributes, tokens, authentication vs authorization |
| `iga-service` | SailPoint-style IGA | Aggregation, correlation, access request, approval, provisioning, certification |
| `scim-target` | CrowdStrike-like endpoint security SaaS | SCIM users, groups, role assignment, security entitlement governance |
| `jdbc-target` | IBM Maximo-like operations platform | Database accounts, roles, mapping tables, IAM-safe views, JDBC aggregation |
| `webservices-target` | Custom risk/incident platform | REST API connector pattern, payload mapping, API provisioning, pagination, errors |
| `pam-target` | CyberArk-like PAM platform | Safes, vaults, privileged accounts, checkout, JIT access, session audit |

## What to rebuild from each product category

### IdP category

Build only:

- Workforce identities
- Login simulation
- Token generation mock
- Manager and department attributes
- Identity status lifecycle

Do not build:

- Full SSO implementation
- Real OAuth/OIDC security implementation in the first phase
- Production-grade identity federation

### IGA category

Build only:

- Identity aggregation
- Account aggregation
- Entitlement aggregation
- Correlation rules
- Access request workflow
- Approval workflow
- Provisioning event tracking
- Governance report

Do not build:

- Full SailPoint replacement
- Complex policy engine in the first phase
- Enterprise workflow designer

### Endpoint security category

Build only:

- Security users
- Security groups
- Endpoint security roles
- SCIM users/groups endpoints
- Role assignment through group membership

Do not build:

- Real endpoint detection
- Malware scanning
- EDR agent logic

### Security asset operations category

Build only:

- Asset users
- Asset roles
- User-role mapping
- IAM aggregation views
- Basic asset ownership data

Do not build:

- Full asset management product
- Work order engine
- Real CMDB implementation

### Risk and incident category

Build only:

- Users API
- Roles API
- Role assignment API
- Risk/incident records for context
- API-based provisioning

Do not build:

- Full GRC product
- Full case management system
- Real incident response platform

### PAM category

Build only:

- Safes/vaults
- Privileged accounts
- Safe membership
- Checkout request
- Approval before checkout
- Privileged session record
- Audit event report

Do not build:

- Real password vault
- Real credential storage
- Real session proxying
- Real secret rotation in the first phase

## Best build sequence

```text
1. jdbc-target
2. webservices-target
3. scim-target
4. pam-target
5. idp-service
6. iga-service
```

Reason:

Start with target applications first so the IGA service has something real to aggregate, correlate, and govern.

## Final learning outcome

By building Luffy, the learner should understand:

- How SailPoint-style onboarding differs across SCIM, JDBC, REST API, and PAM patterns
- How identity, account, entitlement, assignment, approval, and provisioning objects relate to each other
- Why privileged access governance is different from normal app access governance
- How cybersecurity platforms expose access models that IGA systems need to govern
- How to explain IAM integration patterns in interviews and real onboarding discussions
