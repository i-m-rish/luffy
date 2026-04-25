# IdP Service Objectives

## Service name

`idp-service`

## Simulated platform type

Identity Provider.

Examples of real-world platform categories:

```text
Microsoft Entra ID
Okta
Ping Identity
Keycloak
```

## Primary learning objective

Learn how a digital identity provider represents identities, groups, app registrations, login assignments, tokens, and machine identities.

## What this service teaches

```text
Digital identity model
Groups and memberships
SSO app registration
OIDC/SAML/API client concepts
App login assignment
Machine identity / non-human identity basics
Difference between IdP registration and IGA onboarding
```

## Milestone 1 scope

Milestone 1 creates:

```text
IdP design package
GraphQL schema design
sample identity data later
group and app registration data later
machine identity sample data later
validation tests later
```

## Out of scope for Milestone 1

```text
Real authentication
Real tokens
Real SSO
Real OAuth secrets
Real certificates
Production federation
Full admin UI
```

## Future scope

Later versions may add:

```text
REST login/token mock
GraphQL resolver implementation
identity sync from hrms-service
group assignment simulation
machine identity governance feed to iga-service
minimal IdP admin UI
```
