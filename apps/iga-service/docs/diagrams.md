# IGA Service Diagrams

This document contains Mermaid diagrams specific to `iga-service`.

## 1. IGA Context Diagram

```mermaid
flowchart LR
    HRMS[hrms-service<br/>worker lifecycle]
    IDP[idp-service<br/>digital identities / groups / app registrations]
    JDBC[jdbc-target<br/>accounts / entitlements / assignments]
    IGA[iga-service<br/>governance model]
    SIEM[siem-detection-service<br/>audit/finding events later]

    HRMS --> IGA
    IDP --> IGA
    JDBC --> IGA
    IGA --> SIEM
```

## 2. IGA Normalized Entity Relationship Diagram

```mermaid
erDiagram
    APPLICATION ||--o{ ACCOUNT : contains
    APPLICATION ||--o{ ENTITLEMENT : exposes
    IDENTITY ||--o{ ACCOUNT : owns
    ACCOUNT ||--o{ ASSIGNMENT : has
    ENTITLEMENT ||--o{ ASSIGNMENT : assigned_as
    ACCOUNT ||--|| CORRELATION_RESULT : evaluated_by
    IDENTITY ||--o{ CORRELATION_RESULT : matched_to

    APPLICATION {
        string application_id PK
        string application_name
        string application_type
        string integration_pattern
        string risk_level
        string status
        string owner
    }

    IDENTITY {
        string identity_id PK
        string employee_id
        string lan_id
        string email
        string display_name
        string identity_type
        string identity_status
        string source_system
    }

    ACCOUNT {
        string account_id PK
        string application_id FK
        string native_account_id
        string employee_id
        string lan_id
        string email
        string account_status
        string correlation_status
    }

    ENTITLEMENT {
        string entitlement_id PK
        string application_id FK
        string native_entitlement_id
        string entitlement_name
        string entitlement_description
        string risk_level
        string status
    }

    ASSIGNMENT {
        string assignment_id PK
        string account_id FK
        string entitlement_id FK
        string assignment_status
        string assigned_by
        string assigned_at
    }

    CORRELATION_RESULT {
        string correlation_id PK
        string account_id FK
        string identity_id FK
        string result
        string match_attribute
        string confidence
        string reason
    }
```

## 3. Aggregation and Correlation Flow

```mermaid
sequenceDiagram
    participant HRMS as hrms-service
    participant IDP as idp-service
    participant JDBC as jdbc-target
    participant IGA as iga-service

    HRMS->>IGA: Provide worker/identity context
    IDP->>IGA: Provide digital identities and groups
    JDBC->>IGA: Provide accounts, entitlements, assignments
    IGA->>IGA: Normalize identities
    IGA->>IGA: Normalize accounts and entitlements
    IGA->>IGA: Correlate account using employee_id, lan_id, email
    IGA->>IGA: Mark matched, partial, or orphan accounts
```

## 4. Correlation Decision Logic

```mermaid
flowchart TD
    ACCOUNT[Account record]
    EMP{employee_id matches identity?}
    LAN{lan_id matches identity?}
    EMAIL{email matches identity?}
    MATCHED[Result: MATCHED<br/>Confidence: HIGH]
    PARTIAL_LAN[Result: PARTIAL<br/>Confidence: MEDIUM]
    PARTIAL_EMAIL[Result: PARTIAL<br/>Confidence: LOW]
    ORPHAN[Result: ORPHAN<br/>Confidence: NONE]

    ACCOUNT --> EMP
    EMP -->|yes| MATCHED
    EMP -->|no| LAN
    LAN -->|yes| PARTIAL_LAN
    LAN -->|no| EMAIL
    EMAIL -->|yes| PARTIAL_EMAIL
    EMAIL -->|no| ORPHAN
```

## 5. Governance Relationship View

```mermaid
flowchart LR
    IDENTITY[Identity]
    ACCOUNT[Application Account]
    ASSIGNMENT[Assignment]
    ENTITLEMENT[Entitlement]
    APP[Application]
    RISK[Risk Level]

    IDENTITY --> ACCOUNT
    ACCOUNT --> ASSIGNMENT
    ASSIGNMENT --> ENTITLEMENT
    ENTITLEMENT --> APP
    ENTITLEMENT --> RISK
```

## 6. Future IGA UI Flow

```mermaid
flowchart TD
    UI[IGA Governance UI]
    CATALOG[Application Catalog]
    IDENTITIES[Identities]
    ACCOUNTS[Accounts]
    ACCESS[Access / Assignments]
    CORR[Correlation Results]
    REVIEW[Access Review / Certification later]
    REQUEST[Access Request later]

    UI --> CATALOG
    UI --> IDENTITIES
    UI --> ACCOUNTS
    UI --> ACCESS
    UI --> CORR
    UI --> REVIEW
    UI --> REQUEST
```
