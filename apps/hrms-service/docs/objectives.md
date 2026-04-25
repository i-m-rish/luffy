# HRMS Service Objectives

## Service name

`hrms-service`

## Simulated platform type

Human Resource Management System.

Examples of real-world platform categories:

```text
Workday
SAP SuccessFactors
Oracle HCM
PeopleSoft
```

## Primary learning objective

Learn how authoritative HR data drives identity lifecycle management and SailPoint-style joiner, mover, and leaver governance.

## What this service teaches

```text
Authoritative identity source
Worker lifecycle
Joiner/mover/leaver events
Manager relationship
Department and position context
Birthright access inputs
Leaver deprovisioning trigger
Mover access review trigger
```

## Milestone 1 scope

Milestone 1 creates:

```text
worker data model
department data model
position data model
lifecycle event model
sample fake data later
service design docs
```

## Out of scope for Milestone 1

```text
Real HR data
Real HRMS integration
Payroll data
Salary data
National ID data
Full HR admin UI
Production workflow engine
```

## Future scope

Later versions may add:

```text
REST API
SQLite/PostgreSQL storage
joiner event simulation
mover event simulation
leaver event simulation
identity sync to idp-service
lifecycle feed to iga-service
minimal HR admin UI
```
