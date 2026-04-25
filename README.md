# Luffy

Luffy is a cybersecurity IAM learning lab for building smaller, runnable versions of real identity, governance, application onboarding, privileged access, and detection patterns.

The current focus is an applied IAM flow:

```text
HRMS lifecycle data
→ IdP authentication and role claims
→ IGA/SailPoint-style governance visibility
→ target applications with realistic connector patterns
```

## Current runnable apps

| App | Acts like | Port | Current status | Purpose |
|---|---|---:|---|---|
| `idp-service` | Entra ID / Okta-style IdP | 8002 | Runnable | OIDC-like login, auth code flow, user claims, groups, app registrations, OAuth clients |
| `iga-service` | SailPoint-style IGA | 8001 | Runnable | Identity warehouse, sources, accounts, entitlements, correlation, access reviews, policy violations, RBAC |
| `zsp-jit-app` | Enterprise SaaS target app | 8003 | Runnable | OIDC login through IdP, JIT user provisioning, zero standing privilege, temporary elevation, audit events |
| `hrms-service` | HRMS source | data/tests | Foundation | Joiner, mover, leaver, department, position and lifecycle sample data |
| `jdbc-target` | JDBC/SQL legacy app | data/tests | Foundation | SQL users, roles, mappings, and IAM aggregation views |

## Planned apps

| Planned app | Pattern | Purpose |
|---|---|---|
| `scim-target` | SCIM 2.0 | SaaS provisioning pattern with `/Users` and `/Groups` |
| `webservices-target` | REST | Web services connector pattern |
| `pam-target` | PAM API | Safes, privileged accounts, checkout, sessions, audit |
| `api-security-gateway` | REST | API posture checks, monitor/enforce, findings |
| `siem-detection-service` | Event API | Events, alerts, investigations, detections |
| `desktop-agent-app` | Desktop/client app | Endpoint posture, heartbeat, machine identity |

## Local run

### macOS

```bash
chmod +x scripts/run-local-mac.sh
./scripts/run-local-mac.sh
```

### Linux / Git Bash

```bash
chmod +x scripts/run-local.sh
./scripts/run-local.sh
```

### Windows PowerShell

```powershell
.\scripts\run-local.ps1
```

The local runners start:

```text
IGA UI:       http://127.0.0.1:8001/ui
IGA API docs: http://127.0.0.1:8001/docs
IdP UI:       http://127.0.0.1:8002/ui
IdP API docs: http://127.0.0.1:8002/docs
ZSP App UI:   http://127.0.0.1:8003
ZSP API docs: http://127.0.0.1:8003/docs
```

## Demo login users

The IdP authenticates users and returns role claims to IGA and ZSP.

| Username | Password | IdP role claim | IGA behavior | ZSP app role |
|---|---|---|---|---|
| `admin` | `admin123` | `IGA_ADMIN` | Full governance access | `ZSP_ADMIN` |
| `reviewer` | `reviewer123` | `ACCESS_REVIEWER` | Review/risk access | `ZSP_APPROVER` |
| `owner` | `owner123` | `APP_OWNER` | App/account/entitlement visibility | `ZSP_OPERATOR` |
| `reader` | `reader123` | `READ_ONLY` | Limited read access | `ZSP_VIEWER` |

## Implemented auth flow

```text
Browser
→ IGA or ZSP /login
→ IdP /oauth/authorize
→ user signs in
→ IdP returns authorization code
→ relying app exchanges code at /oauth/token
→ relying app creates local session from IdP claims
→ relying app enforces RBAC
```

This is a local OAuth/OIDC-like learning flow. It is intentionally not production authentication.

## IGA governance model

IGA now governs:

```text
Identities
Sources
Accounts
Entitlements
Assignments
Correlation results
Orphan accounts
High-risk access
Access review placeholders
Policy violation placeholders
```

IGA includes ZSP as a governed source so the lab demonstrates:

```text
IdP authenticates user
ZSP provisions app-local user JIT
IGA sees ZSP accounts, entitlements, assignments, and temporary high-risk access
```

## Security and responsible AI baseline

Every service should follow these project guardrails:

```text
Secure by default
Least privilege everywhere
No real secrets in code
No real personal data
Audit important actions
Human approval for high-risk actions
Agents recommend first; they do not silently provision or revoke
NIST/OWASP-aligned API and authentication standards
```

See:

- [Secure by Design and Responsible AI Guardrails](docs/secure-by-design-and-responsible-ai.md)
- [API and Authentication Standards](docs/api-authentication-standards.md)

## Integration pattern principle

Use the right integration pattern for each service:

```text
IdP / IGA concepts      → highly connected IAM graph concepts
JDBC target             → SQL/JDBC
ZSP SaaS app            → OIDC + JIT + app-local RBAC
SCIM target later       → SCIM 2.0
REST targets later      → REST/Web Services APIs
PAM target later        → PAM-style REST APIs and audit
Agents later            → after clean data and APIs exist
```

## Test command

```bash
python -m pytest apps/jdbc-target/tests -q
python -m pytest apps/hrms-service/tests -q
python -m pytest apps/idp-service/tests -q
python -m pytest apps/iga-service/tests -q
python -m pytest apps/zsp-jit-app/tests -q
```

## Current build direction

Next recommended build order:

```text
1. Stabilize docs/runners/tests for current apps
2. Refactor ZSP app into the same layered style as IGA
3. Build SCIM target
4. Add provisioning/request workflow simulation between IGA and target apps
5. Add PAM and API security patterns
6. Add AI agents only after the data and APIs are reliable
```

## Documentation

- [Architecture](docs/architecture.md)
- [Mermaid Diagrams](docs/diagrams.md)
- [Naming Standards](docs/naming-standards.md)
- [Secure by Design and Responsible AI Guardrails](docs/secure-by-design-and-responsible-ai.md)
- [API and Authentication Standards](docs/api-authentication-standards.md)
- [App Registration Model](docs/app-registration-model.md)
- [HRMS Service](docs/hrms-service.md)
- [PAM Target](docs/pam-target.md)
- [Security Control Plane](docs/security-control-plane.md)
- [Learning Strategy](docs/learning-strategy.md)
