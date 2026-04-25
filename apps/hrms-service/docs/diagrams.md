# HRMS Service Diagrams

This document contains Mermaid diagrams specific to `hrms-service`.

## 1. HRMS Context Diagram

```mermaid
flowchart LR
    HRMS[hrms-service<br/>Worker lifecycle source]
    IDP[idp-service<br/>Digital identity later]
    IGA[iga-service<br/>Lifecycle governance later]
    SIEM[siem-detection-service<br/>Audit events later]

    HRMS -->|worker attributes| IDP
    HRMS -->|joiner/mover/leaver events| IGA
    HRMS -->|audit events later| SIEM
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

## 3. Joiner Flow

```mermaid
sequenceDiagram
    participant HRMS as hrms-service
    participant IDP as idp-service later
    participant IGA as iga-service later
    participant SIEM as siem-detection-service later

    HRMS->>HRMS: Create worker record
    HRMS->>HRMS: Create JOINER lifecycle event
    HRMS->>IDP: Send worker attributes later
    IDP->>IDP: Create digital identity later
    IDP->>IGA: Identity aggregation later
    IGA->>IGA: Evaluate birthright access later
    HRMS->>SIEM: Send worker lifecycle audit event later
```

## 4. Mover Flow

```mermaid
sequenceDiagram
    participant HRMS as hrms-service
    participant IGA as iga-service later
    participant SIEM as siem-detection-service later

    HRMS->>HRMS: Update department / position / manager
    HRMS->>HRMS: Create MOVER lifecycle event
    HRMS->>IGA: Send lifecycle event later
    IGA->>IGA: Review old access later
    IGA->>IGA: Evaluate new access later
    HRMS->>SIEM: Send mover audit event later
```

## 5. Leaver Flow

```mermaid
sequenceDiagram
    participant HRMS as hrms-service
    participant IDP as idp-service later
    participant IGA as iga-service later
    participant SIEM as siem-detection-service later

    HRMS->>HRMS: Set employment_status = TERMINATED
    HRMS->>HRMS: Create LEAVER lifecycle event
    HRMS->>IDP: Send termination status later
    IDP->>IDP: Disable digital identity later
    HRMS->>IGA: Send leaver event later
    IGA->>IGA: Trigger deprovisioning later
    HRMS->>SIEM: Send leaver audit event later
```

## 6. Downstream Governance Mapping

```mermaid
flowchart LR
    WORKER[worker attributes]
    EVENT[lifecycle event]
    IDP[idp-service]
    IGA[iga-service]

    WORKER -->|identity attributes| IDP
    WORKER -->|manager/department context| IGA
    EVENT -->|joiner/mover/leaver trigger| IGA

    IGA --> BIRTHRIGHT[birthright access]
    IGA --> REVIEW[mover access review]
    IGA --> DEPROV[leaver deprovisioning]
```
