# IdP Service Diagrams

This document contains Mermaid diagrams specific to `idp-service`.

## 1. IdP Context Diagram

```mermaid
flowchart LR
    HRMS[hrms-service<br/>worker source]
    IDP[idp-service<br/>digital identity source]
    IGA[iga-service<br/>governance aggregation]
    SIEM[siem-detection-service<br/>auth/admin events later]

    HRMS -->|worker attributes later| IDP
    IDP -->|identities / groups / apps / machine identities| IGA
    IDP -->|auth and admin events later| SIEM
```

## 2. IdP Entity Relationship Diagram

```mermaid
erDiagram
    IDENTITY ||--o{ GROUP_MEMBERSHIP : has
    GROUP ||--o{ GROUP_MEMBERSHIP : contains
    APPLICATION_REGISTRATION ||--o{ APP_ASSIGNMENT : grants_login_to
    GROUP ||--o{ APP_ASSIGNMENT : assigned_to_app
    MACHINE_IDENTITY }o--|| APPLICATION_REGISTRATION : used_by

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

    GROUP {
        string group_id PK
        string group_name UK
        string group_type
        string description
        string risk_level
        string status
    }

    GROUP_MEMBERSHIP {
        string membership_id PK
        string identity_id FK
        string group_id FK
        string membership_status
        string assigned_by
        string assigned_at
    }

    APPLICATION_REGISTRATION {
        string app_registration_id PK
        string app_id UK
        string app_name
        string auth_protocol
        boolean sso_enabled
        string token_audience
        string status
    }

    APP_ASSIGNMENT {
        string app_assignment_id PK
        string app_registration_id FK
        string group_id FK
        string assignment_status
        string assigned_at
    }

    MACHINE_IDENTITY {
        string machine_identity_id PK
        string name
        string type
        string owner
        string used_by_service
        string risk_level
        string status
        string rotation_status
        string last_used_at
    }
```

## 3. IdP to IGA Normalization Flow

```mermaid
flowchart LR
    IDENTITIES[identities.json]
    GROUPS[groups.json]
    MEMBERSHIPS[group-memberships.json]
    APPREG[app-registrations.json]
    APPASN[app-assignments.json]
    NHI[machine-identities.json]

    IGA_IDS[iga-service<br/>identities-normalized.json]
    IGA_APPS[iga-service<br/>application-catalog.json]
    IGA_FUTURE[future IGA access / NHI governance]

    IDENTITIES -->|digital identities| IGA_IDS
    GROUPS -->|group access context later| IGA_FUTURE
    MEMBERSHIPS -->|identity-group relationships later| IGA_FUTURE
    APPREG -->|application registration context| IGA_APPS
    APPASN -->|login assignment context later| IGA_FUTURE
    NHI -->|machine identity governance later| IGA_FUTURE
```

## 4. HRMS to IdP Identity Flow

```mermaid
sequenceDiagram
    participant HRMS as hrms-service
    participant IDP as idp-service
    participant IGA as iga-service

    HRMS->>IDP: Send worker attributes later
    IDP->>IDP: Create or update digital identity
    IDP->>IDP: Assign baseline groups
    IDP->>IGA: Expose identity, group, app registration, and NHI data
```

## 5. App Registration vs IGA Onboarding

```mermaid
flowchart TD
    APP[Application]
    IDPREG[IdP App Registration<br/>SSO / OIDC / SAML / API client]
    IGACAT[IGA Application Catalog<br/>governance / access / certification]

    APP --> IDPREG
    APP --> IGACAT

    IDPREG --> LOGIN[Can user authenticate?]
    IDPREG --> GROUP[Which group grants login?]
    IDPREG --> TOKEN[Which token audience/client?]

    IGACAT --> ACCESS[Should user have access?]
    IGACAT --> APPROVAL[Who approved access?]
    IGACAT --> REVOKE[Can access be revoked/certified?]
```

## 6. Machine Identity Governance Flow

```mermaid
flowchart LR
    NHI[machine identity]
    OWNER[owner / owning team]
    APP[used by service/app]
    RISK[risk level]
    ROTATION[rotation status]
    IGA[iga-service]

    NHI --> OWNER
    NHI --> APP
    NHI --> RISK
    NHI --> ROTATION
    NHI --> IGA

    IGA --> FUTURE_REVIEW[future NHI access review]
    IGA --> FUTURE_ROTATION[future rotation risk finding]
```

## 7. Future GraphQL Query Flow

```mermaid
sequenceDiagram
    participant Client as GraphQL Client
    participant IDP as idp-service GraphQL
    participant Store as IdP Data Store
    participant IGA as iga-service later

    Client->>IDP: Query identity with groups and app assignments
    IDP->>IDP: Authenticate caller later
    IDP->>IDP: Apply object-level authorization later
    IDP->>Store: Fetch identity relationships
    Store-->>IDP: Return identities/groups/apps
    IDP-->>Client: Return authorized fields only
    IGA->>IDP: Aggregate governed IdP data later
```
