# JDBC Target Data Model

## Entity: users

Represents application accounts in the database-backed security asset operations app.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `user_id` | integer | Yes | Primary key |
| `employee_id` | text | Yes | Unique workforce identifier used for correlation |
| `lan_id` | text | Yes | Unique LAN/account identifier |
| `email` | text | Yes | Unique email identifier |
| `display_name` | text | Yes | Human-readable name |
| `department` | text | Yes | Department context |
| `account_status` | text | Yes | `ACTIVE`, `INACTIVE`, `LOCKED`, `TERMINATED` |
| `created_at` | text | Yes | ISO-style timestamp |
| `updated_at` | text | Yes | ISO-style timestamp |

## Entity: roles

Represents application entitlements.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `role_id` | integer | Yes | Primary key |
| `role_code` | text | Yes | Unique entitlement code |
| `role_name` | text | Yes | Human-readable entitlement name |
| `role_description` | text | Yes | Certification-friendly description |
| `risk_level` | text | Yes | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `role_status` | text | Yes | `ACTIVE`, `INACTIVE` |
| `created_at` | text | Yes | ISO-style timestamp |
| `updated_at` | text | Yes | ISO-style timestamp |

## Entity: user_roles

Represents account-entitlement assignments.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `user_role_id` | integer | Yes | Primary key |
| `user_id` | integer | Yes | Foreign key to `users.user_id` |
| `role_id` | integer | Yes | Foreign key to `roles.role_id` |
| `assignment_status` | text | Yes | `ACTIVE`, `REVOKED` |
| `assigned_by` | text | Yes | Actor/source that assigned the role |
| `assigned_at` | text | Yes | Assignment timestamp |
| `revoked_by` | text | No | Actor/source that revoked the role |
| `revoked_at` | text | No | Revocation timestamp |
| `assignment_reason` | text | No | Business reason or note |

## IAM-safe views

### vw_iam_accounts

Used by IGA for account aggregation.

### vw_iam_entitlements

Used by IGA for entitlement aggregation.

### vw_iam_account_entitlements

Used by IGA for account-entitlement assignment aggregation.

## Risk model

```text
LOW       -> read-only/basic access
MEDIUM    -> business-impacting access
HIGH      -> remediation or privileged operational access
CRITICAL  -> system administration or highly privileged access
```

## Correlation attributes

Preferred order for later IGA correlation:

```text
employee_id
lan_id
email
```

## Sample intentional test condition

Seed data includes one orphan-style account:

```text
employee_id: 9001
lan_id: ORPHAN01
email: orphan.account@example.com
```

This is used later to test unmatched account/correlation behavior.
