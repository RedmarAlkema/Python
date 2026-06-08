from __future__ import annotations

import json
from typing import Any

from storage.statistics import GameDataExtractor


class NormalizedGameWriter:
    def __init__(self, extractor: GameDataExtractor | None = None) -> None:
        self.extractor = extractor or GameDataExtractor()

    def replace(self, cursor, game_id: str, game_data: dict[str, Any], stats: dict[str, Any]) -> None:
        cursor.execute(
            """
            INSERT INTO game_states (game_id, state_json)
            VALUES (?, ?)
            ON CONFLICT(game_id) DO UPDATE SET state_json = excluded.state_json
            """,
            (game_id, json.dumps(game_data)),
        )
        self._save_actions(cursor, game_id, self.extractor.actions(game_data))
        self._save_statistics(cursor, game_id, stats)
        self._save_ships(cursor, game_id, "player", self.extractor.ships(game_data, "player"))
        self._save_ships(cursor, game_id, "enemy", self.extractor.ships(game_data, "enemy"))
        self._save_asteroids(cursor, game_id, "player", self.extractor.board(game_data, "player").get("asteroids", []))
        self._save_asteroids(cursor, game_id, "enemy", self.extractor.board(game_data, "enemy").get("asteroids", []))

    def _save_actions(self, cursor, game_id: str, actions: list[dict[str, Any]]) -> None:
        cursor.execute("DELETE FROM game_actions WHERE game_id = ?", (game_id,))
        rows = [
            (
                game_id,
                index,
                action.get("time"),
                action.get("actor"),
                action.get("kind"),
                action.get("target"),
                action.get("direction"),
                action.get("description"),
            )
            for index, action in enumerate(actions)
        ]
        cursor.executemany(
            """
            INSERT INTO game_actions
                (game_id, action_index, action_time, actor, kind, target, direction, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    def _save_statistics(self, cursor, game_id: str, stats: dict[str, Any]) -> None:
        cursor.execute(self._statistics_sql(), self._statistics_values(game_id, stats))

    def _save_ships(self, cursor, game_id: str, owner: str, ships: list[dict[str, Any]]) -> None:
        cursor.execute("DELETE FROM game_ships WHERE game_id = ? AND owner = ?", (game_id, owner))
        rows = []
        for ship in ships:
            cells = ship.get("cells", [])
            hits = ship.get("hits", [])
            rows.append(
                (
                    game_id,
                    owner,
                    int(ship.get("id", 0)),
                    ship.get("type") or ship.get("name") or "?",
                    len(cells),
                    json.dumps(cells),
                    json.dumps(hits),
                    len(hits),
                    1 if self.extractor.ship_is_sunk(ship) else 0,
                    1 if ship.get("power_used") else 0,
                    int(ship.get("disabled_turns", 0)),
                )
            )
        cursor.executemany(
            """
            INSERT INTO game_ships
                (game_id, owner, ship_id, ship_type, length, cells_json, hits_json,
                 hits_count, sunk, power_used, disabled_turns)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    def _save_asteroids(self, cursor, game_id: str, owner: str, asteroids: list[dict[str, Any]]) -> None:
        cursor.execute("DELETE FROM game_asteroids WHERE game_id = ? AND owner = ?", (game_id, owner))
        rows = []
        for asteroid in asteroids:
            pos = asteroid.get("pos", [0, 0])
            direction = asteroid.get("direction", [0, 0])
            rows.append((game_id, owner, int(pos[0]), int(pos[1]), int(direction[0]), int(direction[1])))
        cursor.executemany(
            """
            INSERT INTO game_asteroids (game_id, owner, x, y, dx, dy)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    def _statistics_sql(self) -> str:
        return """
            INSERT INTO game_statistics (
                game_id, turns, player_hits, enemy_hits, player_misses, enemy_misses,
                total_hits, total_misses, hit_miss_ratio, player_ships_left,
                enemy_ships_left, player_ships_lost, enemy_ships_lost, powerups_used,
                cells_moved, asteroid_hits, player_asteroid_hits, enemy_asteroid_hits
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(game_id) DO UPDATE SET
                turns = excluded.turns,
                player_hits = excluded.player_hits,
                enemy_hits = excluded.enemy_hits,
                player_misses = excluded.player_misses,
                enemy_misses = excluded.enemy_misses,
                total_hits = excluded.total_hits,
                total_misses = excluded.total_misses,
                hit_miss_ratio = excluded.hit_miss_ratio,
                player_ships_left = excluded.player_ships_left,
                enemy_ships_left = excluded.enemy_ships_left,
                player_ships_lost = excluded.player_ships_lost,
                enemy_ships_lost = excluded.enemy_ships_lost,
                powerups_used = excluded.powerups_used,
                cells_moved = excluded.cells_moved,
                asteroid_hits = excluded.asteroid_hits,
                player_asteroid_hits = excluded.player_asteroid_hits,
                enemy_asteroid_hits = excluded.enemy_asteroid_hits
        """

    def _statistics_values(self, game_id: str, stats: dict[str, Any]) -> tuple:
        return (
            game_id,
            stats["turns"],
            stats["player_hits"],
            stats["enemy_hits"],
            stats["player_misses"],
            stats["enemy_misses"],
            stats["total_hits"],
            stats["total_misses"],
            stats["hit_miss_ratio"],
            stats["player_ships_left"],
            stats["enemy_ships_left"],
            stats["player_lost"],
            stats["enemy_lost"],
            stats["powerups_used"],
            stats["cells_moved"],
            stats["asteroid_hits"],
            stats["player_asteroid_hits"],
            stats["enemy_asteroid_hits"],
        )
