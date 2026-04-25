from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppSettings:
    service_name: str = "iga-service"
    app_title: str = "Luffy IGA Service"
    app_version: str = "0.3.0"
    app_description: str = "Enterprise-style read-only IGA governance app over normalized sample data."
    host: str = "127.0.0.1"
    port: int = 8001
    app_dir: Path = Path(__file__).resolve().parents[2]

    @property
    def data_dir(self) -> Path:
        return self.app_dir / "data"


settings = AppSettings()
