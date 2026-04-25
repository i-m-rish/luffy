# Luffy Mermaid Diagrams

This document contains the main Mermaid diagrams for the Luffy cybersecurity IAM lab.

## Diagram index

```text
1. System context diagram
2. Container/service architecture
3. Identity lifecycle sequence
4. Access request and provisioning sequence
5. App registration model
6. IGA normalized ERD
7. JDBC target ERD
8. HRMS worker lifecycle model
9. IdP identity and app registration model
10. PAM target model
11. API security gateway flow
12. SIEM detection flow
13. Machine identity model
14. UI/module map
15. Future AI agent layer
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

    LUFFY -->|governs| TARGETS[Target Apps<br/>JDBC / REST / SCIM / PAM]
    LUFFY -->|monitors| SECURITY[API Security + SIEM]
    LUFFY -->|uses lifecycle data| HRMS[HRMS Source]
    LUFFY -->|uses digital identity| IDP[IdP Source]
```

---

## 2. Container / Service Architecture

```mermaid
flowchart LR
    HRMS[hrms-service<br/>REST + DB later<br/>Worker lifecycle]
    IDP[idp-service<br/>GraphQL + REST login<br/>Identities / Groups / Apps]
    IGA[iga-service<br/>GraphQL<br/>Governance / Correlation]

    JDBC[jdbc-target<br/>SQL / JDBC<br/>Security Asset Ops]
    WS[webservices-target<br/>REST + Cloud DB later<br/>Risk Portal]
    SCIM[scim-target<br/>SaaS + SCIM 2.0<br/>Endpoint Security]
    PAM[pam-target<br/>REST/PAM APIs<br/>Safes / Checkout / Sessions]

    APIGW[api-security-gateway<br/>Posture / Monitor / Enforce]
    SIEM[siem-detection-service<br/>Events / Alerts / Detections]
    DESKTOP[desktop-agent-app<br/>Device Posture / Heartbeat]

    HRMS -->|worker lifecycle| IDP
    IDP -->|identities, groups, app registrations| IGA

    IGA -->|JDBC aggregation| JDBC
    IGA -->|REST aggregation/provisioning| WS
    IGA -->|SCIM provisioning| SCIM
    IGA -->|PAM governance| PAM

    DESKTOP -->|device heartbeat later| SCIM
    DESKTOP -->|machine identity evidence later| IGA

    APIGW -. posture scan .-> IDP
    APIGW -. posture scan .-> IGA
    APIGW -. posture scan .-> WS
    APIGW -. posture scan .-> SCIM
    APIGW -. posture scan .-> PAM

    IDP -->|auth/security events| SIEM
    IGA -->|governance audit events| SIEM
    JDBC -->|aggregation findings later| SIEM
    WS -->|API events| SIEM
    SCIM -->|SCIM provisioning events| SIEM
    PAM -->|privileged access audit| SIEM
    APIGW -->|findings / posture score| SIEM
```

---

## 3. Identity Lifecycle Sequence

```mermaid
sequenceDiagram
    participant HRMS as hrms-service
    participant IDP as idp-service
    participant IGA as iga-service
    participant JDBC as jdbc-target
    participant SIEM as siem-detection-service

    HRMS->>HRMS: Create JOINER / MOVER / LEAVER event
    HRMS->>IDP: Sync worker attributes
    IDP->>IDP: Create or update digital identity
    IDP->>IGA: Provide identity aggregation data
    JDBC->>IGA: Provide account and entitlement data via IAM views
    IGA->>IGA: Correlate account to identity
    IGA->>IGA: Detect matched, unmatched, or orphan accounts
    IGA->>SIEM: Send lifecycle and correlation audit event
```

---

## 4. Access Request and Provisioning Sequence

```mermaid
sequenceDiagram
    participant User as Requester
    participant IGA as iga-service
    participant Manager as Manager/App Owner
    participant Gateway as api-security-gateway
    participant SCIM as scim-target
    participant PAM as pam-target
    participant SIEM as siem-detection-service

    User->>IGA: Request access
    IGA->>IGA: Validate identity, app, entitlement, risk
    IGA->>Manager: Route approval
    Manager->>IGA: Approve / reject

    alt Approved SCIM access
        IGA->>Gateway: Send provisioning action for inspection
        Gateway->>Gateway: Check auth, risk, allowlist, payload
        Gateway->>SCIM: Forward allowed SCIM group assignment
        SCIM->>SIEM: Send provisioning event
    end

    alt Approved PAM access
        IGA->>Gateway: Send PAM safe membership action
        Gateway->>Gateway: Require step-up if critical
        Gateway->>PAM: Forward allowed safe membership change
        PAM->>SIEM: Send privileged access event
    end

    IGA->>SIEM: Send access request audit event
```

---

## 5. App Registration Model

```mermaid
flowchart TD
    APP[Application]

    IDPREG[IdP App Registration<br/>Authentication / SSO / Tokens]
    IGAREG[IGA Application Catalog<br/>Governance / Aggregation / Provisioning]

    APP --> IDPREG
    APP --> IGAREG

    IDPREG --> AUTH[Can the user authenticate?]
    IDPREG --> TOKEN[Which token/client/group allows login?]
    IDPREG --> SSO[What SSO protocol is used?]

    IGAREG --> ACCESS[Should the user have access?]
    IGAREG --> ENT[What entitlements exist?]
    IGAREG --> APPROVAL[Who approved access?]
    IGAREG --> CERT[Can access be certified?]
    IGAREG --> REVOKE[Can access be revoked?]
```

---

## 6. IGA Normalized ERD

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
    IDENTITY ||--o{ CERTIFICATION_ITEM : reviewed_in

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

    CERTIFICATION_ITEM {
        string certification_item_id PK
        string identity_id FK
        string assignment_id FK
        string reviewer_id
        string decision
        string review_status
    }
```

---

## 7. JDBC Target ERD

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

---

## 8. HRMS Worker Lifecycle Model

```mermaid
erDiagram
    WORKER ||--o{ LIFECYCLE_EVENT : has
    DEPARTMENT ||--o{ WORKER : contains
    POSITION ||--o{ WORKER : assigned_to
    WORKER ||--o{ WORKER : manages

    WORKER {
        string worker_id PK
        string employee_id UK
        string first_name
        string last_name
        string email
        string worker_type
        string employment_status
        string manager_employee_id
        string department_id FK
        string position_id FK
    }

    DEPARTMENT {
        string department_id PK
        string department_name
        string cost_center
        string status
    }

    POSITION {
        string position_id PK
        string job_title
        string job_family
        string risk_category
        string status
    }

    LIFECYCLE_EVENT {
        string event_id PK
        string employee_id FK
        string event_type
        string effective_date
        string old_value
        string new_value
        string status
    }
```

---

## 9. IdP Identity and App Registration Model

```mermaid
erDiagram
    IDENTITY ||--o{ GROUP_MEMBERSHIP : has
    GROUP ||--o{ GROUP_MEMBERSHIP : contains
    APPLICATION_REGISTRATION ||--o{ APP_ASSIGNMENT : grants_login_to
    GROUP ||--o{ APP_ASSIGNMENT : assigned_to_app
    MACHINE_IDENTITY ||--o{ APPLICATION_REGISTRATION : used_by

    IDENTITY {
        string identity_id PK
        string employee_id
        string lan_id
        string email
        string display_name
        string status
    }

    GROUP {
        string group_id PK
        string group_name
        string group_type
        string status
    }

    GROUP_MEMBERSHIP {
        string membership_id PK
        string identity_id FK
        string group_id FK
        string status
    }

    APPLICATION_REGISTRATION {
        string app_registration_id PK
        string app_id
        string app_name
        string auth_protocol
        string sso_enabled
        string status
    }

    APP_ASSIGNMENT {
        string app_assignment_id PK
        string app_registration_id FK
        string group_id FK
        string assignment_status
    }

    MACHINE_IDENTITY {
        string machine_identity_id PK
        string name
        string type
        string owner
        string rotation_status
        string risk_level
    }
```

---

## 10. PAM Target Model

```mermaid
erDiagram
    SAFE ||--o{ PRIVILEGED_ACCOUNT : contains
    SAFE ||--o{ SAFE_MEMBERSHIP : grants
    PRIVILEGED_ACCOUNT ||--o{ CHECKOUT_REQUEST : requested_for
    CHECKOUT_REQUEST ||--o{ PRIVILEGED_SESSION : starts
    PRIVILEGED_SESSION ||--o{ PAM_AUDIT_EVENT : produces

    SAFE {
        string safe_id PK
        string safe_name
        string owner
        string risk_level
        string status
    }

    PRIVILEGED_ACCOUNT {
        string privileged_account_id PK
        string safe_id FK
        string account_name
        string platform_type
        string target_system
        string risk_level
        string status
    }

    SAFE_MEMBERSHIP {
        string membership_id PK
        string safe_id FK
        string identity_id
        string permission
        string status
    }

    CHECKOUT_REQUEST {
        string checkout_request_id PK
        string privileged_account_id FK
        string identity_id
        string approval_status
        string valid_from
        string valid_until
    }

    PRIVILEGED_SESSION {
        string session_id PK
        string checkout_request_id FK
        string started_at
        string ended_at
        string session_status
        string audit_status
    }

    PAM_AUDIT_EVENT {
        string event_id PK
        string session_id FK
        string event_type
        string actor
        string timestamp
    }
```

---

## 11. API Security Gateway Flow

```mermaid
flowchart LR
    CALLER[Caller / Service / User]
    MODE{API_SECURITY_MODE}
    DIRECT[Direct Mode<br/>Caller -> Target]
    GATEWAY[api-security-gateway]
    CHECKS[Posture + Runtime Checks<br/>TLS / Auth / Headers / CORS / Payload / Policy]
    DECISION{Decision}
    TARGET[Protected API App]
    SIEM[siem-detection-service]

    CALLER --> MODE
    MODE -->|direct| DIRECT --> TARGET
    MODE -->|gateway-monitor| GATEWAY
    MODE -->|gateway-enforce| GATEWAY

    GATEWAY --> CHECKS --> DECISION

    DECISION -->|ALLOW| TARGET
    DECISION -->|ALLOW_WITH_FINDING| TARGET
    DECISION -->|BLOCK| BLOCKED[Request blocked]
    DECISION -->|RATE_LIMIT| LIMITED[Rate limited]
    DECISION -->|REQUIRE_STEP_UP| STEPUP[Step-up / approval required]

    GATEWAY -->|findings / posture score| SIEM
    TARGET -->|audit events| SIEM
```

---

## 12. SIEM Detection Flow

```mermaid
flowchart TD
    EVENTS[Events and Findings]
    NORMALIZE[Normalize event schema]
    RULES[Run detection rules]
    ALERTS[Create alerts]
    INVESTIGATE[Investigation queue]
    CLOSE[Close / document outcome]

    IDP[idp-service] --> EVENTS
    IGA[iga-service] --> EVENTS
    PAM[pam-target] --> EVENTS
    APIGW[api-security-gateway] --> EVENTS
    SCIM[scim-target] --> EVENTS
    WS[webservices-target] --> EVENTS

    EVENTS --> NORMALIZE --> RULES --> ALERTS --> INVESTIGATE --> CLOSE

    RULES --> DET1[DET-001 Failed login spike]
    RULES --> DET2[DET-002 High-risk access without approval]
    RULES --> DET3[DET-003 PAM checkout outside window]
    RULES --> DET4[DET-004 Orphan account active]
    RULES --> DET5[DET-005 Weak API posture]
```

---

## 13. Machine Identity Model

```mermaid
erDiagram
    MACHINE_IDENTITY ||--o{ SECRET : owns
    MACHINE_IDENTITY ||--o{ CERTIFICATE : owns
    MACHINE_IDENTITY ||--o{ TOKEN : uses
    MACHINE_IDENTITY }o--|| OWNER : owned_by
    MACHINE_IDENTITY }o--|| APPLICATION : used_by

    MACHINE_IDENTITY {
        string machine_identity_id PK
        string name
        string type
        string used_by_service
        string risk_level
        string status
        string last_used_at
    }

    SECRET {
        string secret_id PK
        string machine_identity_id FK
        string secret_type
        string rotation_due_at
        string rotation_status
    }

    CERTIFICATE {
        string certificate_id PK
        string machine_identity_id FK
        string common_name
        string expiry_date
        string certificate_status
    }

    TOKEN {
        string token_id PK
        string machine_identity_id FK
        string token_type
        string issued_at
        string expires_at
    }

    OWNER {
        string owner_id PK
        string owner_name
        string owner_type
    }

    APPLICATION {
        string application_id PK
        string application_name
        string integration_pattern
    }
```

---

## 14. UI / Module Map

```mermaid
flowchart TD
    CONSOLE[luffy-console<br/>future unified UI]

    IGA_UI[IGA Module<br/>requests / approvals / certifications]
    IDP_UI[IdP Module<br/>identities / groups / app registrations]
    HRMS_UI[HRMS Module<br/>workers / lifecycle events]
    PAM_UI[PAM Module<br/>safes / checkout / sessions]
    API_UI[API Security Module<br/>posture / findings / policies]
    SIEM_UI[SIEM Module<br/>events / alerts / investigations]
    NHI_UI[Machine Identity Module<br/>secrets / certs / tokens]
    AGENT_UI[Agents Module<br/>recommendations / evidence]

    CONSOLE --> IGA_UI
    CONSOLE --> IDP_UI
    CONSOLE --> HRMS_UI
    CONSOLE --> PAM_UI
    CONSOLE --> API_UI
    CONSOLE --> SIEM_UI
    CONSOLE --> NHI_UI
    CONSOLE --> AGENT_UI
```

---

## 15. Future AI Agent Layer

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
