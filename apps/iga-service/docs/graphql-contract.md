# IGA Service GraphQL Contract

## Purpose

This document defines the planned GraphQL contract for `iga-service`.

GraphQL is used because IGA data is relationship-heavy:

```text
identity -> accounts -> assignments -> entitlements -> applications -> risk -> correlation
```

## Query examples

### Get identity access

```graphql
query GetIdentityAccess($identityId: ID!) {
  identity(identityId: $identityId) {
    identityId
    displayName
    identityStatus
    accounts {
      accountId
      application {
        applicationName
      }
      assignments {
        entitlement {
          entitlementName
          riskLevel
        }
      }
    }
  }
}
```

### Get orphan accounts

```graphql
query GetOrphanAccounts {
  accounts(correlationStatus: ORPHAN) {
    accountId
    application {
      applicationName
    }
    nativeAccountId
    lanId
    email
    accountStatus
  }
}
```

### Get high-risk entitlements

```graphql
query GetHighRiskEntitlements {
  entitlements(riskLevel: CRITICAL) {
    entitlementId
    entitlementName
    application {
      applicationName
    }
    riskLevel
  }
}
```

## Planned query roots

```text
application(applicationId: ID!): Application
applications(status: ApplicationStatus): [Application!]!
identity(identityId: ID!): Identity
identityByEmployeeId(employeeId: String!): Identity
identities(status: IdentityStatus): [Identity!]!
account(accountId: ID!): Account
accounts(correlationStatus: CorrelationStatus): [Account!]!
entitlement(entitlementId: ID!): Entitlement
entitlements(riskLevel: RiskLevel): [Entitlement!]!
correlationResults(result: CorrelationResultType): [CorrelationResult!]!
```

## Planned mutation roots later

Mutations are out of scope for Milestone 1.

Future mutations may include:

```text
createAccessRequest
approveAccessRequest
rejectAccessRequest
createCertificationCampaign
submitCertificationDecision
triggerAggregation
```

High-impact mutations require human approval and audit events.

## Security controls for GraphQL

```text
Authentication
Role-based authorization
Object-level authorization
Query depth limits
Query complexity limits
Pagination limits
No silent provisioning mutations
Audit high-risk queries and mutations
```
