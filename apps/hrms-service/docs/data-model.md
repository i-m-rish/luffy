# HRMS Service Data Model

## Entity: worker

Represents a person or workforce record.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `worker_id` | string | Yes | HRMS native worker ID |
| `employee_id` | string | Yes | Unique employee/workforce identifier |
| `first_name` | string | Yes | Fake/sample first name |
| `last_name` | string | Yes | Fake/sample last name |
| `display_name` | string | Yes | Human-readable name |
| `email` | string | Yes | Fake/sample corporate email |
| `worker_type` | string | Yes | `EMPLOYEE`, `CONTRACTOR`, `SERVICE`, `INTERN` |
| `employment_status` | string | Yes | `ACTIVE`, `INACTIVE`, `TERMINATED`, `ON_LEAVE` |
| `department_id` | string | Yes | References department |
| `position_id` | string | Yes | References position |
| `manager_employee_id` | string | No | Manager employee ID |
| `location` | string | Yes | Work location |
| `start_date` | string | Yes | Start date |
| `termination_date` | string | No | Termination date when applicable |
| `last_updated_at` | string | Yes | Last update timestamp |

## Entity: department

Represents organization structure.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `department_id` | string | Yes | Unique department ID |
| `department_name` | string | Yes | Department name |
| `department_owner_employee_id` | string | No | Owner/leader employee ID |
| `cost_center` | string | No | Fake/sample cost center |
| `status` | string | Yes | `ACTIVE`, `INACTIVE` |

## Entity: position

Represents job/role context.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `position_id` | string | Yes | Unique position ID |
| `job_title` | string | Yes | Job title |
| `job_family` | string | Yes | Job family/category |
| `risk_category` | string | Yes | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `status` | string | Yes | `ACTIVE`, `INACTIVE` |

## Entity: lifecycle_event

Represents a worker lifecycle change.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `event_id` | string | Yes | Unique event ID |
| `employee_id` | string | Yes | Worker employee ID |
| `event_type` | string | Yes | Lifecycle event type |
| `effective_date` | string | Yes | Date event becomes effective |
| `old_value` | object/string | No | Previous value when relevant |
| `new_value` | object/string | No | New value when relevant |
| `status` | string | Yes | `PENDING`, `PROCESSED`, `CANCELLED`, `FAILED` |
| `created_at` | string | Yes | Event creation timestamp |

## Lifecycle event types

```text
JOINER
MOVER
LEAVER
MANAGER_CHANGE
DEPARTMENT_CHANGE
LOCATION_CHANGE
WORKER_TYPE_CHANGE
REHIRE
TERMINATION_RESCIND
```

## Correlation attributes for downstream systems

Preferred identifiers:

```text
employee_id
email
manager_employee_id
```

## Privacy rule

Do not add unnecessary sensitive HR data.

Avoid:

```text
salary
national ID
home address
medical data
real personal phone number
real personal email
```
