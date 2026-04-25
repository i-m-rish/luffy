# JDBC Target Diagrams

This document contains Mermaid diagrams specific to `jdbc-target`.

`jdbc-target` simulates a database-backed security asset operations application that exposes IAM-safe views for SailPoint/IGA-style JDBC aggregation.

## 1. JDBC Target Context Diagram

```mermaid
flowchart LR
    IGA[iga-service<br/>Future IGA Aggregation]
    JDBC[jdbc-target<br/>Security Asset Operations DB]
    SIEM[siem-detection-service<br/>Future Findings / Alerts]

    JDBC -->|IAM-safe views| IGA
    IGA -->|aggregation findings later| SIEM

    subgraph JDBC_DB[jdbc-target database]
        USERS[users table]
        ROLES[roles table]
        USER_ROLES[user_roles table]
        VIEWS[IAM-safe views]
    end

    USERS --> VIEWS
    ROLES --> VIEWS
    USER_ROLES --> VIEWS
```

## 2. JDBC Target HLD Diagram

```mermaid
flowchart TD
    RAW[Raw application tables]
    USERS[users]
    ROLES[roles]
    USERROLES[user_roles]

    VIEW1[vw_iam_accounts]
    VIEW2[vw_iam_entitlements]
    VIEW3[vw_iam_account_entitlements]

    IGA[iga-service<br/>Future JDBC aggregation]

    RAW --> USERS
    RAW --> ROLES
    RAW --> USERROLES

    USERS --> VIEW1
    ROLES --> VIEW2
    USERS --> VIEW3
    ROLES --> VIEW3
    USERROLES --> VIEW3

    VIEW1 --> IGA
    VIEW2 --> IGA
    VIEW3 --> IGA
```

## 3. JDBC Target Entity Relationship Diagram

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

## 4. IAM View Mapping Diagram

```mermaid
flowchart LR
    USERS[users] --> ACCOUNTS[vw_iam_accounts]
    ROLES[roles] --> ENTS[vw_iam_entitlements]
    USERS --> ASSIGNMENTS[vw_iam_account_entitlements]
    ROLES --> ASSIGNMENTS
    USERROLES[user_roles] --> ASSIGNMENTS

    ACCOUNTS --> IGA_ACCOUNT[IGA Account]
    ENTS --> IGA_ENT[IGA Entitlement]
    ASSIGNMENTS --> IGA_ASSIGN[IGA Assignment]
```

## 5. Future JDBC Aggregation Sequence

```mermaid
sequenceDiagram
    participant IGA as iga-service
    participant DB as jdbc-target database
    participant ACC as vw_iam_accounts
    participant ENT as vw_iam_entitlements
    participant ASN as vw_iam_account_entitlements

    IGA->>DB: Open read-only JDBC connection later
    IGA->>ACC: Read accounts
    ACC-->>IGA: Return account rows
    IGA->>ENT: Read entitlements
    ENT-->>IGA: Return entitlement rows
    IGA->>ASN: Read account-entitlement assignments
    ASN-->>IGA: Return assignment rows
    IGA->>IGA: Normalize into Account, Entitlement, Assignment
    IGA->>IGA: Correlate accounts using employee_id, lan_id, email
```

## 6. Correlation Logic Diagram

```mermaid
flowchart TD
    ACCOUNT[JDBC account row]
    EMP{employee_id match?}
    LAN{lan_id match?}
    EMAIL{email match?}
    MATCHED[Correlation status: HIGH / MATCHED]
    MEDIUM[Correlation status: MEDIUM]
    LOW[Correlation status: LOW]
    ORPHAN[Correlation status: UNMATCHED / ORPHAN]

    ACCOUNT --> EMP
    EMP -->|yes| MATCHED
    EMP -->|no| LAN
    LAN -->|yes| MEDIUM
    LAN -->|no| EMAIL
    EMAIL -->|yes| LOW
    EMAIL -->|no| ORPHAN
```

## 7. Risk Visibility Diagram

```mermaid
flowchart LR
    ROLE[roles.risk_level]
    VIEW[vw_iam_entitlements.risk_level]
    ASSIGN[vw_iam_account_entitlements.risk_level]
    IGA[iga-service entitlement catalog]
    REVIEW[Access review / certification]

    ROLE --> VIEW
    ROLE --> ASSIGN
    VIEW --> IGA
    ASSIGN --> IGA
    IGA --> REVIEW
```

## 8. Optional Future UI Diagram

```mermaid
flowchart TD
    UI[jdbc-target optional view-only UI]
    USERS[Users screen]
    ROLES[Roles screen]
    ASSIGNMENTS[User-role assignments screen]
    IAMVIEWS[IAM views preview screen]

    UI --> USERS
    UI --> ROLES
    UI --> ASSIGNMENTS
    UI --> IAMVIEWS

    USERS -. read-only .-> DB[(jdbc-target DB)]
    ROLES -. read-only .-> DB
    ASSIGNMENTS -. read-only .-> DB
    IAMVIEWS -. read-only .-> DB
```
