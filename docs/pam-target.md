# PAM Target

## Service name

`pam-target`

## Simulated platform type

Privileged Access Management platform.

This is a CyberArk-like PAM system used to govern privileged accounts, vault access, credential checkout, session access, emergency access, and privileged activity audit.

## Why this app is important

This app is different from normal SCIM, JDBC, or Web Services target applications.

Most target apps answer this question:

```text
Who has what access?
```

A PAM platform also answers:

```text
Who can check out privileged credentials?
Who can start privileged sessions?
Who approved the session?
When was the credential used?
Was the privileged activity audited?
```

This makes it a high-value IAM/cybersecurity use case.

## Connector pattern

Use a PAM connector pattern.

The integration should focus on:

- Privileged account inventory
- Safe/vault membership
- Credential checkout permission
- Session access permission
- Just-in-time privileged access
- Approval before privileged access
- Session audit logs
- Emergency/break-glass access

## Difference from other connector types

| Target | Normal pattern | What access means |
|---|---|---|
| `scim-target` | SCIM | User/group provisioning |
| `jdbc-target` | JDBC | DB account-role mappings |
| `webservices-target` | REST APIs | API-based role assignment |
| `pam-target` | PAM connector | Permission to use privileged accounts and sessions |

## Core objects

### Safe

A safe is a logical vault/container for privileged accounts.

Example:

```text
safe_id
safe_name
safe_description
owner
risk_level
status
```

### Privileged account

A privileged account is a shared or elevated account stored in a safe.

Example:

```text
privileged_account_id
safe_id
account_name
platform_type
target_system
risk_level
status
```

### Safe membership

Safe membership defines who can access a vault/safe and what they can do.

Example permissions:

```text
View Safe
List Accounts
Request Checkout
Approve Checkout
Manage Safe
Rotate Password
Emergency Access
```

### Checkout request

A checkout request records a request to use a privileged credential or privileged session.

Example:

```text
checkout_request_id
identity_id
privileged_account_id
requested_reason
approval_status
approved_by
valid_from
valid_until
status
```

### Privileged session

A privileged session records actual use of privileged access.

Example:

```text
session_id
checkout_request_id
identity_id
privileged_account_id
started_at
ended_at
session_status
audit_status
```

## Example entitlements

```text
PAM Safe Viewer
PAM Account Requester
PAM Checkout Approver
PAM Password Rotator
PAM Safe Administrator
PAM Emergency Access
```

## Recommended risk levels

```text
PAM Safe Viewer          MEDIUM
PAM Account Requester    HIGH
PAM Checkout Approver    HIGH
PAM Password Rotator     CRITICAL
PAM Safe Administrator   CRITICAL
PAM Emergency Access     CRITICAL
```

## APIs to simulate

```text
GET  /pam/v1/safes
GET  /pam/v1/safes/{safeId}/accounts
GET  /pam/v1/safes/{safeId}/members
POST /pam/v1/safes/{safeId}/members
DELETE /pam/v1/safes/{safeId}/members/{identityId}

POST /pam/v1/checkout-requests
POST /pam/v1/checkout-requests/{requestId}/approve
POST /pam/v1/checkout-requests/{requestId}/deny
POST /pam/v1/sessions/start
POST /pam/v1/sessions/{sessionId}/end
GET  /pam/v1/audit-events
```

## IGA use cases

The `iga-service` should support these PAM governance use cases:

1. Aggregate privileged safes.
2. Aggregate privileged accounts.
3. Aggregate safe memberships.
4. Correlate safe members to identities.
5. Request access to a PAM safe.
6. Require additional approval for critical access.
7. Provision safe membership.
8. Review who can check out privileged accounts.
9. Detect orphan privileged access.
10. Generate PAM certification reports.

## Minimum viable demo

```text
1. Seed one safe: Windows Domain Admin Safe.
2. Seed two privileged accounts: domain-admin-01 and server-root-01.
3. Seed one identity from idp-service.
4. Request PAM Account Requester access.
5. Approve the request.
6. Add the identity as a safe member.
7. Create a credential checkout request.
8. Approve checkout.
9. Start and end a privileged session.
10. Generate audit report.
```

## Why this is strong for interviews

This app shows understanding beyond normal access provisioning.

It covers:

- Privileged identity governance
- PAM and IGA integration
- High-risk entitlement governance
- Just-in-time access
- Approval workflow
- Session audit
- Break-glass access
- Orphan privileged access review
