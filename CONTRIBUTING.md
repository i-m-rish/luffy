# Contributing to Luffy

## Development principles

Before adding code, keep the project aligned with:

```text
secure by design
least privilege
clear documentation
fake data only
no real secrets
human approval for risky actions
responsible AI guardrails
```

## How to work on a service

Each service should have a design package before serious implementation:

```text
apps/<service-name>/docs/objectives.md
apps/<service-name>/docs/hld.md
apps/<service-name>/docs/dld.md
apps/<service-name>/docs/data-model.md
apps/<service-name>/docs/diagrams.md
apps/<service-name>/docs/security-controls.md
apps/<service-name>/docs/audit-events.md
apps/<service-name>/docs/ui-decision.md
```

## Running tests

From the repository root:

```bash
python -m pytest
```

For only the JDBC target:

```bash
python -m pytest apps/jdbc-target/tests
```

## Adding a new service

Before implementation, define:

```text
objective
HLD
DLD
data model
relationship diagram
API/GraphQL/SQL contract
security controls
audit events
UI decision
```

## Pull request checklist

Every PR should include:

```text
What changed
Why it changed
How it was tested
Security impact
Docs updated
```

## Data rules

Do not commit:

```text
real employee data
real customer data
real credentials
real API tokens
real certificates/private keys
production URLs
```

Use fake/sample values only.
