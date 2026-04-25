from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ZspSettings:
    service_name: str = "zsp-jit-app"
    app_title: str = "Luffy ZSP JIT Enterprise App"
    app_description: str = "Enterprise SaaS-style app with IdP login, JIT provisioning, RBAC, and temporary privilege elevation."
    app_version: str = "0.2.0"
    host: str = "127.0.0.1"
    port: int = 8003
    idp_base_url: str = "http://127.0.0.1:8002"
    client_id: str = "luffy-zsp"
    redirect_uri: str = "http://127.0.0.1:8003/auth/callback"
    session_cookie_name: str = "luffy_zsp_session"
    state_cookie_name: str = "luffy_zsp_auth_state"


settings = ZspSettings()
