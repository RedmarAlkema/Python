from __future__ import annotations

from dataclasses import dataclass
from random import choice, random

from domain.board import GameBoard
from domain.geometry import Coord
from domain.ships import Ship


@dataclass(slots=True)
class Player:
    board: GameBoard
    name: str = "Speler"
    selected_ship: Ship | None = None

    def __getattr__(self, attribute: str):
        return getattr(self.board, attribute)

    def select_ship(self, pos: Coord) -> Ship | None:
        ship = self.board.ship_at(pos)
        self.selected_ship = ship
        return ship

    def clear_selection(self) -> None:
        self.selected_ship = None

    def receive_attack(self, pos: Coord) -> tuple[str, Ship | None]:
        return self.board.receive_attack(pos)

    def move_ship(self, ship: Ship, direction: Coord) -> str:
        return self.board.move_ship(ship, direction)

    def move_asteroids(self) -> list[str]:
        return self.board.move_asteroids()

    def tick_disables(self) -> None:
        self.board.tick_disables()

    def fleet_destroyed(self) -> bool:
        return self.board.fleet_destroyed()

    def living_ships(self) -> list[Ship]:
        return self.board.living_ships()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "board": self.board.to_dict(),
            "selected_ship_id": self.selected_ship.id if self.selected_ship else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        player = cls(GameBoard.from_dict(data["board"]), data.get("name", "Speler"))
        selected_id = data.get("selected_ship_id")
        player.selected_ship = next((ship for ship in player.board.ships if ship.id == selected_id), None)
        return player


@dataclass(slots=True)
class AIPlayer(Player):
    def take_turn(self, enemy: Player) -> str:
        from ai import random_ai_turn

        return random_ai_turn(self.board, enemy.board)