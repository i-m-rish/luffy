# IdP Service Data Model

## Entity: identity

Represents a digital identity.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `identity_id` | string | Yes | IdP native identity ID |
| `employee_id` | string | Conditional | Required for human workforce identities |
| `lan_id` | string | Yes | Login/account identifier |
| `email` | string | Yes | Fake/sample corporate email |
| `display_name` | string | Yes | Human-readable name |
| `identity_type` | string | Yes | `HUMAN`, `MACHINE` |
| `identity_status` | string | Yes | `ACTIVE`, `DISABLED`, `TERMINATED`, `STAGED` |
| `source_system` | string | Yes | Example: `hrms-service` |
| `created_at` | string | Yes | Creation timestamp |
| `updated_at` | string | Yes | Update timestamp |

## Entity: group

Represents an IdP group.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `group_id` | string | Yes | Unique group ID |
| `group_name` | string | Yes | Unique group name |
| `group_type` | string | Yes | `SECURITY`, `APP_ACCESS`, `ADMIN`, `SYSTEM` |
| `description` | string | Yes | Business-readable group description |
| `risk_level` | string | Yes | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `status` | string | Yes | `ACTIVE`, `INACTIVE` |

## Entity: group_membership

Represents identity-to-group membership.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `membership_id` | string | Yes | Unique membership ID |
| `identity_id` | string | Yes | References identity |
| `group_id` | string | Yes | References group |
| `membership_status` | string | Yes | `ACTIVE`, `REMOVED` |
| `assigned_by` | string | Yes | Assignment source |
| `assigned_at` | string | Yes | Assignment timestamp |

## Entity: application_registration

Represents an app configured in the IdP for authentication/SSO/API client purposes.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `app_registration_id` | string | Yes | Unique registration ID |
| `app_id` | string | Yes | App identifier used across Luffy |
| `app_name` | string | Yes | Human-readable app name |
| `auth_protocol` | string | Yes | `OIDC`, `SAML`, `API_CLIENT_CREDENTIALS`, `NONE` |
| `sso_enabled` | boolean | Yes | Whether SSO/login is enabled |
| `token_audience` | string | No | Token audience for OIDC/API clients |
| `status` | string | Yes | `ACTIVE`, `INACTIVE` |

## Entity: app_assignment

Represents group-to-application login assignment.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `app_assignment_id` | string | Yes | Unique app assignment ID |
| `app_registration_id` | string | Yes | References application registration |
| `group_id` | string | Yes | Group assigned to app |
| `assignment_status` | string | Yes | `ACTIVE`, `REMOVED` |
| `assigned_at` | string | Yes | Assignment timestamp |

## Entity: machine_identity

Represents a non-human identity.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `machine_identity_id` | string | Yes | Unique machine identity ID |
| `name` | string | Yes | Machine identity name |
| `type` | string | Yes | `SERVICE_ACCOUNT`, `OAUTH_CLIENT`, `SERVICE_PRINCIPAL`, `CERTIFICATE_IDENTITY`, `DESKTOP_AGENT` |
| `owner` | string | Yes | Owning team/person |
| `used_by_service` | string | Yes | Service using this identity |
| `risk_level` | string | Yes | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `status` | string | Yes | `ACTIVE`, `INACTIVE`, `EXPIRED`, `ORPHANED` |
| `rotation_status` | string | Yes | `CURRENT`, `DUE_SOON`, `OVERDUE`, `NOT_APPLICABLE` |
| `last_used_at` | string | No | Last observed usage timestamp |

## Important distinction

```text
IdP app registration != IGA application onboarding
```

IdP answers:

```text
Can the user authenticate into the app?
Which group/client/token allows login?
```

IGA answers:

```text
Should the user have access?
Who approved access?
Can access be revoked or certified?
```
