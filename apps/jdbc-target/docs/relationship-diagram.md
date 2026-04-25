# JDBC Target Relationship Diagram

## Entity relationship diagram

```mermaid
erDiagram
    USERS ||--o{ USER_ROLES : receives
    ROLES ||--o{ USER_ROLES : assigned_as

    USERS {
        integer user_id PK
        string employee_id UK
        string lan_id UK
        string email UK
        string display_name
        string department
        string account_status
        string created_at
        string updated_at
    }

    ROLES {
        integer role_id PK
        string role_code UK
        string role_name
        string role_description
        string risk_level
        string role_status
        string created_at
        string updated_at
    }

    USER_ROLES {
        integer user_role_id PK
        integer user_id FK
        integer role_id FK
        string assignment_status
        string assigned_by
        string assigned_at
        string revoked_by
        string revoked_at
        string assignment_reason
    }
```

## Relationship explanation

```text
One user can have many role assignments.
One role can be assigned to many users.
user_roles is the many-to-many mapping table.
```

## IGA interpretation

```text
users       -> accounts
roles       -> entitlements
user_roles  -> account-entitlement assignments
```
