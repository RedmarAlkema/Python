from __future__ import annotations

import sqlite3

from storage.config import DEFAULT_CONFIG
from storage.database import Database
from storage.repository import GameRepository

SQLITE_DATABASE_PATH = DEFAULT_CONFIG.path

_repository = GameRepository()


def _connect() -> sqlite3.Connection:
    return Database().connect()


def initialize_database() -> None:
    _repository.initialize()


def backfill_database() -> None:
    _repository.backfill_existing_rows()


def load_saved_games() -> list[dict]:
    return _repository.load_saved_games()


def save_game_data(game_data: dict) -> None:
    _repository.save_game_data(game_data)


def load_game_statistics() -> list[dict]:
    return _repository.load_game_statistics()
