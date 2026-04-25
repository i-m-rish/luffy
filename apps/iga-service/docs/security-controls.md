# IGA Service Security Controls

## Security posture

`iga-service` is the governance and decision layer.

It must be designed carefully because future versions may recommend or trigger access changes.

## Controls

### Separation of duties

```text
Requester should not auto-approve own request.
Approver/reviewer/admin roles must be separated later.
High-risk access requires explicit approval.
Future AI agents can recommend, not silently approve/provision/revoke.
```

### Least privilege

```text
Read-only aggregation access to source systems by default.
Provisioning access must be separated from read aggregation.
Future GraphQL users should only see authorized identities/apps.
```

### Data minimization

IGA should store only governance-relevant identity/access fields.

Avoid:

```text
salary
national ID
home address
real secrets
real tokens
real passwords
private keys
```

### Correlation safety

```text
employee_id match = high confidence
lan_id match = medium confidence
email match = low confidence
no match = orphan
```

Do not auto-remediate orphan accounts in Milestone 1.

### High-risk access visibility

The model must preserve:

```text
application risk
entitlement risk
assignment status
correlation status
```

### Future GraphQL security

```text
authentication
role-based authorization
object-level authorization
query depth limits
query complexity limits
pagination limits
audit for high-risk queries/mutations
```

## Risk conditions to detect later

```text
orphan account with active access
terminated identity with active account
critical entitlement assigned to active account
high-risk app without owner
assignment to inactive entitlement
account without correlation result
```
