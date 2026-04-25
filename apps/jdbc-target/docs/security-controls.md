# JDBC Target Security Controls

## Security posture

`jdbc-target` is database-first and should be treated as a protected internal application data source.

## Controls

### Least privilege

```text
IGA should read only IAM-safe views.
IGA should not read raw users, roles, or user_roles tables directly.
Future DB user for IGA should be read-only.
```

### Data protection

```text
No real employee data.
No real secrets.
No passwords.
No tokens.
No production URLs.
```

### Database safety

```text
Use parameterized queries in future scripts.
Avoid unsafe dynamic SQL.
Keep raw tables separate from IAM aggregation views.
Use constraints for allowed status/risk values.
```

### Access governance

```text
High-risk and critical roles must be visible through IAM views.
Entitlement descriptions must be business-readable.
Assignments must include assigned_by and assigned_at.
```

### Future controls

```text
Read-only DB account for IGA.
Connection encryption for non-local DB deployments.
Database audit logging.
Secret scanning for config files.
Dependency scanning for future scripts.
```

## Risk conditions to detect later

```text
Orphan account with active access.
Critical entitlement assigned without approval.
Inactive account with active role assignment.
Role missing business description.
Account missing correlation attributes.
```
