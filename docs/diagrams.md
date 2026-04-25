# Luffy Global Mermaid Diagrams

This document contains global system-level Mermaid diagrams for the Luffy cybersecurity IAM lab.

Detailed service-specific diagrams should live inside each service folder, for example:

```text
apps/jdbc-target/docs/diagrams.md
apps/hrms-service/docs/diagrams.md
apps/idp-service/docs/diagrams.md
apps/iga-service/docs/diagrams.md
```

See also:

```text
docs/diagram-strategy.md
```

## Diagram index

```text
1. System context diagram
2. Container/service architecture
3. Milestone 1 foundation flow
4. Identity lifecycle and aggregation sequence
5. Access request and provisioning sequence
6. API security and SIEM overview
7. UI/module map
8. Future AI agent layer
```

---

## 1. System Context Diagram

```mermaid
flowchart LR
    USER[Human User<br/>Employee / Manager / App Owner]
    ADMIN[Security Admin / IAM Analyst]
    AGENT[Future AI Agents]

    LUFFY[Luffy IAM Lab]

    USER -->|request access / review access| LUFFY
    ADMIN -->|configure apps / review risks| LUFFY
    AGENT -->|recommend / summarize / flag risk| LUFFY

    LUFFY -->|governs access through| IGA[IGA Governance Layer]
    LUFFY -->|uses lifecycle data from| HRMS[HRMS Source]
    LUFFY -->|uses digital identity from| IDP[IdP Source]
    LUFFY -->|aggregates access from| TARGETS[Target Apps<br/>JDBC / REST / SCIM / PAM]
    LUFFY -->|monitors| SECURITY[API Security + SIEM]
```

---

## 2. Container / Service Architecture

```mermaid
flowchart LR
    HRMS[hrms-service<br/>Worker lifecycle source]
    IDP[idp-service<br/>GraphQL<br/>Identities / Groups / Apps / NHI]
    IGA[iga-service<br/>GraphQL<br/>Governance / Correlation / Catalog]

    JDBC[jdbc-target<br/>SQL / JDBC<br/>Security Asset Ops]
    WS[webservices-target<br/>REST + Cloud DB later<br/>Risk Portal]
    SCIM[scim-target<br/>SaaS + SCIM 2.0<br/>Endpoint Security]
    PAM[pam-target<br/>REST/PAM APIs<br/>Safes / Checkout / Sessions]

    APIGW[api-security-gateway<br/>Posture / Monitor / Enforce]
    SIEM[siem-detection-service<br/>Events / Alerts / Detections]
    DESKTOP[desktop-agent-app<br/>Device Posture / Heartbeat]

    HRMS -->|worker lifecycle / employment status| IGA
    HRMS -->|worker attributes later| IDP
    IDP -->|digital identities, groups, app registrations, NHI| IGA
    JDBC -->|accounts, entitlements, assignments| IGA

    IGA -->|future REST aggregation/provisioning| WS
    IGA -->|future SCIM provisioning| SCIM
    IGA -->|future PAM governance| PAM

    DESKTOP -->|device heartbeat later| SCIM
    DESKTOP -->|machine identity evidence later| IGA

    APIGW -. posture scan .-> IDP
    APIGW -. posture scan .-> IGA
    APIGW -. posture scan .-> WS
    APIGW -. posture scan .-> SCIM
    APIGW -. posture scan .-> PAM

    IDP -->|auth/security events later| SIEM
    IGA -->|governance audit events later| SIEM
    JDBC -->|aggregation findings later| SIEM
    WS -->|API events later| SIEM
    SCIM -->|SCIM provisioning events later| SIEM
    PAM -->|privileged access audit later| SIEM
    APIGW -->|findings / posture score later| SIEM
```

---

## 3. Milestone 1 Foundation Flow

```mermaid
flowchart LR
    HRMS_DATA[hrms-service<br/>workers / departments / positions / lifecycle events]
    IDP_DATA[idp-service<br/>identities / groups / app registrations / machine identities]
    JDBC_DATA[jdbc-target<br/>users / roles / user_roles / IAM views]
    IGA_DATA[iga-service<br/>application catalog / normalized identities / accounts / entitlements / correlation]

    HRMS_DATA -->|employment truth| IGA_DATA
    IDP_DATA -->|digital identity truth| IGA_DATA
    JDBC_DATA -->|target app access truth| IGA_DATA

    IGA_DATA --> GOVERNANCE[Governance visibility<br/>who has what access / matched vs orphan / high-risk access]
```

---

## 4. Identity Lifecycle and Aggregation Sequence

```mermaid
sequenceDiagram
    participant HRMS as hrms-service
    participant IDP as idp-service
    participant JDBC as jdbc-target
    participant IGA as iga-service
    participant SIEM as siem-detection-service later

    HRMS->>HRMS: Maintain worker and lifecycle events
    HRMS->>IDP: Sync worker attributes later
    IDP->>IDP: Maintain digital identities, groups, app registrations, NHI
    HRMS->>IGA: Provide worker/lifecycle context
    IDP->>IGA: Provide identity/group/app registration data
    JDBC->>IGA: Provide account, entitlement, and assignment data
    IGA->>IGA: Normalize identities, accounts, entitlements, assignments
    IGA->>IGA: Correlate accounts using employee_id, lan_id, email
    IGA->>IGA: Detect matched, partial, and orphan accounts
    IGA->>SIEM: Send lifecycle/correlation audit event later
```

---

## 5. Access Request and Provisioning Sequence

```mermaid
sequenceDiagram
    participant User as Requester
    participant IGA as iga-service
    participant Manager as Manager/App Owner
    participant Gateway as api-security-gateway
    participant SCIM as scim-target
    participant PAM as pam-target
    participant SIEM as siem-detection-service

    User->>IGA: Request access later
    IGA->>IGA: Validate identity, app, entitlement, risk
    IGA->>Manager: Route approval
    Manager->>IGA: Approve / reject

    alt Approved SCIM access later
        IGA->>Gateway: Send provisioning action for inspection
        Gateway->>Gateway: Check auth, risk, allowlist, payload
        Gateway->>SCIM: Forward allowed SCIM group assignment
        SCIM->>SIEM: Send provisioning event
    end

    alt Approved PAM access later
        IGA->>Gateway: Send PAM safe membership action
        Gateway->>Gateway: Require step-up if critical
        Gateway->>PAM: Forward allowed safe membership change
        PAM->>SIEM: Send privileged access event
    end

    IGA->>SIEM: Send access request audit event
```

---

## 6. API Security and SIEM Overview

```mermaid
flowchart LR
    CALLER[Caller / Service / User]
    MODE{API_SECURITY_MODE}
    DIRECT[Direct Mode]
    GATEWAY[api-security-gateway]
    TARGET[Protected API App]
    SIEM[siem-detection-service]

    CALLER --> MODE
    MODE -->|direct| DIRECT --> TARGET
    MODE -->|gateway-monitor| GATEWAY
    MODE -->|gateway-enforce| GATEWAY

    GATEWAY --> CHECKS[Posture + Runtime Checks<br/>TLS / Auth / Headers / CORS / Payload / Policy]
    CHECKS --> DECISION{Decision}

    DECISION -->|ALLOW| TARGET
    DECISION -->|ALLOW_WITH_FINDING| TARGET
    DECISION -->|BLOCK| BLOCKED[Request blocked]
    DECISION -->|RATE_LIMIT| LIMITED[Rate limited]
    DECISION -->|REQUIRE_STEP_UP| STEPUP[Step-up / approval required]

    GATEWAY -->|findings / posture score| SIEM
    TARGET -->|audit events| SIEM
    SIEM --> ALERTS[Alerts / detections / investigations]
```

---

## 7. UI / Module Map

```mermaid
flowchart TD
    CONSOLE[luffy-console<br/>future unified UI]

    IGA_UI[IGA Module<br/>application catalog / identities / accounts / access / correlation]
    IDP_UI[IdP Module<br/>identities / groups / app registrations / NHI]
    HRMS_UI[HRMS Module<br/>workers / lifecycle events]
    PAM_UI[PAM Module<br/>safes / checkout / sessions]
    API_UI[API Security Module<br/>posture / findings / policies]
    SIEM_UI[SIEM Module<br/>events / alerts / investigations]
    AGENT_UI[Agents Module<br/>recommendations / evidence]

    CONSOLE --> IGA_UI
    CONSOLE --> IDP_UI
    CONSOLE --> HRMS_UI
    CONSOLE --> PAM_UI
    CONSOLE --> API_UI
    CONSOLE --> SIEM_UI
    CONSOLE --> AGENT_UI
```

---

## 8. Future AI Agent Layer

```mermaid
flowchart TD
    DATA[Governed Data<br/>Identities / Accounts / Entitlements / Requests / Findings]
    AGENTS[AI Agent Layer]

    REVIEW[IAM Review Agent]
    ONBOARD[App Onboarding Agent]
    APISEC[API Security Agent]
    CERT[Certification Recommendation Agent]
    NHI[Machine Identity Risk Agent]

    HUMAN[Human Reviewer / Owner]
    IGA[iga-service]

    DATA --> AGENTS
    AGENTS --> REVIEW
    AGENTS --> ONBOARD
    AGENTS --> APISEC
    AGENTS --> CERT
    AGENTS --> NHI

    REVIEW -->|recommendation + evidence| HUMAN
    ONBOARD -->|questions + integration gaps| HUMAN
    APISEC -->|posture risk summary| HUMAN
    CERT -->|approve/revoke recommendation| HUMAN
    NHI -->|secret/cert/token risk| HUMAN

    HUMAN -->|explicit approval only| IGA
```
