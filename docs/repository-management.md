# Repository Management Standard

## Purpose

This document defines how the Luffy repository should be managed as it grows from a learning lab into a serious cybersecurity IAM project.

It is based on common patterns seen in mature open-source projects and adapted for this repo.

## Current review summary

Luffy already has strong planning artifacts:

```text
README.md
architecture docs
diagram strategy
design documentation standard
secure-by-design and responsible AI guardrails
API/authentication standards
service-level JDBC docs
basic Python runner and tests for jdbc-target
```

The main improvement needed now is repo hygiene:

```text
clear contribution rules
security policy
issue/PR templates
CI test workflow
root-level Python tooling baseline
consistent service package structure
clear roadmap
```

## Best-practice structure

Recommended root structure:

```text
luffy/
├── .github/
│   ├── workflows/
│   │   └── python-tests.yml
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── design_task.md
│   └── pull_request_template.md
├── apps/
├── docs/
├── tests/
├── scripts/
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
├── ROADMAP.md
├── pyproject.toml
└── .gitignore
```

## Documentation rules

### Global docs

Global docs go in:

```text
docs/
```

Use them for:

```text
overall architecture
security baseline
API/auth standards
responsible AI guardrails
diagram strategy
roadmap-level design
```

### Service docs

Service-specific docs go in:

```text
apps/<service-name>/docs/
```

Use them for:

```text
objectives
HLD
DLD
data model
relationship diagrams
API/GraphQL/SQL contracts
security controls
audit events
UI decision
```

## Diagram rules

Global diagrams:

```text
docs/diagrams.md
```

Service-specific diagrams:

```text
apps/<service-name>/docs/diagrams.md
```

Do not put every app ERD in the global diagrams file.

## Issue management

Use issues for all work.

Recommended issue labels:

```text
architecture
documentation
foundation
security
test
ci
service:jdbc-target
service:hrms-service
service:idp-service
service:iga-service
service:api-security-gateway
milestone-1
milestone-2
```

Issue types:

```text
Design task
Implementation task
Test task
Security review
Documentation cleanup
Bug
```

Every issue should answer:

```text
Goal
Scope
Out of scope
Files expected
Security considerations
Done when
```

## Pull request standard

Every PR should include:

```text
What changed
Why it changed
How it was tested
Security impact
Docs updated
Screenshots/diagrams if relevant
```

## Testing standard

All Python-based components should have tests.

Minimum test categories:

```text
unit tests
schema/model tests
security validation tests
contract tests
negative tests for invalid input
```

For `jdbc-target`, tests should verify:

```text
database builds
required tables exist
IAM views exist
seed data loads
risk levels are exposed
orphan-style account exists
```

## CI standard

Add GitHub Actions to run:

```text
python -m pytest
```

Later add:

```text
ruff check
mypy
secret scanning
dependency scanning
markdown linting
```

## Python standard

Use a root `pyproject.toml` for:

```text
pytest configuration
ruff configuration later
Python version target
package/tooling conventions
```

Recommended Python version target:

```text
Python 3.11+
```

## Security management

Add:

```text
SECURITY.md
```

Should state:

```text
No real secrets
No real employee data
Do not report real vulnerabilities from external systems here
This is a learning lab
How to report security issues in the repo
```

## Contribution management

Add:

```text
CONTRIBUTING.md
```

Should explain:

```text
How to run tests
How to structure docs
How to add a new service
How to follow secure-by-design rules
How to write issues and PRs
```

## Roadmap management

Add:

```text
ROADMAP.md
```

Should show:

```text
Milestone 1 - IAM foundation
Milestone 2 - Additional connector patterns
Milestone 3 - API security and detection
Milestone 4 - machine identity and desktop agent
Milestone 5 - AI agents
```

## Service readiness checklist

Before a service moves beyond design:

```text
README exists
objectives.md exists
hld.md exists
dld.md exists
data-model.md exists
diagrams.md exists
security-controls.md exists
audit-events.md exists
ui-decision.md exists
contract doc exists if API/GraphQL/SQL based
basic tests exist if implementation exists
```

## Current priority

Do not add more product ideas right now.

Next priority:

```text
1. Add repo-management files: CONTRIBUTING.md, SECURITY.md, ROADMAP.md, pyproject.toml, .gitignore.
2. Add GitHub Actions for Python tests.
3. Finish and run jdbc-target tests.
4. Then start hrms-service design package.
```

## Final rule

A serious repo is not just code.

For Luffy, every change should maintain:

```text
clear docs
clear scope
clear tests
clear security impact
clear next milestone
```
