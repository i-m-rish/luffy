# IdP Service Security Controls

## Security posture

`idp-service` represents the digital identity and authentication layer.

Even in the lab, it must be designed as if identity data and authentication metadata are sensitive.

## Controls

### No real secrets

Do not store:

```text
real passwords
real OAuth client secrets
real private keys
real certificates
real tokens
production issuer URLs
```

Use placeholders only.

### Least privilege

Future access model:

```text
iga-service can read identities, groups, app registrations, and machine identity metadata.
Only IdP admins can create groups or register apps.
Only security admins can manage machine identity records.
Normal users cannot view other users' sensitive identity data.
```

### GraphQL security

Future GraphQL implementation must include:

```text
authentication
object-level authorization
field-level authorization for sensitive fields
query depth limits
query complexity limits
pagination limits
no secret/token/private key fields
restricted introspection outside local/dev mode
```

### App registration security

```text
Auth protocol must be explicit.
SSO-enabled apps must have a defined token audience or protocol metadata later.
Inactive app registrations should not be assignable.
High-risk app groups should be visible to IGA.
```

### Machine identity security

Machine identities must have:

```text
owner
used_by_service
risk_level
status
rotation_status
last_used_at when available
```

Risk conditions:

```text
orphaned machine identity
overdue rotation
expired certificate identity
high-risk OAuth client without owner
unused service principal still active
```

### Auditability

Audit later:

```text
identity created/disabled
group created/updated
group membership changed
application registered/disabled
app assignment changed
machine identity created/updated
rotation status changed
```
