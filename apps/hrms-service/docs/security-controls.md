# HRMS Service Security Controls

## Security posture

`hrms-service` is an authoritative source for identity lifecycle data.

Because HRMS data drives downstream identity and access actions, it must be treated as high-integrity data.

## Controls

### Privacy by design

Use fake/sample data only.

Do not store:

```text
salary
national ID
government ID
home address
medical data
real phone number
real personal email
```

### Least privilege

Future downstream access should be limited:

```text
idp-service can read worker identity attributes.
iga-service can read lifecycle and manager/department context.
No downstream service should modify HRMS worker records by default.
```

### Data minimization

Expose only required fields downstream:

```text
employee_id
name
email
worker_type
employment_status
department_id
position_id
manager_employee_id
location
start_date
termination_date
```

### Lifecycle integrity

High-impact events must be auditable:

```text
LEAVER
TERMINATION_RESCIND
WORKER_TYPE_CHANGE
MANAGER_CHANGE
DEPARTMENT_CHANGE
```

### Future API controls

When REST APIs are added:

```text
Require authentication.
Require authorization for worker changes.
Validate all input.
Use safe error messages.
Use request_id for traceability.
Do not log unnecessary personal data.
Rate-limit admin write endpoints.
```

## Risk conditions to detect later

```text
Worker terminated but identity still active.
Worker moved departments but old high-risk access remains.
Manager missing for active worker.
Worker type changed to contractor but privileged access remains.
Lifecycle event failed but downstream identity changed.
```
