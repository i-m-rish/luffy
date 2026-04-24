# Luffy

Luffy is a cybersecurity IAM learning lab for building smaller versions of real identity, governance, privileged access, API security, and detection platforms.

The project is designed to teach SailPoint-style IGA concepts, IdP concepts, HRMS-driven identity lifecycle, multiple application onboarding patterns, API security posture, machine identity governance, and future AI-agent assisted reviews.

## Core principle

Use the right integration pattern for each service.

```text
GraphQL where relationships are complex.
REST/SCIM/SQL where those patterns are realistic.
Agents later, after clean data and APIs exist.
```

## Services

| Service | Acts like | Main API/data style | Purpose |
|---|---|---|---|
| `hrms-service` | Workday / SAP SuccessFactors / Oracle HCM | REST + database later | Employee lifecycle source: joiner, mover, leaver |
| `idp-service` | Entra ID / Okta | GraphQL + REST login | Digital identities, groups, app registrations, machine identities |
| `iga-service` | SailPoint-like IGA | GraphQL | Aggregation, correlation, request, approval, provisioning, certification |
| `jdbc-target` | DB/JDBC legacy app | SQL database | Security asset app with users, roles, mappings, IAM views |
| `webservices-target` | Custom cloud/security risk app | REST + cloud DB later | REST/Web Services connector pattern |
| `scim-target` | SaaS endpoint security app | SCIM 2.0 | SaaS provisioning pattern using users/groups |
| `pam-target` | CyberArk-like PAM | REST + audit data | Safes, privileged accounts, checkout, sessions, audit |
| `api-security-gateway` | API security posture gateway | REST | SSL/TLS, auth, headers, CORS, posture scan, monitor/enforce |
| `siem-detection-service` | SIEM/detection platform | Event ingestion API | Events, alerts, detections, investigations |
| `desktop-agent-app` | Endpoint desktop agent | Desktop/client app later | Device posture, heartbeat, machine identity, local events |

## Target structure

```text
luffy/
├── apps/
│   ├── hrms-service/
│   ├── idp-service/
│   ├── iga-service/
│   ├── jdbc-target/
│   ├── webservices-target/
│   ├── scim-target/
│   ├── pam-target/
│   ├── api-security-gateway/
│   ├── siem-detection-service/
│   └── desktop-agent-app/
├── docs/
├── scripts/
├── tests/
└── README.md
```

## GraphQL decision

Use GraphQL in:

```text
idp-service
iga-service
```

Reason:

```text
IdP and IGA data is highly connected:
Identity -> groups -> apps -> accounts -> entitlements -> approvals -> risks.
```

Do not force GraphQL into every target app. Target apps should keep their realistic integration style:

```text
jdbc-target            -> SQL/JDBC
webservices-target     -> REST
scim-target            -> SCIM
pam-target             -> REST/PAM-style APIs
api-security-gateway   -> REST
siem-detection         -> event API
```

## Build order

### Milestone 1 - IAM foundation

```text
1. jdbc-target
2. hrms-service
3. idp-service with basic GraphQL model
4. iga-service with basic GraphQL model
```

Goal:

```text
HRMS worker -> IdP identity -> IGA normalized identity/account/entitlement -> JDBC correlation report
```

### Milestone 2 - Additional connector patterns

```text
5. webservices-target
6. scim-target as SaaS app
7. pam-target
```

Goal:

```text
Show REST, SCIM, and PAM onboarding/governance patterns.
```

### Milestone 3 - Security control and detection

```text
8. api-security-gateway
9. siem-detection-service
```

Goal:

```text
API posture checks, monitor/enforce mode, findings, alerts, detection rules.
```

### Milestone 4 - Endpoint and machine identity

```text
10. desktop-agent-app
11. machine identity governance inside idp-service and iga-service
```

Goal:

```text
Device identity, certificates, service accounts, OAuth clients, token/secret ownership and rotation status.
```

### Milestone 5 - AI agents

```text
12. IAM review agent
13. app onboarding agent
14. API security agent
15. certification recommendation agent
16. machine identity risk agent
```

Goal:

```text
Agents explain risks, suggest reviews, summarize onboarding gaps, and recommend remediation.
```

## Documentation

- [Architecture](docs/architecture.md)
- [Naming Standards](docs/naming-standards.md)
- [App Registration Model](docs/app-registration-model.md)
- [HRMS Service](docs/hrms-service.md)
- [PAM Target](docs/pam-target.md)
- [Security Control Plane](docs/security-control-plane.md)
- [Learning Strategy](docs/learning-strategy.md)
