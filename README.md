# Luffy

Luffy is a practical cybersecurity IAM integration lab for learning SailPoint-style application onboarding, governance, and privileged access patterns.

The project simulates six enterprise IAM/cybersecurity components:

1. `idp-service` - identity provider / authoritative identity source
2. `iga-service` - SailPoint-like identity governance service
3. `scim-target` - SCIM-enabled endpoint security application
4. `jdbc-target` - database/JDBC-style security asset application
5. `webservices-target` - REST Web Services-style risk and incident application
6. `pam-target` - CyberArk-like privileged access management application

## Goal

Build a hands-on lab that demonstrates:

- Identity aggregation
- Account aggregation
- Account correlation
- Entitlement catalog normalization
- Access request and approval workflow
- Provisioning through SCIM, JDBC-style data, REST APIs, and PAM-style privileged access flows
- Privileged access governance
- Credential checkout and session audit concepts
- Governance and certification-style reporting

## Target structure

```text
luffy/
├── apps/
│   ├── idp-service/
│   ├── iga-service/
│   ├── scim-target/
│   ├── jdbc-target/
│   ├── webservices-target/
│   └── pam-target/
├── docs/
│   ├── architecture.md
│   ├── naming-standards.md
│   └── pam-target.md
├── scripts/
├── tests/
└── README.md
```

## Build order

1. `jdbc-target`
2. `webservices-target`
3. `scim-target`
4. `pam-target`
5. `idp-service`
6. `iga-service`

## Documentation

- [Architecture](docs/architecture.md)
- [Naming Standards](docs/naming-standards.md)
- [PAM Target](docs/pam-target.md)
