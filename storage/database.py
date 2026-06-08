from __future__ import annotations

import sqlite3

from storage.config import DatabaseConfig, DEFAULT_CONFIG
from storage.sqlite import SQLITE_SCHEMA


class Database:
    def __init__(self, config: DatabaseConfig = DEFAULT_CONFIG) -> None:
        self.config = config

    def connect(self) -> sqlite3.Connection:
        self.config.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.config.path)
        connection.row_factory = self._dict_factory
        connection.execute("PRAGMA foreign_keys = ON")
        self._ensure_schema(connection)
        return connection

    @staticmethod
    def _dict_factory(cursor: sqlite3.Cursor, row: tuple) -> dict:
        return {column[0]: row[index] for index, column in enumerate(cursor.description)}

    def _ensure_schema(self, connection: sqlite3.Connection) -> None:
        cursor = connection.cursor()
        try:
            for statement in SQLITE_SCHEMA:
                cursor.execute(statement)
        finally:
            cursor.close()
        connection.commit()
