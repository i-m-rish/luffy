# JDBC Target SQL View Contract

## Purpose

This document defines the contract between `jdbc-target` and the future `iga-service` JDBC aggregation logic.

IGA should read IAM-safe views, not raw application tables.

## Account aggregation view

View:

```text
vw_iam_accounts
```

Fields:

```text
account_id
employee_id
lan_id
email
display_name
department
account_status
active
created_at
updated_at
```

## Entitlement aggregation view

View:

```text
vw_iam_entitlements
```

Fields:

```text
entitlement_id
entitlement_code
entitlement_name
entitlement_description
risk_level
entitlement_status
active
created_at
updated_at
```

## Account-entitlement aggregation view

View:

```text
vw_iam_account_entitlements
```

Fields:

```text
assignment_id
account_id
employee_id
lan_id
email
entitlement_id
entitlement_code
entitlement_name
risk_level
assignment_status
assigned_by
assigned_at
revoked_by
revoked_at
assignment_reason
```

## Correlation guidance

Preferred matching order:

```text
1. employee_id
2. lan_id
3. email
```

## IGA assumptions

```text
account_id is the native account identifier for jdbc-target.
entitlement_id is the native entitlement identifier for jdbc-target.
active is a string value in Milestone 1: true/false.
risk_level should be preserved into IGA entitlement catalog.
```

## Security rule

IGA should not query:

```text
users
roles
user_roles
```

IGA should query only:

```text
vw_iam_accounts
vw_iam_entitlements
vw_iam_account_entitlements
```
