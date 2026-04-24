# Secure by Design and Responsible AI Guardrails

## Purpose

This document defines the baseline security, privacy, responsible AI, and safe-by-design rules for Luffy before implementation starts.

Luffy is a cybersecurity IAM learning lab. Even though it is a lab, it should be designed as if it could later become a serious internal platform.

## Core principles

```text
Secure by default
Least privilege everywhere
No real secrets in code
No real personal data
Audit all important actions
Explain before automating
Human approval for risky actions
Agents recommend first, execute later only with controls
```

## Secure by design checklist

### 1. Least privilege

Every service should only have the minimum access it needs.

Examples:

```text
iga-service can read HRMS data but should not directly modify HRMS workers.
iga-service can provision to target apps only through defined connector APIs.
jdbc-target should expose IAM-safe views, not raw transactional tables.
api-security-gateway should inspect traffic but not silently change business data.
```

### 2. Separation of duties

Separate duties across request, approval, provisioning, and review.

Rules:

```text
Requester should not approve their own access.
High-risk access requires additional approval.
PAM emergency access requires follow-up review.
Admin access should be separately reviewed.
```

### 3. Defense in depth

Do not rely on only one layer.

Use:

```text
IdP authentication
IGA approval
Target app authorization
API security gateway inspection
SIEM detection
Audit logs
Certification review
```

### 4. Secure defaults

Default behavior should be safe.

Examples:

```text
New APIs require authentication by default.
Dangerous debug endpoints are disabled by default.
Gateway starts in monitor mode, not silent bypass.
Agents are read-only by default.
PAM critical actions require approval.
```

### 5. No secrets in code

Never commit real secrets.

Do not store:

```text
Passwords
API tokens
OAuth client secrets
Private keys
Real certificates
Real employee data
Real production URLs
```

Use placeholders:

```text
EXAMPLE_SECRET_DO_NOT_USE
sample-token
localhost
*.luffy.local
```

### 6. Auditability

Every important action should create an audit event.

Audit events should capture:

```text
event_id
actor
source_service
target_service
action
decision
reason
timestamp
request_id
risk_level
```

Audit required for:

```text
Access request
Approval/rejection
Provisioning
Deprovisioning
PAM checkout
PAM session start/end
Gateway block/allow decision
Agent recommendation
Certification decision
```

### 7. Privacy by design

Use fake users and sample data only.

Avoid storing unnecessary personal data.

Preferred sample attributes:

```text
employee_id
lan_id
email
manager_id
department
status
```

Avoid unnecessary sensitive data:

```text
national ID
salary
home address
medical data
real phone numbers
real personal emails
```

### 8. Secure API design

Every API-based service should consider:

```text
Authentication
Authorization
Input validation
Output filtering
Rate limiting
Request ID
Error handling
Security headers
CORS policy
Logging without secrets
```

### 9. GraphQL security

GraphQL should be used in `idp-service` and `iga-service`, but with controls.

Controls:

```text
Disable unrestricted introspection outside local/dev mode.
Limit query depth.
Limit query complexity.
Apply object-level authorization.
Prevent access to unauthorized identities/accounts.
Avoid returning secrets or tokens.
Log high-risk queries.
```

### 10. Database security

For database-backed services:

```text
Use parameterized queries.
Avoid raw dynamic SQL.
Use read-only IAM views where possible.
Separate app tables from IAM aggregation views.
Use least-privilege DB users.
Do not store secrets in plain text.
```

## Responsible AI guardrails

AI agents should help users understand and review IAM risk. They should not silently perform risky changes.

### Allowed agent behavior in early phases

Agents may:

```text
Summarize access risk.
Explain why access looks risky.
Recommend approve/revoke decisions.
Generate onboarding questions.
Generate certification review notes.
Identify missing evidence.
Identify orphan accounts.
Flag machine identity risks.
```

### Disallowed agent behavior in early phases

Agents must not:

```text
Provision access without human approval.
Revoke access without human approval.
Approve access requests automatically.
Modify PAM access silently.
Rotate or expose secrets.
Generate real exploit instructions.
Use real personal data.
Hide uncertainty.
```

### Human-in-the-loop rule

Any high-impact action requires explicit human approval.

High-impact actions include:

```text
Granting admin access
Granting PAM access
Revoking production access
Approving certification decisions
Changing gateway enforcement policies
Changing machine identity secrets/certificates
```

### Agent output requirements

Agent recommendations should include:

```text
Recommendation
Reason
Evidence used
Confidence level
Risk level
Human action required
```

Example:

```json
{
  "recommendation": "REVIEW_BEFORE_APPROVAL",
  "reason": "User is requesting high-risk PAM access and has no current business justification recorded.",
  "confidence": "MEDIUM",
  "risk_level": "HIGH",
  "human_action_required": true
}
```

## Threat modeling baseline

Each service should have a basic threat model before implementation.

Use this structure:

```text
Service name
Assets protected
Trust boundaries
Main actors
Main abuse cases
Security controls
Audit events
Open risks
```

Example abuse cases:

```text
User approves their own access.
Unmatched account keeps active entitlement.
PAM emergency access is used without review.
API endpoint exposes sensitive fields.
GraphQL query leaks another user's access.
Machine identity secret is overdue for rotation.
Gateway is bypassed for sensitive action.
```

## Supply chain and code safety

Before adding dependencies:

```text
Use minimal dependencies.
Prefer well-known maintained libraries.
Avoid copying random code.
Pin dependency versions later.
Add dependency scanning later.
Add secret scanning later.
Add linting and tests before major code.
```

## Logging standard

Logs must not contain:

```text
Passwords
Tokens
Secrets
Private keys
Full certificate private material
Sensitive personal data
```

Logs should contain:

```text
request_id
event_id
actor
service
action
status
reason
risk_level
timestamp
```

## Security gates before coding

Before building each service, define:

```text
1. What data does this service store?
2. What APIs does it expose?
3. Who can call those APIs?
4. What actions must be audited?
5. What data must never be logged?
6. What is the default safe behavior?
7. What can agents see or recommend?
8. What requires human approval?
```

## Project-level non-goals

Luffy should not be used to:

```text
Store real company data
Store real secrets
Attack real systems
Bypass authentication
Build exploit tooling
Automate harmful access changes
Replace production IAM tools
```

## Final rule

Build the lab so every feature can answer these questions:

```text
Is it secure by default?
Is it auditable?
Is it least privilege?
Is it explainable?
Can a human review risky actions?
Can we detect misuse later?
```
