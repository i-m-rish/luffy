-- JDBC Target Schema
-- Simulates a database-backed security asset operations application.

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS user_roles;
DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    employee_id TEXT NOT NULL,
    lan_id TEXT NOT NULL,
    email TEXT NOT NULL,
    display_name TEXT NOT NULL,
    department TEXT NOT NULL,
    account_status TEXT NOT NULL CHECK (account_status IN ('ACTIVE', 'INACTIVE', 'LOCKED', 'TERMINATED')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(employee_id),
    UNIQUE(lan_id),
    UNIQUE(email)
);

CREATE TABLE roles (
    role_id INTEGER PRIMARY KEY,
    role_code TEXT NOT NULL UNIQUE,
    role_name TEXT NOT NULL,
    role_description TEXT NOT NULL,
    risk_level TEXT NOT NULL CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    role_status TEXT NOT NULL CHECK (role_status IN ('ACTIVE', 'INACTIVE')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE user_roles (
    user_role_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    assignment_status TEXT NOT NULL CHECK (assignment_status IN ('ACTIVE', 'REVOKED')),
    assigned_by TEXT NOT NULL,
    assigned_at TEXT NOT NULL,
    revoked_by TEXT,
    revoked_at TEXT,
    assignment_reason TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (role_id) REFERENCES roles(role_id),
    UNIQUE(user_id, role_id)
);

CREATE INDEX idx_users_employee_id ON users(employee_id);
CREATE INDEX idx_users_lan_id ON users(lan_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_roles_role_code ON roles(role_code);
CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_role_id ON user_roles(role_id);
CREATE INDEX idx_user_roles_status ON user_roles(assignment_status);
