# Security Policy

## Purpose

Luffy is a cybersecurity IAM learning lab. It must not contain real secrets, real production data, or real employee/customer data.

## Security rules

Do not commit:

```text
passwords
API tokens
OAuth client secrets
private keys
real certificates
real employee data
real customer data
production URLs
```

Use placeholders such as:

```text
EXAMPLE_SECRET_DO_NOT_USE
sample-token
localhost
*.luffy.local
```

## Reporting security issues

For this learning repository, open a GitHub issue if you find:

```text
accidental secret-like values
unsafe sample patterns
missing authentication/authorization checks
unsafe logging guidance
insecure documentation examples
```

Do not use this repository to report vulnerabilities in real third-party systems.

## Responsible AI rule

Future agents must be recommendation-first.

They must not silently:

```text
approve access
provision access
revoke access
modify PAM access
rotate secrets
change gateway enforcement policies
```

High-impact actions require explicit human approval.
