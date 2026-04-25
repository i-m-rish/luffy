# IdP Service DLD

## Detailed design

`idp-service` starts as a JSON-backed design-first service in Milestone 1.

It will later become a Python GraphQL service with a small REST login/token simulation.

## Modules

Milestone 1 expected files:

```text
data/identities.json
data/groups.json
data/group-memberships.json
data/app-registrations.json
data/app-assignments.json
data/machine-identities.json
graphql/schema.graphql
graphql/example-queries.graphql
```

Future modules:

```text
src/models.py          -> identity, group, app registration, machine identity models
src/repository.py      -> data access layer
src/graphql_api.py     -> GraphQL schema/resolvers
src/auth.py            -> mock login/token behavior
src/audit.py           -> audit event creation
```

## Processing flow

### Identity sync

```text
1. Worker exists in hrms-service.
2. IdP creates digital identity later.
3. Identity is assigned to groups.
4. Groups may grant app login.
5. IGA aggregates identities, groups, app registrations, and assignments.
```

### App registration

```text
1. Application is registered in IdP.
2. Auth protocol is defined: OIDC, SAML, API_CLIENT_CREDENTIALS, or NONE.
3. Groups are assigned to the app.
4. IGA separately onboards the app for governance.
```

### Machine identity

```text
1. Service account/OAuth client/service principal is registered.
2. Owner and risk level are assigned.
3. Rotation and expiry metadata are tracked later.
4. IGA aggregates machine identities for governance.
```

## Validation rules

### identities

```text
identity_id required and unique
employee_id required and unique for human identities
email required and unique for human identities
identity_status must be ACTIVE, DISABLED, TERMINATED, or STAGED
```

### groups

```text
group_id required and unique
group_name required and unique
group_type must be SECURITY, APP_ACCESS, ADMIN, or SYSTEM
status must be ACTIVE or INACTIVE
```

### app_registrations

```text
app_registration_id required and unique
app_id required and unique
auth_protocol must be OIDC, SAML, API_CLIENT_CREDENTIALS, or NONE
sso_enabled must be true or false
status must be ACTIVE or INACTIVE
```

### machine_identities

```text
machine_identity_id required and unique
type must be SERVICE_ACCOUNT, OAUTH_CLIENT, SERVICE_PRINCIPAL, CERTIFICATE_IDENTITY, or DESKTOP_AGENT
owner required
risk_level must be LOW, MEDIUM, HIGH, or CRITICAL
status must be ACTIVE, INACTIVE, EXPIRED, or ORPHANED
```

## Security decision points

```text
Do not store real secrets.
Do not expose token values.
Do not use real certificates.
GraphQL must enforce object-level authorization later.
Machine identities require owner and risk metadata.
```
