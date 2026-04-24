# IAM AccessOps Toolkit - Project Plan

## Project idea

Build a small IAM/SailPoint-adjacent toolkit that helps onboarding analysts validate application onboarding inputs before they go to SailPoint, L1 teams, or app owners.

This is not a replacement for SailPoint. It is a helper tool for access onboarding, governance checks, and documentation readiness.

## Why this project makes sense

This project fits real IAM onboarding work:

- Validates application onboarding information
- Checks whether an app is conforming or non-conforming
- Reviews access model data such as roles, entitlements, groups, and owners
- Helps detect feed issues such as missing email, LAN ID mismatch, duplicate accounts, or inconsistent casing
- Generates action items/questions for app teams
- Can later become a small web app or API

## MVP scope

### Phase 1 - Command-line validation tool

Input: CSV or JSON file containing application access data.

Output:

- Validation report
- Missing field report
- Duplicate user/account report
- Feed quality score
- Suggested questions for app team

### Phase 2 - IAM onboarding checklist generator

Input: application details such as auth model, access model, provisioning approach, and feed/API availability.

Output:

- Conforming/non-conforming classification draft
- Questions for app owner/vendor
- Meeting notes template
- Email draft template

### Phase 3 - Simple web UI

Build a simple UI where a user can upload a file and get validation results.

## Suggested tech stack

Start simple:

- Python
- CSV/JSON processing
- Markdown report generation
- Later: FastAPI backend
- Later: React or simple HTML UI

## Initial folder structure

```text
luffy/
├── README.md
├── docs/
│   └── project-plan.md
├── sample-data/
│   └── access-feed-sample.csv
├── src/
│   └── validate_feed.py
└── reports/
```

## First build target

Create a Python script that validates a sample access feed.

Required checks:

1. Required columns exist:
   - employee_id
   - lan_id
   - email
   - account_name
   - entitlement
   - application_name
   - owner

2. Check missing values.

3. Check duplicate account entries.

4. Check whether account_name format is consistent.

5. Generate a markdown report.

## Example use case

An app team provides a feed file before SailPoint onboarding. The analyst runs this tool to check whether the feed is clean enough for onboarding and certification governance.

## Resume framing

Built an IAM AccessOps validation toolkit to automate pre-onboarding checks for application access feeds, identify data quality gaps, and generate governance-ready reports for SailPoint onboarding workflows.
