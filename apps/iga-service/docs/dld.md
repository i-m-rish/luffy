# IGA Service DLD

## Detailed design

`iga-service` starts as a normalized JSON-backed service in Milestone 1.

It will later become a Python GraphQL service with aggregation, request, approval, certification, and provisioning simulation.

## Modules

Milestone 1 expected files:

```text
data/application-catalog.json
data/identities-normalized.json
data/accounts-normalized.json
data/entitlements-normalized.json
data/assignments-normalized.json
data/correlation-results.json
graphql/schema.graphql
graphql/example-queries.graphql
scripts/validate_iga_data.py
```

Future modules:

```text
src/models.py              -> IGA object models
src/repository.py          -> data access layer
src/aggregation.py         -> source aggregation simulation
src/correlation.py         -> identity/account matching
src/graphql_api.py         -> GraphQL schema/resolvers
src/access_request.py      -> request/approval simulation
src/certification.py       -> access review simulation
src/provisioning.py        -> provisioning command simulation
src/audit.py               -> audit event creation
```

## Processing flow

### Aggregation

```text
1. Read identities from HRMS/IdP-style sources.
2. Read accounts and entitlements from target apps.
3. Normalize source data into IGA objects.
4. Store normalized identity, account, entitlement, and assignment records.
```

### Correlation

```text
1. Take account record from target application.
2. Try employee_id match.
3. If not matched, try lan_id match.
4. If not matched, try email match.
5. Produce MATCHED, PARTIAL, or ORPHAN correlation result.
```

### Governance visibility

```text
1. Join identity -> account -> assignment -> entitlement -> application.
2. Preserve risk level from application/entitlement.
3. Flag orphan accounts and high-risk access.
4. Prepare for future certification and access review.
```

## Validation rules

### applications

```text
application_id required and unique
integration_pattern required
status must be ACTIVE, INACTIVE, DESIGN, or FUTURE
risk_level must be LOW, MEDIUM, HIGH, or CRITICAL
```

### identities

```text
identity_id required and unique
employee_id required and unique for human identities
identity_status must be ACTIVE, DISABLED, TERMINATED, or STAGED
```

### accounts

```text
account_id required and unique
application_id must reference application catalog
account_status must be ACTIVE, DISABLED, LOCKED, or TERMINATED
correlation_status must be MATCHED, PARTIAL, ORPHAN, or NOT_EVALUATED
```

### entitlements

```text
entitlement_id required and unique
application_id must reference application catalog
risk_level must be LOW, MEDIUM, HIGH, or CRITICAL
status must be ACTIVE or INACTIVE
```

### assignments

```text
assignment_id required and unique
account_id must reference accounts
entitlement_id must reference entitlements
assignment_status must be ACTIVE or REVOKED
```

### correlation_results

```text
correlation_id required and unique
account_id must reference accounts
result must be MATCHED, PARTIAL, or ORPHAN
match_attribute must be employee_id, lan_id, email, or NONE
```

## Security decision points

```text
IGA does not authenticate users like an IdP.
IGA does not own employment lifecycle like HRMS.
IGA governs access and decisions.
High-risk assignments must be visible.
Orphan accounts must be visible.
Future provisioning requires explicit approval.
```
