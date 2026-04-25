# Luffy Roadmap

## Milestone 1 - IAM Foundation

Goal:

```text
HRMS worker -> IdP identity -> IGA normalized identity/account/entitlement -> JDBC correlation report
```

Scope:

```text
jdbc-target
hrms-service
idp-service with basic GraphQL model
iga-service with basic GraphQL model
```

## Milestone 2 - Connector Patterns

Goal:

```text
Show REST, SCIM, and PAM onboarding/governance patterns.
```

Scope:

```text
webservices-target
scim-target as SaaS app
pam-target
```

## Milestone 3 - API Security and Detection

Goal:

```text
API posture checks, monitor/enforce mode, findings, alerts, and detection rules.
```

Scope:

```text
api-security-gateway
siem-detection-service
```

## Milestone 4 - Endpoint and Machine Identity

Goal:

```text
Device identity, certificates, service accounts, OAuth clients, token/secret ownership, and rotation status.
```

Scope:

```text
desktop-agent-app
machine identity governance inside idp-service and iga-service
```

## Milestone 5 - AI Agents

Goal:

```text
Agents explain risks, suggest reviews, summarize onboarding gaps, and recommend remediation.
```

Scope:

```text
IAM review agent
App onboarding agent
API security agent
Certification recommendation agent
Machine identity risk agent
```

## Current focus

```text
Finish jdbc-target foundation and tests.
Then start hrms-service design package.
```
