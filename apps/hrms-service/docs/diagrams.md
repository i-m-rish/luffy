# HRMS Service Diagrams

This document contains Mermaid diagrams specific to `hrms-service`.

## 1. HRMS Context Diagram

```mermaid
flowchart LR
    HRMS[hrms-service<br/>Worker lifecycle source]
    IDP[idp-service<br/>Digital identity source]
    IGA[iga-service<br/>Governance and correlation]
    SIEM[siem-detection-service<br/>Audit events later]

    HRMS -->|worker attributes later| IDP
    HRMS -->|employment truth / lifecycle events| IGA
    HRMS -->|worker lifecycle audit later| SIEM
```

## 2. HRMS Entity Relationship Diagram

```mermaid
erDiagram
    DEPARTMENT ||--o{ WORKER : contains
    POSITION ||--o{ WORKER : assigned_to
    WORKER ||--o{ LIFECYCLE_EVENT : has
    WORKER ||--o{ WORKER : manages

    WORKER {
        string worker_id PK
        string employee_id UK
        string first_name
        string last_name
        string display_name
        string email UK
        string worker_type
        string employment_status
        string department_id FK
        string position_id FK
        string manager_employee_id
        string location
        string start_date
        string termination_date
        string last_updated_at
    }

    DEPARTMENT {
        string department_id PK
        string department_name
        string department_owner_employee_id
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
        string created_at
    }
```

## 3. HRMS to IGA Normalization Flow

```mermaid
flowchart LR
    WORKERS[workers.json]
    EVENTS[lifecycle-events.json]
    IGA_IDENTITIES[iga-service<br/>identities-normalized.json]
    IGA_GOV[IGA governance context]

    WORKERS -->|employee_id / lan_id / email / status| IGA_IDENTITIES
    EVENTS -->|joiner / mover / leaver trigger| IGA_GOV
    IGA_IDENTITIES --> IGA_GOV
```

## 4. Joiner Flow

```mermaid
sequenceDiagram
    participant HRMS as hrms-service
    participant IDP as idp-service later
    participant IGA as iga-service
    participant SIEM as siem-detection-service later

    HRMS->>HRMS: Create worker record
    HRMS->>HRMS: Create JOINER lifecycle event
    HRMS->>IDP: Send worker attributes later
    IDP->>IDP: Create digital identity later
    HRMS->>IGA: Provide worker context
    IDP->>IGA: Provide digital identity context later
    IGA->>IGA: Normalize identity and evaluate birthright access later
    HRMS->>SIEM: Send worker lifecycle audit event later
```

## 5. Mover Flow

```mermaid
sequenceDiagram
    participant HRMS as hrms-service
    participant IGA as iga-service
    participant SIEM as siem-detection-service later

    HRMS->>HRMS: Update department / position / manager
    HRMS->>HRMS: Create MOVER lifecycle event
    HRMS->>IGA: Provide updated lifecycle context
    IGA->>IGA: Review old access later
    IGA->>IGA: Evaluate new access later
    HRMS->>SIEM: Send mover audit event later
```

## 6. Leaver Flow

```mermaid
sequenceDiagram
    participant HRMS as hrms-service
    participant IDP as idp-service later
    participant IGA as iga-service
    participant SIEM as siem-detection-service later

    HRMS->>HRMS: Set employment_status = TERMINATED
    HRMS->>HRMS: Create LEAVER lifecycle event
    HRMS->>IDP: Send termination status later
    IDP->>IDP: Disable digital identity later
    HRMS->>IGA: Provide leaver status
    IGA->>IGA: Flag active accounts for deprovisioning review later
    HRMS->>SIEM: Send leaver audit event later
```

## 7. Downstream Governance Mapping

```mermaid
flowchart LR
    WORKER[worker attributes]
    EVENT[lifecycle event]
    IDP[idp-service]
    IGA[iga-service]

    WORKER -->|identity attributes| IDP
    WORKER -->|manager / department / employment status| IGA
    EVENT -->|joiner / mover / leaver trigger| IGA

    IGA --> BIRTHRIGHT[birthright access later]
    IGA --> REVIEW[mover access review later]
    IGA --> DEPROV[leaver deprovisioning review later]
```
