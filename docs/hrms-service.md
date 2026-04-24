# HRMS Service

## Service name

`hrms-service`

## Simulated platform type

Human Resource Management System.

This service simulates a Workday, SAP SuccessFactors, Oracle HCM, or PeopleSoft-style HR system.

## Purpose

`hrms-service` is the authoritative source for employee lifecycle data.

It should answer:

```text
Who is the person?
Are they active or terminated?
What is their employee ID?
What is their department?
Who is their manager?
What is their job title?
What is their worker type?
When did they join?
When did they move teams?
When did they leave?
```

## Difference between HRMS and IdP

| Service | Role | Example real-world equivalent |
|---|---|---|
| `hrms-service` | Authoritative employee record and lifecycle source | Workday, SAP SuccessFactors, Oracle HCM |
| `idp-service` | Authentication and digital identity provider | Entra ID, Okta, Ping |
| `iga-service` | Governance and access orchestration | SailPoint-style IGA |

## Lifecycle flow

```text
hrms-service
  -> employee created / updated / terminated
  -> idp-service creates or updates digital identity
  -> iga-service aggregates identity data
  -> iga-service creates / modifies / removes access
```

## Core HRMS objects

### Worker

```text
worker_id
employee_id
first_name
last_name
display_name
email
worker_type
employment_status
job_title
department
manager_employee_id
location
start_date
termination_date
last_updated_at
```

### Department

```text
department_id
department_name
department_owner
cost_center
status
```

### Position

```text
position_id
job_title
job_family
department_id
risk_category
status
```

### Lifecycle event

```text
event_id
employee_id
event_type
effective_date
old_value
new_value
status
```

## Lifecycle event types

```text
JOINER
MOVER
LEAVER
MANAGER_CHANGE
LOCATION_CHANGE
DEPARTMENT_CHANGE
WORKER_TYPE_CHANGE
REHIRE
TERMINATION_RESCIND
```

## APIs to simulate

```text
GET  /hrms/v1/workers
GET  /hrms/v1/workers/{employeeId}
POST /hrms/v1/workers
PATCH /hrms/v1/workers/{employeeId}
GET  /hrms/v1/departments
GET  /hrms/v1/positions
GET  /hrms/v1/lifecycle-events
POST /hrms/v1/lifecycle-events
```

## Example worker

```json
{
  "worker_id": "wrk-1001",
  "employee_id": "1001",
  "first_name": "Rishabh",
  "last_name": "Singh",
  "display_name": "Rishabh Singh",
  "email": "rishabh.singh@example.com",
  "worker_type": "EMPLOYEE",
  "employment_status": "ACTIVE",
  "job_title": "Security Analyst",
  "department": "Cybersecurity Operations",
  "manager_employee_id": "2001",
  "location": "India",
  "start_date": "2026-01-01",
  "termination_date": null
}
```

## IGA use cases

The `iga-service` should use HRMS data for:

```text
Joiner provisioning
Mover access review
Leaver deprovisioning
Manager-based approval routing
Department-based birthright access
Worker-type based access restrictions
Dormant/terminated user detection
Access review campaign scoping
```

## Example flows

### Joiner

```text
1. New worker is created in hrms-service.
2. idp-service creates digital identity.
3. iga-service aggregates worker and identity data.
4. iga-service assigns birthright access based on department and worker type.
5. iga-service provisions approved access to target apps.
```

### Mover

```text
1. Worker department changes in hrms-service.
2. iga-service detects mover event.
3. Old department access is reviewed.
4. New department birthright access is requested or assigned.
5. High-risk access requires approval.
```

### Leaver

```text
1. Worker is terminated in hrms-service.
2. idp-service disables digital identity.
3. iga-service triggers deprovisioning.
4. Access is removed from SCIM, JDBC, Web Services, and PAM targets.
5. Certification report records removal evidence.
```

## Build priority

Add `hrms-service` before `idp-service` and `iga-service`.

Recommended order after target apps:

```text
1. jdbc-target
2. webservices-target
3. scim-target
4. pam-target
5. hrms-service
6. idp-service
7. iga-service
8. api-gateway-waf
9. siem-detection-service
```

## Why this matters

A real IGA program depends heavily on HRMS data.

Without HRMS, the lab can show access governance.

With HRMS, the lab can show full identity lifecycle governance:

```text
Joiner
Mover
Leaver
Birthright access
Manager approval
Department-based access
Termination-driven deprovisioning
```
