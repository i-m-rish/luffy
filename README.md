# Luffy

Luffy is a practical IAM integration lab for learning SailPoint-style application onboarding and governance patterns.

The project simulates five enterprise IAM components:

1. `idp-service` - identity provider / authoritative identity source
2. `iga-service` - SailPoint-like identity governance service
3. `scim-target` - SCIM-enabled target application
4. `jdbc-target` - database/JDBC-style target application
5. `webservices-target` - REST Web Services-style target application

## Goal

Build a hands-on lab that demonstrates:

- Identity aggregation
- Account aggregation
- Account correlation
- Entitlement catalog normalization
- Access request and approval workflow
- Provisioning through SCIM, JDBC-style data, and REST APIs
- Governance and certification-style reporting

## Target structure

```text
luffy/
├── apps/
│   ├── idp-service/
│   ├── iga-service/
│   ├── scim-target/
│   ├── jdbc-target/
│   └── webservices-target/
├── docs/
│   ├── architecture.md
│   └── naming-standards.md
├── scripts/
├── tests/
└── README.md
```

## Build order

1. `jdbc-target`
2. `webservices-target`
3. `scim-target`
4. `idp-service`
5. `iga-service`

## Documentation

- [Architecture](docs/architecture.md)
- [Naming Standards](docs/naming-standards.md)
