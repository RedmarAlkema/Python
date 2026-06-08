from __future__ import annotations

import json
from typing import Any


class GameQueries:
    def load_saved_games(self, cursor) -> list[dict[str, Any]]:
        cursor.execute(
            """
            SELECT state_json
            FROM game_states
            JOIN games ON games.id = game_states.game_id
            ORDER BY games.updated_at
            """
        )
        return self._decode_game_rows(cursor.fetchall(), "state_json")

    def load_statistics(self, cursor) -> list[dict[str, Any]]:
        cursor.execute(
            """
            SELECT
                games.nickname,
                games.started_at,
                games.updated_at,
                games.size,
                COALESCE(games.winner, 'nog bezig') AS winner,
                game_statistics.turns,
                game_statistics.player_hits,
                game_statistics.enemy_hits,
                game_statistics.player_misses,
                game_statistics.enemy_misses,
                game_statistics.total_hits,
                game_statistics.total_misses,
                game_statistics.hit_miss_ratio,
                game_statistics.player_ships_left,
                game_statistics.enemy_ships_left,
                game_statistics.player_ships_lost AS player_lost,
                game_statistics.enemy_ships_lost AS enemy_lost,
                game_statistics.powerups_used,
                game_statistics.cells_moved,
                game_statistics.asteroid_hits,
                game_statistics.player_asteroid_hits,
                game_statistics.enemy_asteroid_hits
            FROM game_statistics
            JOIN games ON games.id = game_statistics.game_id
            ORDER BY games.updated_at
            """
        )
        return list(cursor.fetchall())

    def missing_state_rows(self, cursor) -> list[tuple[str, dict[str, Any]]]:
        cursor.execute(
            """
            SELECT games.id, games.data
            FROM games
            LEFT JOIN game_states ON game_states.game_id = games.id
            WHERE game_states.game_id IS NULL AND games.data IS NOT NULL
            """
        )
        return self._decode_id_rows(cursor.fetchall(), "id", "data")

    def incomplete_normalized_rows(self, cursor) -> list[tuple[str, dict[str, Any]]]:
        cursor.execute(
            """
            SELECT game_states.game_id, game_states.state_json
            FROM game_states
            LEFT JOIN game_statistics ON game_statistics.game_id = game_states.game_id
            LEFT JOIN game_ships ON game_ships.game_id = game_states.game_id
            WHERE game_statistics.game_id IS NULL OR game_ships.game_id IS NULL
            GROUP BY game_states.game_id, game_states.state_json
            """
        )
        return self._decode_id_rows(cursor.fetchall(), "game_id", "state_json")

    def _decode_game_rows(self, rows: list[dict[str, Any]], data_key: str) -> list[dict[str, Any]]:
        games = []
        for row in rows:
            try:
                games.append(json.loads(row[data_key]))
            except json.JSONDecodeError:
                continue
        return games

    def _decode_id_rows(self, rows: list[dict[str, Any]], id_key: str, data_key: str) -> list[tuple[str, dict[str, Any]]]:
        decoded = []
        for row in rows:
            try:
                decoded.append((str(row[id_key]), json.loads(row[data_key])))
            except json.JSONDecodeError:
                continue
        return decoded
