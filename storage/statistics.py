from __future__ import annotations

import re
from typing import Any


class GameDataExtractor:
    def board(self, game_data: dict[str, Any], owner: str) -> dict[str, Any]:
        owner_data = game_data.get(owner, {})
        if not isinstance(owner_data, dict):
            return {}
        board = owner_data.get("board", owner_data)
        return board if isinstance(board, dict) else {}

    def ships(self, game_data: dict[str, Any], owner: str) -> list[dict[str, Any]]:
        ships = self.board(game_data, owner).get("ships", [])
        return ships if isinstance(ships, list) else []

    def actions(self, game_data: dict[str, Any]) -> list[dict[str, Any]]:
        actions = game_data.get("actions", [])
        return actions if isinstance(actions, list) else []

    def ship_is_sunk(self, ship: dict[str, Any]) -> bool:
        return len(ship.get("hits", [])) >= len(ship.get("cells", []))


class StatisticsBuilder:
    def __init__(self, extractor: GameDataExtractor | None = None) -> None:
        self.extractor = extractor or GameDataExtractor()

    def build(self, game_data: dict[str, Any]) -> dict[str, int | float | str | None]:
        actions = self.extractor.actions(game_data)
        player_ships = self.extractor.ships(game_data, "player")
        enemy_ships = self.extractor.ships(game_data, "enemy")
        player_hits = sum(len(ship.get("hits", [])) for ship in player_ships)
        enemy_hits = sum(len(ship.get("hits", [])) for ship in enemy_ships)
        player_misses = self._count_attacks(actions, False, "mis")
        enemy_misses = self._count_attacks(actions, True, "mis")
        total_hits = player_hits + enemy_hits
        total_misses = player_misses + enemy_misses
        player_asteroid_hits = self._count_asteroid_hits(actions, True)
        enemy_asteroid_hits = self._count_asteroid_hits(actions, False)
        return {
            "nickname": game_data.get("nickname", "Speler"),
            "started_at": game_data.get("started_at", "?"),
            "updated_at": game_data.get("updated_at", game_data.get("started_at", "?")),
            "size": int(game_data.get("size", 0)),
            "winner": game_data.get("winner") or "nog bezig",
            "turns": sum(1 for action in actions if action.get("actor") not in {"systeem"}),
            "player_hits": player_hits,
            "enemy_hits": enemy_hits,
            "player_misses": player_misses,
            "enemy_misses": enemy_misses,
            "total_hits": total_hits,
            "total_misses": total_misses,
            "hit_miss_ratio": round(total_hits / max(1, total_misses), 3),
            "player_ships_left": sum(1 for ship in player_ships if not self.extractor.ship_is_sunk(ship)),
            "enemy_ships_left": sum(1 for ship in enemy_ships if not self.extractor.ship_is_sunk(ship)),
            "player_lost": sum(1 for ship in player_ships if self.extractor.ship_is_sunk(ship)),
            "enemy_lost": sum(1 for ship in enemy_ships if self.extractor.ship_is_sunk(ship)),
            "powerups_used": sum(1 for ship in player_ships + enemy_ships if ship.get("power_used")),
            "cells_moved": sum(1 for action in actions if action.get("kind") == "move" or "beweegt" in self._description(action)),
            "asteroid_hits": player_asteroid_hits + enemy_asteroid_hits,
            "player_asteroid_hits": player_asteroid_hits,
            "enemy_asteroid_hits": enemy_asteroid_hits,
        }

    def _count_attacks(self, actions: list[dict[str, Any]], actor_is_player: bool, word: str) -> int:
        total = 0
        for action in actions:
            if self._is_player_action(action) != actor_is_player:
                continue
            text = self._description(action)
            if "aanval" in text or "valt" in text or "missile" in text or "salvo" in text:
                total += len(re.findall(rf"\b{re.escape(word)}\b", text))
        return total

    def _count_asteroid_hits(self, actions: list[dict[str, Any]], actor_is_player: bool) -> int:
        return sum(
            1
            for action in actions
            if self._is_player_action(action) == actor_is_player
            and "asteroide geraakt tijdens beweging" in self._description(action)
        )

    def _is_player_action(self, action: dict[str, Any]) -> bool:
        return str(action.get("actor", "")) not in {"systeem", "AI"}

    def _description(self, action: dict[str, Any]) -> str:
        return str(action.get("description", "")).lower()
