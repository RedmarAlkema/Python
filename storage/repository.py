from __future__ import annotations

import json
from typing import Any, Callable

from storage.database import Database
from storage.queries import GameQueries
from storage.statistics import GameDataExtractor, StatisticsBuilder
from storage.writer import NormalizedGameWriter


class GameRepository:
    def __init__(
        self,
        database: Database | None = None,
        queries: GameQueries | None = None,
        statistics_builder: StatisticsBuilder | None = None,
        writer: NormalizedGameWriter | None = None,
    ) -> None:
        extractor = GameDataExtractor()
        self.database = database or Database()
        self.queries = queries or GameQueries()
        self.statistics_builder = statistics_builder or StatisticsBuilder(extractor)
        self.writer = writer or NormalizedGameWriter(extractor)

    def initialize(self) -> None:
        connection = self.database.connect()
        connection.close()

    def load_saved_games(self) -> list[dict[str, Any]]:
        return self._read(self.queries.load_saved_games)

    def load_game_statistics(self) -> list[dict[str, Any]]:
        return self._read(self.queries.load_statistics)

    def save_game_data(self, game_data: dict[str, Any]) -> None:
        game_id = str(game_data.get("id"))
        stats = self.statistics_builder.build(game_data)

        def write(cursor) -> None:
            self._save_game_row(cursor, game_id, game_data)
            self.writer.replace(cursor, game_id, game_data, stats)

        self._write(write)

    def backfill_existing_rows(self) -> None:
        def write(cursor) -> None:
            for game_id, game_data in self.queries.missing_state_rows(cursor):
                self.writer.replace(cursor, game_id, game_data, self.statistics_builder.build(game_data))
            for game_id, game_data in self.queries.incomplete_normalized_rows(cursor):
                self.writer.replace(cursor, game_id, game_data, self.statistics_builder.build(game_data))

        self._write(write)

    def _read(self, query: Callable[[Any], list[dict[str, Any]]]) -> list[dict[str, Any]]:
        connection = self.database.connect()
        try:
            cursor = connection.cursor()
            try:
                return query(cursor)
            finally:
                cursor.close()
        finally:
            connection.close()

    def _write(self, action: Callable[[Any], None]) -> None:
        connection = self.database.connect()
        try:
            cursor = connection.cursor()
            try:
                action(cursor)
            finally:
                cursor.close()
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _save_game_row(self, cursor, game_id: str, game_data: dict[str, Any]) -> None:
        updated_at = game_data.get("updated_at") or game_data.get("last_saved_at") or game_data.get("started_at", "")
        cursor.execute(
            """
            INSERT INTO games (id, nickname, started_at, updated_at, size, winner, game_over, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                nickname = excluded.nickname,
                started_at = excluded.started_at,
                updated_at = excluded.updated_at,
                size = excluded.size,
                winner = excluded.winner,
                game_over = excluded.game_over,
                data = excluded.data
            """,
            (
                game_id,
                game_data.get("nickname", "Speler"),
                game_data.get("started_at", updated_at),
                updated_at,
                int(game_data.get("size", 0)),
                game_data.get("winner"),
                1 if game_data.get("game_over") else 0,
                json.dumps(game_data),
            ),
        )
