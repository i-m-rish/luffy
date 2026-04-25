# IdP Service GraphQL Contract

## Purpose

This document defines the planned GraphQL contract for `idp-service`.

GraphQL is used because IdP data is highly connected:

```text
identity -> groups -> app assignments -> app registrations
machine identity -> owner -> used by service -> risk/rotation status
```

## Query examples

### Get identity with groups

```graphql
query GetIdentity($identityId: ID!) {
  identity(identityId: $identityId) {
    identityId
    employeeId
    lanId
    email
    displayName
    identityStatus
    groups {
      groupId
      groupName
      groupType
      riskLevel
    }
  }
}
```

### Get application registration and login groups

```graphql
query GetApplication($appId: String!) {
  applicationRegistration(appId: $appId) {
    appRegistrationId
    appId
    appName
    authProtocol
    ssoEnabled
    assignedGroups {
      groupId
      groupName
      riskLevel
    }
  }
}
```

### Get machine identities by risk

```graphql
query GetMachineIdentities($riskLevel: RiskLevel) {
  machineIdentities(riskLevel: $riskLevel) {
    machineIdentityId
    name
    type
    owner
    usedByService
    riskLevel
    status
    rotationStatus
  }
}
```

## Planned query roots

```text
identity(identityId: ID!): Identity
identityByEmployeeId(employeeId: String!): Identity
identities(status: IdentityStatus): [Identity!]!
group(groupId: ID!): Group
groups(groupType: GroupType): [Group!]!
applicationRegistration(appId: String!): ApplicationRegistration
applicationRegistrations(status: Status): [ApplicationRegistration!]!
machineIdentity(machineIdentityId: ID!): MachineIdentity
machineIdentities(riskLevel: RiskLevel): [MachineIdentity!]!
```

## Planned mutation roots later

Mutations are out of scope for Milestone 1.

Future mutations may include:

```text
createGroup
assignIdentityToGroup
registerApplication
assignGroupToApplication
registerMachineIdentity
updateMachineIdentityRotationStatus
```

All mutations must require admin authorization and audit events.

## Security controls for GraphQL

```text
Object-level authorization
Field-level authorization for sensitive fields
Query depth limits
Query complexity limits
No secret/token/private key fields
Disable unrestricted introspection outside local/dev mode later
Audit high-risk queries and mutations
```

## IGA usage

`iga-service` will later use IdP GraphQL to aggregate:

```text
identities
groups
group memberships
app registrations
app assignments
machine identities
```

## Important distinction

GraphQL here is for relationship queries and aggregation.

It is not a replacement for OIDC/SAML authentication protocols.
