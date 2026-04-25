-- JDBC Target IAM-Safe Views
-- These views simulate the controlled read layer exposed to IGA/SailPoint.

DROP VIEW IF EXISTS vw_iam_account_entitlements;
DROP VIEW IF EXISTS vw_iam_entitlements;
DROP VIEW IF EXISTS vw_iam_accounts;

CREATE VIEW vw_iam_accounts AS
SELECT
    u.user_id AS account_id,
    u.employee_id,
    u.lan_id,
    u.email,
    u.display_name,
    u.department,
    u.account_status,
    CASE
        WHEN u.account_status = 'ACTIVE' THEN 'true'
        ELSE 'false'
    END AS active,
    u.created_at,
    u.updated_at
FROM users u;

CREATE VIEW vw_iam_entitlements AS
SELECT
    r.role_id AS entitlement_id,
    r.role_code AS entitlement_code,
    r.role_name AS entitlement_name,
    r.role_description AS entitlement_description,
    r.risk_level,
    r.role_status AS entitlement_status,
    CASE
        WHEN r.role_status = 'ACTIVE' THEN 'true'
        ELSE 'false'
    END AS active,
    r.created_at,
    r.updated_at
FROM roles r;

CREATE VIEW vw_iam_account_entitlements AS
SELECT
    ur.user_role_id AS assignment_id,
    u.user_id AS account_id,
    u.employee_id,
    u.lan_id,
    u.email,
    r.role_id AS entitlement_id,
    r.role_code AS entitlement_code,
    r.role_name AS entitlement_name,
    r.risk_level,
    ur.assignment_status,
    ur.assigned_by,
    ur.assigned_at,
    ur.revoked_by,
    ur.revoked_at,
    ur.assignment_reason
FROM user_roles ur
JOIN users u ON ur.user_id = u.user_id
JOIN roles r ON ur.role_id = r.role_id;
