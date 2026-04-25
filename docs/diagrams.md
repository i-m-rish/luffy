# Luffy Diagrams

This document contains Mermaid diagrams for the Luffy cybersecurity IAM lab.

## 1. High-Level Architecture

```mermaid
flowchart LR
    HRMS[hrms-service<br/>HRMS / Worker Lifecycle]
    IDP[idp-service<br/>GraphQL + REST Login<br/>Identities / Groups / Apps]
    IGA[iga-service<br/>GraphQL IGA<br/>Aggregation / Correlation / Governance]

    JDBC[jdbc-target<br/>SQL / JDBC<br/>Security Asset Operations]
    WS[webservices-target<br/>REST + Cloud DB Later<br/>Security Risk Portal]
    SCIM[scim-target<br/>SaaS + SCIM 2.0<br/>Endpoint Security Console]
    PAM[pam-target<br/>PAM REST APIs<br/>Safes / Checkout / Sessions]

    APIGW[api-security-gateway<br/>Posture Scan / Monitor / Enforce]
    SIEM[siem-detection-service<br/>Events / Alerts / Detections]
    DESKTOP[desktop-agent-app<br/>Device Posture / Heartbeat<br/>Machine Identity Later]

    HRMS -->|worker lifecycle| IDP
    IDP -->|identity, groups, app registrations| IGA

    IGA -->|JDBC aggregation| JDBC
    IGA -->|REST aggregation/provisioning| WS
    IGA -->|SCIM provisioning| SCIM
    IGA -->|PAM governance| PAM

    DESKTOP -->|device heartbeat / local events later| SCIM
    DESKTOP -->|machine identity evidence later| IGA

    APIGW -. posture scan .-> IDP
    APIGW -. posture scan .-> IGA
    APIGW -. posture scan .-> WS
    APIGW -. posture scan .-> SCIM
    APIGW -. posture scan .-> PAM

    IDP -->|security events| SIEM
    IGA -->|audit events| SIEM
    JDBC -->|access data findings later| SIEM
    WS -->|API events| SIEM
    SCIM -->|SCIM events| SIEM
    PAM -->|privileged session audit| SIEM
    APIGW -->|findings / blocks / posture score| SIEM
```

## 2. Identity Lifecycle and Governance Flow

```mermaid
sequenceDiagram
    participant HRMS as hrms-service
    participant IDP as idp-service
    participant IGA as iga-service
    participant JDBC as jdbc-target
    participant SCIM as scim-target
    participant PAM as pam-target
    participant SIEM as siem-detection-service

    HRMS->>HRMS: Create JOINER lifecycle event
    HRMS->>IDP: Sync worker identity attributes
    IDP->>IDP: Create digital identity and groups
    IDP->>IGA: Identity aggregation
    JDBC->>IGA: Account and entitlement aggregation through IAM views
    IGA->>IGA: Correlate account to identity
    IGA->>IGA: Evaluate birthright / requested access
    IGA->>IGA: Route approval if required
    IGA->>SCIM: Provision SaaS group membership if approved
    IGA->>PAM: Provision PAM safe membership if approved
    IGA->>SIEM: Send governance audit event
    SCIM->>SIEM: Send provisioning event
    PAM->>SIEM: Send privileged access audit event
```

## 3. App Registration Model

```mermaid
flowchart TD
    APP[Application]

    IDPREG[IdP App Registration<br/>Authentication / SSO / Tokens]
    IGAREG[IGA Application Catalog<br/>Governance / Aggregation / Provisioning]

    APP --> IDPREG
    APP --> IGAREG

    IDPREG --> AUTH[Can the user authenticate?]
    IDPREG --> TOKEN[Which token/client/group allows login?]

    IGAREG --> ACCESS[Should the user have access?]
    IGAREG --> ENT[What entitlements exist?]
    IGAREG --> APPROVAL[Who approved access?]
    IGAREG --> REVOCATION[Can access be revoked/certified?]
```

## 4. JDBC Target Entity Relationship Diagram

```mermaid
erDiagram
    USERS ||--o{ USER_ROLES : receives
    ROLES ||--o{ USER_ROLES : assigned_as

    USERS {
        integer user_id PK
        string employee_id UK
        string lan_id UK
        string email UK
        string display_name
        string department
        string account_status
        string created_at
        string updated_at
    }

    ROLES {
        integer role_id PK
        string role_code UK
        string role_name
        string role_description
        string risk_level
        string role_status
        string created_at
        string updated_at
    }

    USER_ROLES {
        integer user_role_id PK
        integer user_id FK
        integer role_id FK
        string assignment_status
        string assigned_by
        string assigned_at
        string revoked_by
        string revoked_at
        string assignment_reason
    }
```

## 5. IGA Normalized Relationship Model

```mermaid
erDiagram
    IDENTITY ||--o{ ACCOUNT : owns
    APPLICATION ||--o{ ACCOUNT : contains
    APPLICATION ||--o{ ENTITLEMENT : exposes
    ACCOUNT ||--o{ ASSIGNMENT : has
    ENTITLEMENT ||--o{ ASSIGNMENT : assigned_as
    IDENTITY ||--o{ ACCESS_REQUEST : requests
    ACCESS_REQUEST ||--o{ APPROVAL : requires
    ACCESS_REQUEST ||--o{ PROVISIONING_EVENT : results_in

    IDENTITY {
        string identity_id PK
        string employee_id
        string lan_id
        string email
        string display_name
        string department
        string manager_id
        string status
    }

    APPLICATION {
        string application_id PK
        string application_name
        string integration_pattern
        string risk_level
        string status
    }

    ACCOUNT {
        string account_id PK
        string application_id FK
        string identity_id FK
        string native_account_id
        string account_status
        string correlation_status
    }

    ENTITLEMENT {
        string entitlement_id PK
        string application_id FK
        string native_entitlement_id
        string entitlement_name
        string risk_level
        string status
    }

    ASSIGNMENT {
        string assignment_id PK
        string account_id FK
        string entitlement_id FK
        string assignment_status
        string assigned_at
        string assigned_by
    }

    ACCESS_REQUEST {
        string request_id PK
        string identity_id FK
        string application_id FK
        string entitlement_id FK
        string request_status
        string risk_level
    }

    APPROVAL {
        string approval_id PK
        string request_id FK
        string approver_id
        string decision
        string decided_at
    }

    PROVISIONING_EVENT {
        string event_id PK
        string request_id FK
        string target_application_id
        string action
        string status
        string timestamp
    }
```

## 6. Security Control Plane Flow

```mermaid
flowchart LR
    CALLER[Caller / Service / User]
    MODE{API_SECURITY_MODE}
    DIRECT[Direct Mode<br/>Caller -> Target]
    GATEWAY[api-security-gateway]
    TARGET[Protected API App]
    SIEM[siem-detection-service]

    CALLER --> MODE
    MODE -->|direct| DIRECT --> TARGET
    MODE -->|gateway-monitor| GATEWAY
    MODE -->|gateway-enforce| GATEWAY

    GATEWAY --> CHECKS[Check TLS / Auth / Headers / CORS / Payload / Policy]
    CHECKS --> DECISION{Decision}

    DECISION -->|ALLOW| TARGET
    DECISION -->|ALLOW_WITH_FINDING| TARGET
    DECISION -->|BLOCK| BLOCKED[Request blocked]
    DECISION -->|RATE_LIMIT| LIMITED[Rate limited]
    DECISION -->|REQUIRE_STEP_UP| STEPUP[Step-up / approval required]

    GATEWAY -->|findings / posture score| SIEM
    TARGET -->|audit events| SIEM
```

## 7. Future AI Agent Layer

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
