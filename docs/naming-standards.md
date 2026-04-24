# Naming Standards

## Repository name

`luffy`

Short repository name kept as-is.

## Service naming

Use lowercase kebab-case for service folders.

```text
idp-service
iga-service
scim-target
jdbc-target
webservices-target
```

## Python package naming

Use lowercase snake_case for Python packages and modules.

```text
idp_service
iga_service
scim_target
jdbc_target
webservices_target
```

## API path naming

Use lowercase hyphenated nouns for normal REST APIs.

```text
/api/v1/users
/api/v1/roles
/api/v1/access-requests
/api/v1/provisioning-events
```

Use SCIM-standard casing only for SCIM APIs.

```text
/scim/v2/Users
/scim/v2/Groups
```

## Database naming

Use lowercase snake_case for tables, views, and columns.

Tables:

```text
users
roles
user_roles
```

IAM aggregation views:

```text
vw_iam_accounts
vw_iam_entitlements
vw_iam_account_entitlements
```

Columns:

```text
user_id
employee_id
lan_id
email
role_id
role_name
assignment_status
created_at
updated_at
```

## Object naming inside IGA

Use clear governance nouns.

```text
Identity
Account
Entitlement
Assignment
AccessRequest
Approval
ProvisioningEvent
CertificationReport
```

## Commit naming

Use short imperative commit messages.

Examples:

```text
Add JDBC target schema
Add SCIM users endpoint
Add identity aggregation job
Add account correlation logic
Add access request workflow
```

## Avoid

Avoid unclear or mixed naming such as:

```text
app1
application2
sailpointApp
dbmsApplication
webApiThing
userDataFinal
new_test_file
```
