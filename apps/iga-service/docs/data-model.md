# IGA Service Data Model

## Entity: application

Represents an onboarded application/source in IGA.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `application_id` | string | Yes | Unique app/source ID |
| `application_name` | string | Yes | Human-readable name |
| `application_type` | string | Yes | `HRMS`, `IDP`, `TARGET`, `PAM`, `SECURITY`, `IGA` |
| `integration_pattern` | string | Yes | `JSON`, `JDBC`, `GRAPHQL`, `REST`, `SCIM`, `PAM_API`, `EVENT_API` |
| `risk_level` | string | Yes | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `status` | string | Yes | `ACTIVE`, `INACTIVE`, `DESIGN`, `FUTURE` |
| `owner` | string | Yes | Owning team |

## Entity: identity

Represents a governed identity.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `identity_id` | string | Yes | IGA identity ID |
| `employee_id` | string | Conditional | Required for human workforce identities |
| `lan_id` | string | Yes | Login/account identifier |
| `email` | string | Yes | Fake/sample email |
| `display_name` | string | Yes | Name |
| `identity_type` | string | Yes | `HUMAN`, `MACHINE` |
| `identity_status` | string | Yes | `ACTIVE`, `DISABLED`, `TERMINATED`, `STAGED` |
| `source_system` | string | Yes | Source app/service |

## Entity: account

Represents an account inside a specific application.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `account_id` | string | Yes | IGA account ID |
| `application_id` | string | Yes | Application containing the account |
| `native_account_id` | string | Yes | Source-native account ID |
| `employee_id` | string | No | Correlation attribute |
| `lan_id` | string | No | Correlation attribute |
| `email` | string | No | Correlation attribute |
| `account_status` | string | Yes | `ACTIVE`, `DISABLED`, `LOCKED`, `TERMINATED` |
| `correlation_status` | string | Yes | `MATCHED`, `PARTIAL`, `ORPHAN`, `NOT_EVALUATED` |

## Entity: entitlement

Represents a governed app entitlement.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `entitlement_id` | string | Yes | IGA entitlement ID |
| `application_id` | string | Yes | Application exposing entitlement |
| `native_entitlement_id` | string | Yes | Source-native entitlement ID |
| `entitlement_name` | string | Yes | Name |
| `entitlement_description` | string | Yes | Certification-friendly description |
| `risk_level` | string | Yes | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `status` | string | Yes | `ACTIVE`, `INACTIVE` |

## Entity: assignment

Represents account-entitlement relationship.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `assignment_id` | string | Yes | Unique assignment ID |
| `account_id` | string | Yes | Account receiving access |
| `entitlement_id` | string | Yes | Entitlement assigned |
| `assignment_status` | string | Yes | `ACTIVE`, `REVOKED` |
| `assigned_by` | string | Yes | Source/actor |
| `assigned_at` | string | Yes | Timestamp |

## Entity: correlation_result

Represents account-to-identity matching outcome.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `correlation_id` | string | Yes | Unique correlation ID |
| `account_id` | string | Yes | Account evaluated |
| `identity_id` | string | No | Matched identity if any |
| `result` | string | Yes | `MATCHED`, `PARTIAL`, `ORPHAN` |
| `match_attribute` | string | Yes | `employee_id`, `lan_id`, `email`, `NONE` |
| `confidence` | string | Yes | `HIGH`, `MEDIUM`, `LOW`, `NONE` |
| `reason` | string | Yes | Explanation |

## Important distinction

```text
HRMS worker = employment record
IdP identity = digital identity/authentication record
IGA identity = governed identity record
Target account = account inside an application
Entitlement = access unit inside an application
Assignment = account has entitlement
```
