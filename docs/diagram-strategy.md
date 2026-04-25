# Diagram Strategy

## Purpose

This document defines how diagrams should be organized in Luffy.

The goal is to keep diagrams useful, readable, and easy to find without overloading the main documentation.

## Best-practice rule

Use two levels of diagrams:

```text
Global diagrams   -> show the whole system at a high level
Service diagrams  -> show one app/service in detail
```

## Global diagrams

Global diagrams live here:

```text
docs/diagrams.md
```

They should explain the overall lab:

```text
System context
Service/container architecture
End-to-end identity lifecycle
Access request and provisioning flow
Security control plane overview
Future AI agent layer
```

Global diagrams should not contain every table, field, or app-specific ERD.

## Service-specific diagrams

Service diagrams live inside each service folder:

```text
apps/<service-name>/docs/diagrams.md
```

They should explain the service details:

```text
Service context
HLD
DLD flow
Entity relationship diagram
API/GraphQL/SQL contract flow
Security flow
Audit flow
Optional UI flow
```

Example:

```text
apps/jdbc-target/docs/diagrams.md
```

contains JDBC-specific diagrams for:

```text
users
roles
user_roles
IAM-safe views
future aggregation sequence
correlation logic
risk visibility
optional UI
```

## Why not keep every diagram in the main docs?

Too many diagrams in the main docs causes problems:

```text
Harder to understand the first view
Harder to find service-specific diagrams
Main architecture becomes noisy
App details become mixed with system details
Diagrams become harder to maintain
```

## Recommended structure

```text
docs/
├── diagrams.md                  # global system diagrams only
├── diagram-strategy.md          # this file
└── architecture.md

apps/
├── jdbc-target/
│   └── docs/
│       └── diagrams.md          # JDBC-specific diagrams
├── hrms-service/
│   └── docs/
│       └── diagrams.md          # HRMS-specific diagrams later
├── idp-service/
│   └── docs/
│       └── diagrams.md          # IdP-specific diagrams later
└── iga-service/
    └── docs/
        └── diagrams.md          # IGA-specific diagrams later
```

## Diagram count guideline

### Global docs

Keep around 5 to 7 diagrams.

Recommended global diagrams:

```text
1. System context
2. Service/container architecture
3. Identity lifecycle
4. Access request/provisioning
5. API security and SIEM flow
6. UI/module map
7. Future AI agent layer
```

### Service docs

A service can have more diagrams if needed, but start simple.

Recommended service diagrams:

```text
1. Service overview
2. HLD
3. ERD/data model
4. Main sequence flow
5. Security/audit flow
```

Add more only when they explain something important.

## Diagram naming standard

Use clear names:

```text
System Context Diagram
Container Architecture
Identity Lifecycle Flow
Access Request Sequence
Entity Relationship Diagram
Security Flow
Audit Flow
UI Flow
```

Avoid vague names:

```text
Diagram 1
Architecture Thing
DB Flow
Full All Model
```

## Final decision

```text
Main docs should show the whole system.
Service docs should show service-specific details.
```

For Luffy:

```text
docs/diagrams.md                         -> global overview only
apps/jdbc-target/docs/diagrams.md         -> JDBC-specific diagrams
apps/<future-service>/docs/diagrams.md    -> service-specific diagrams as each service is designed
```
