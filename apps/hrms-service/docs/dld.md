# HRMS Service DLD

## Detailed design

`hrms-service` starts as a JSON-backed design-first service in Milestone 1.

It will later become a Python REST API with database storage.

## Modules

Milestone 1 expected files:

```text
data/workers.json
data/departments.json
data/positions.json
data/lifecycle-events.json
```

Future modules:

```text
src/models.py          -> worker, department, position, lifecycle event models
src/repository.py      -> data access layer
src/service.py         -> lifecycle business logic
src/api.py             -> REST API routes
src/audit.py           -> audit event creation
```

## Processing flow

### Joiner

```text
1. Worker record is created.
2. JOINER lifecycle event is created.
3. idp-service later creates digital identity.
4. iga-service later evaluates birthright access.
```

### Mover

```text
1. Worker department, position, manager, or location changes.
2. MOVER or specific change event is created.
3. iga-service later reviews old access and evaluates new access.
```

### Leaver

```text
1. Worker employment_status becomes TERMINATED.
2. LEAVER lifecycle event is created.
3. idp-service later disables digital identity.
4. iga-service later triggers deprovisioning.
```

## Validation rules

### workers

```text
employee_id required and unique
email required and unique
employment_status must be ACTIVE, INACTIVE, TERMINATED, or ON_LEAVE
worker_type must be EMPLOYEE, CONTRACTOR, SERVICE, or INTERN
manager_employee_id should refer to another worker where applicable
```

### departments

```text
department_id required and unique
department_name required
status must be ACTIVE or INACTIVE
```

### positions

```text
position_id required and unique
job_title required
risk_category must be LOW, MEDIUM, HIGH, or CRITICAL
status must be ACTIVE or INACTIVE
```

### lifecycle_events

```text
event_id required and unique
employee_id required
event_type must be a supported lifecycle event type
effective_date required
status must be PENDING, PROCESSED, CANCELLED, or FAILED
```

## Error handling

Milestone 1 tests should catch:

```text
missing required fields
invalid status values
duplicate employee_id
duplicate email
lifecycle event for unknown worker
```

## Audit behavior

Future HRMS changes should produce audit events for:

```text
worker created
worker updated
worker terminated
department changed
manager changed
position changed
lifecycle event created
```

## Security decision points

```text
No real HR data.
No salary, government ID, home address, or medical data.
Downstream services should receive only required identity lifecycle attributes.
Leaver events are high-impact and must be audited.
```
