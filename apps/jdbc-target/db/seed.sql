-- JDBC Target Seed Data
-- Uses fake sample data only.

INSERT INTO users (
    user_id,
    employee_id,
    lan_id,
    email,
    display_name,
    department,
    account_status,
    created_at,
    updated_at
) VALUES
(1, '1001', 'RSINGH01', 'rishabh.singh@example.com', 'Rishabh Singh', 'Cybersecurity Operations', 'ACTIVE', '2026-01-01T09:00:00Z', '2026-01-01T09:00:00Z'),
(2, '1002', 'AKUMAR01', 'amit.kumar@example.com', 'Amit Kumar', 'Risk Management', 'ACTIVE', '2026-01-02T09:00:00Z', '2026-01-02T09:00:00Z'),
(3, '1003', 'NSHARMA01', 'neha.sharma@example.com', 'Neha Sharma', 'Asset Management', 'ACTIVE', '2026-01-03T09:00:00Z', '2026-01-03T09:00:00Z'),
(4, '1004', 'PKAPOOR01', 'priya.kapoor@example.com', 'Priya Kapoor', 'Security Engineering', 'ACTIVE', '2026-01-04T09:00:00Z', '2026-01-04T09:00:00Z'),
(5, '9001', 'ORPHAN01', 'orphan.account@example.com', 'Orphan Account', 'Unknown', 'ACTIVE', '2026-01-05T09:00:00Z', '2026-01-05T09:00:00Z');

INSERT INTO roles (
    role_id,
    role_code,
    role_name,
    role_description,
    risk_level,
    role_status,
    created_at,
    updated_at
) VALUES
(1, 'ASSET_VIEWER', 'Asset Viewer', 'Can view security asset inventory and basic asset metadata.', 'LOW', 'ACTIVE', '2026-01-01T09:00:00Z', '2026-01-01T09:00:00Z'),
(2, 'ASSET_OWNER', 'Asset Owner', 'Can own assets and update asset ownership details.', 'MEDIUM', 'ACTIVE', '2026-01-01T09:00:00Z', '2026-01-01T09:00:00Z'),
(3, 'REMEDIATION_MANAGER', 'Remediation Manager', 'Can manage remediation tasks for security asset issues.', 'HIGH', 'ACTIVE', '2026-01-01T09:00:00Z', '2026-01-01T09:00:00Z'),
(4, 'COMPLIANCE_REVIEWER', 'Compliance Reviewer', 'Can review asset compliance posture and evidence.', 'MEDIUM', 'ACTIVE', '2026-01-01T09:00:00Z', '2026-01-01T09:00:00Z'),
(5, 'SYSTEM_ADMINISTRATOR', 'System Administrator', 'Can administer users, roles, and security asset platform settings.', 'CRITICAL', 'ACTIVE', '2026-01-01T09:00:00Z', '2026-01-01T09:00:00Z');

INSERT INTO user_roles (
    user_role_id,
    user_id,
    role_id,
    assignment_status,
    assigned_by,
    assigned_at,
    revoked_by,
    revoked_at,
    assignment_reason
) VALUES
(1, 1, 1, 'ACTIVE', 'APP_OWNER', '2026-01-10T10:00:00Z', NULL, NULL, 'Default read access for cybersecurity operations.'),
(2, 2, 4, 'ACTIVE', 'APP_OWNER', '2026-01-10T10:05:00Z', NULL, NULL, 'Risk team compliance review responsibility.'),
(3, 3, 2, 'ACTIVE', 'APP_OWNER', '2026-01-10T10:10:00Z', NULL, NULL, 'Asset ownership responsibility.'),
(4, 4, 5, 'ACTIVE', 'SECURITY_ADMIN', '2026-01-10T10:15:00Z', NULL, NULL, 'Security engineering platform administration.'),
(5, 5, 3, 'ACTIVE', 'UNKNOWN', '2026-01-10T10:20:00Z', NULL, NULL, 'Intentionally seeded orphan-style account for correlation testing.');
