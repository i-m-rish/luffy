# UI Strategy

## Principle

Not every service needs a full UI.

Luffy should be built API/data-first, then UI should be added only where human interaction is genuinely useful.

## UI priority by service

| Service | UI decision | Priority | Reason |
|---|---|---|---|
| `iga-service` | Full UI | First | Main governance portal for applications, identities, accounts, entitlements, requests, approvals, provisioning events, certifications, and reports |
| `idp-service` | Minimal admin UI | Later | Useful for identities, groups, app registrations, machine identities, OAuth clients, and token/login simulation |
| `hrms-service` | Minimal admin UI | Later | Useful for workers, departments, positions, and joiner/mover/leaver lifecycle events |
| `pam-target` | Focused UI | Later | Useful for safes, privileged accounts, checkout requests, approvals, sessions, and audit events |
| `api-security-gateway` | Dashboard UI | Later | Useful for API posture score, findings, allowlists, blocklists, monitor mode, and enforce mode |
| `siem-detection-service` | Dashboard UI | Later | Useful for events, detections, alerts, investigations, and alert closure |
| `desktop-agent-app` | Desktop/client UI | Later | It is itself a desktop/client app for device posture, heartbeat, local events, and machine identity |
| `webservices-target` | Optional small UI | Low | API-first target app; small admin UI can be added later if useful |
| `scim-target` | Optional small UI | Low | SCIM-first SaaS target; admin UI can be added later for users, groups, and tenant settings |
| `jdbc-target` | Optional view-only UI | Lowest | Database-first target; optional UI can show users, roles, user-role assignments, and IAM views |

## First UI to build

Build the first real UI for:

```text
iga-service
```

Reason:

```text
IGA is where humans request access, approve access, review access, and understand governance risk.
```

## First IGA UI screens

```text
Applications
Identities
Accounts
Entitlements
Correlation results
Access requests
Approvals
Provisioning events
Certification / access review report
```

## Recommended final UI model

Instead of building many separate polished frontends, create one unified console later:

```text
luffy-console
```

Suggested modules:

```text
HRMS
IdP
IGA
Target Apps
PAM
API Security
SIEM
Machine Identity
Reports
Agents
```

## Build order for UI

```text
1. No UI during first data-model work
2. IGA UI after basic aggregation/correlation works
3. PAM, API security, and SIEM dashboards after their services exist
4. HRMS and IdP admin screens as minimal support screens
5. Unified luffy-console later
```

## Avoid

Do not build separate polished UIs for every service at the start.

Avoid:

```text
Premature frontend work
Duplicate admin screens
UI before data model
UI before security model
UI before audit model
```

## Final decision

```text
All services get APIs/data models.
Only selected services get UI.
iga-service gets the first real UI.
luffy-console becomes the long-term unified interface.
```
