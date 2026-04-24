# Application Registration Model

## Core principle

All applications in the Luffy IAM Lab should be represented in both:

```text
idp-service
iga-service
```

But they are represented for different reasons.

```text
idp-service
  -> Knows applications for authentication, SSO, tokens, clients, and app assignments.

iga-service
  -> Knows applications for governance, account aggregation, entitlement aggregation, access requests, approvals, provisioning, certification, and audit.
```

## Why both are needed

An application can be present in the IdP but still not be fully governed.

Example:

```text
Application exists in IdP for SSO.
Users can authenticate into the app.
But SailPoint/IGA still needs to know:
- Which accounts exist in the app?
- Which entitlements exist?
- Who has what access?
- Who approved that access?
- Can access be provisioned or revoked?
- Can access be certified?
```

So IdP registration is not the same as IGA onboarding.

## App registration in idp-service

The IdP registration should represent authentication and SSO configuration.

### IdP application object

```text
app_id
app_name
app_type
sso_enabled
auth_protocol
redirect_uris
token_audience
assigned_groups
status
```

### Supported auth protocols

```text
OIDC
SAML
API_CLIENT_CREDENTIALS
NONE
```

### Example IdP app records

```text
sec-endpoint-scim
  app_name: Endpoint Security Console
  auth_protocol: OIDC
  sso_enabled: true

sec-risk-api
  app_name: Security Risk and Incident Portal
  auth_protocol: OIDC
  sso_enabled: true

pam-target
  app_name: Privileged Access Management
  auth_protocol: SAML
  sso_enabled: true

luffy-iga
  app_name: Luffy IGA Governance
  auth_protocol: OIDC
  sso_enabled: true
```

## App onboarding in iga-service

The IGA registration should represent governance and integration configuration.

### IGA application object

```text
application_id
application_name
business_owner
technical_owner
integration_pattern
source_system
account_schema
entitlement_schema
correlation_rule
provisioning_supported
certification_required
risk_level
status
```

### Supported integration patterns

```text
HRMS_SOURCE
IDP_SOURCE
JDBC
WEB_SERVICES
SCIM
PAM
API_SECURITY_POSTURE
SIEM_EVENTS
```

### Example IGA app records

```text
hrms-service
  integration_pattern: HRMS_SOURCE
  purpose: identity lifecycle source

idp-service
  integration_pattern: IDP_SOURCE
  purpose: digital identity source

jdbc-target
  integration_pattern: JDBC
  purpose: account and entitlement aggregation from database views

webservices-target
  integration_pattern: WEB_SERVICES
  purpose: REST API aggregation and provisioning

scim-target
  integration_pattern: SCIM
  purpose: SCIM user/group aggregation and provisioning

pam-target
  integration_pattern: PAM
  purpose: privileged access governance

api-gateway-waf
  integration_pattern: API_SECURITY_POSTURE
  purpose: API posture findings and enforcement events

siem-detection-service
  integration_pattern: SIEM_EVENTS
  purpose: security alerts and detection events
```

## Which apps go where

| Service | In IdP? | In IGA? | Reason |
|---|---|---|---|
| `hrms-service` | Optional | Yes | HRMS is authoritative lifecycle source; not always SSO app |
| `idp-service` | No, it is the IdP | Yes | IGA aggregates identities/groups from IdP |
| `iga-service` | Yes | Self-registered | Users log in to IGA; IGA also governs its own admin access later |
| `jdbc-target` | Optional | Yes | May not have SSO; definitely has accounts/roles to govern |
| `webservices-target` | Yes | Yes | Has login/API access and governable roles |
| `scim-target` | Yes | Yes | Has SSO and SCIM users/groups |
| `pam-target` | Yes | Yes | Has SSO and privileged access governance |
| `api-gateway-waf` | Yes | Yes | Admin console access is governed; findings are monitored |
| `siem-detection-service` | Yes | Yes | Analyst/admin console access is governed; alerts are consumed |

## Correct mental model

```text
IdP answers:
Can the user authenticate into this app?
Which token/client/group allows login?

IGA answers:
Should the user have access?
What access do they have?
Who approved it?
Can it be removed?
Can it be certified?
Is it high risk?
```

## End-to-end example

### User requests access to Endpoint Security Console

```text
1. App exists in idp-service for SSO.
2. App exists in iga-service for governance.
3. User requests Detection Analyst access in iga-service.
4. Manager/app owner approves.
5. iga-service provisions group membership to scim-target.
6. IdP may also assign SSO group if required.
7. User logs in through idp-service.
8. scim-target authorizes user based on provisioned group/role.
9. siem-detection-service receives audit events.
```

## Important rule

Do not treat IdP group assignment as full governance by itself.

IdP group assignment may provide login or app role mapping, but IGA must still track:

```text
request
approval
provisioning
audit
certification
revocation
```

## Implementation recommendation

Create two separate registries:

```text
idp-service/app-registry.json
iga-service/application-catalog.json
```

The same application may appear in both, but with different attributes.

IdP registry focuses on authentication.
IGA catalog focuses on governance.
