# ZSP JIT Enterprise App

`zsp-jit-app` is a protected enterprise SaaS-style target application.

It demonstrates:

```text
OIDC-style authentication through idp-service
JIT user provisioning on first login
zero standing privilege access model
time-bound privileged sessions
application RBAC
audit events
enterprise app UI
```

## Why this app exists

This app is intentionally different from IGA.

```text
IdP authenticates the user.
IGA governs whether access should exist.
ZSP JIT App enforces app-local access and temporary privilege.
```

## Run locally

```bash
cd apps/zsp-jit-app/src
uvicorn fastapi_app:app --reload --port 8003
```

Open:

```text
http://127.0.0.1:8003
```

## Login flow

```text
User opens ZSP app
↓
ZSP redirects to IdP /oauth/authorize
↓
IdP authenticates user
↓
IdP redirects to ZSP /auth/callback
↓
ZSP exchanges authorization code for claims
↓
ZSP creates local user account just-in-time
↓
ZSP maps IdP role claim to app role
↓
User can request temporary privilege
```

## Demo role mapping

```text
IGA_ADMIN       -> ZSP_ADMIN
ACCESS_REVIEWER -> ZSP_APPROVER
APP_OWNER       -> ZSP_OPERATOR
READ_ONLY       -> ZSP_VIEWER
```

## Scope

This is a local learning app. It is not production authentication.

Missing production controls intentionally:

```text
JWT signing
PKCE
client secret
real database
HTTPS-only cookies
persistent audit logs
```
