from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DatabaseConfig:
    path: Path = Path("saves/cosmic_confrontation.sqlite3")


DEFAULT_CONFIG = DatabaseConfig()
