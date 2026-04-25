from __future__ import annotations

import hashlib
import hmac
import time
import uuid
from dataclasses import dataclass
from typing import Any

AUTHORIZATION_CODES: dict[str, dict[str, Any]] = {}
ACCESS_TOKENS: dict[str, dict[str, Any]] = {}

REGISTERED_CLIENTS = {
    "luffy-iga": {
        "client_name": "Luffy IGA Service",
        "redirect_uri": "http://127.0.0.1:8001/auth/callback",
        "allowed_roles": ["IGA_ADMIN", "ACCESS_REVIEWER", "APP_OWNER", "READ_ONLY"],
    }
}


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class IdpUser:
    username: str
    display_name: str
    email: str
    role: str
    password_hash: str

    def claims(self) -> dict[str, Any]:
        return {
            "sub": self.username,
            "preferred_username": self.username,
            "name": self.display_name,
            "email": self.email,
            "role": self.role,
        }


IDP_USERS = {
    "admin": IdpUser(
        username="admin",
        display_name="IGA Administrator",
        email="iga.admin@example.com",
        role="IGA_ADMIN",
        password_hash=hash_password("admin123"),
    ),
    "reviewer": IdpUser(
        username="reviewer",
        display_name="Access Reviewer",
        email="access.reviewer@example.com",
        role="ACCESS_REVIEWER",
        password_hash=hash_password("reviewer123"),
    ),
    "owner": IdpUser(
        username="owner",
        display_name="Application Owner",
        email="app.owner@example.com",
        role="APP_OWNER",
        password_hash=hash_password("owner123"),
    ),
    "reader": IdpUser(
        username="reader",
        display_name="Read Only User",
        email="read.only@example.com",
        role="READ_ONLY",
        password_hash=hash_password("reader123"),
    ),
}


def authenticate_user(username: str, password: str) -> IdpUser | None:
    user = IDP_USERS.get(username)
    if user is None:
        return None
    if not hmac.compare_digest(hash_password(password), user.password_hash):
        return None
    return user


def validate_client(client_id: str, redirect_uri: str) -> bool:
    client = REGISTERED_CLIENTS.get(client_id)
    return client is not None and client["redirect_uri"] == redirect_uri


def create_authorization_code(client_id: str, redirect_uri: str, user: IdpUser) -> str:
    code = str(uuid.uuid4())
    AUTHORIZATION_CODES[code] = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "claims": user.claims(),
        "created_at": time.time(),
    }
    return code


def exchange_code_for_token(code: str, client_id: str, redirect_uri: str) -> dict[str, Any] | None:
    auth_code = AUTHORIZATION_CODES.pop(code, None)
    if auth_code is None:
        return None
    if auth_code["client_id"] != client_id or auth_code["redirect_uri"] != redirect_uri:
        return None
    if time.time() - auth_code["created_at"] > 300:
        return None

    token = str(uuid.uuid4())
    ACCESS_TOKENS[token] = {
        "claims": auth_code["claims"],
        "client_id": client_id,
        "issued_at": time.time(),
    }
    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": 3600,
        "claims": auth_code["claims"],
    }


def get_userinfo(access_token: str) -> dict[str, Any] | None:
    token_data = ACCESS_TOKENS.get(access_token)
    if token_data is None:
        return None
    if time.time() - token_data["issued_at"] > 3600:
        ACCESS_TOKENS.pop(access_token, None)
        return None
    return token_data["claims"]
