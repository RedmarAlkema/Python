from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from domain.board import Board
from domain.decorators import audit_action
from domain.geometry import Coord
from domain.move import Move
from domain.player import AIPlayer, Player
from domain.ships import Ship
from storage import save_game_data


class Game:
    def __init__(self, size: int, nickname: str = "Speler", randomize_player: bool = True) -> None:
        self.id = uuid4().hex
        self.nickname = nickname.strip() or "Speler"
        self.started_at = datetime.now().isoformat(timespec="seconds")
        self.size = size
        self.player = Player(Board(size), "Speler")
        self.enemy = AIPlayer(Board(size), "AI")
        if randomize_player:
            self.player.randomize_fleet()
            self.player.place_asteroids()
        self.enemy.randomize_fleet()
        self.enemy.place_asteroids()
        self.mode = "attack"
        self.salvo_axis = (1, 0)
        self.message = "Klik op het vijandelijke bord om aan te vallen." if randomize_player else "Plaats eerst je vloot."
        self.game_over = False
        self.winner: str | None = None
        self.cheat_enabled = False
        self.actions: list[dict[str, str]] = []
        self.audit_log: list[dict[str, str]] = []
        self.updated_at = self.started_at
        self.record_action("systeem", f"Nieuw spel gestart op {size}x{size}.", autosave=False)
        if randomize_player:
            self.save()

    def finish_player_setup(self) -> None:
        self.player.place_asteroids()
        self.message = "Vloot geplaatst. Klik op het vijandelijke bord om aan te vallen."
        self.record_action("systeem", "Speler heeft de vloot handmatig geplaatst.", autosave=False)
        self.save()

    def record_action(self, actor: str, description: str, autosave: bool = True) -> None:
        self.actions.append(
            {
                "time": datetime.now().isoformat(timespec="seconds"),
                "actor": actor,
                "description": description,
            }
        )
        if autosave:
            self.save()

    def record_move(self, actor: str, move: Move, description: str, autosave: bool = True) -> None:
        self.actions.append(move.to_log_entry(actor, description))
        if autosave:
            self.save()

    def statistics(self) -> dict[str, int | str | None]:
        player_ships = self.player.board.ships
        enemy_ships = self.enemy.board.ships
        return {
            "nickname": self.nickname,
            "started_at": self.started_at,
            "updated_at": self.updated_at,
            "size": self.size,
            "winner": self.winner,
            "turns": sum(1 for action in self.actions if action.get("actor") not in {"systeem"}),
            "player_hits": sum(len(ship.hits) for ship in player_ships),
            "enemy_hits": sum(len(ship.hits) for ship in enemy_ships),
            "player_lost": sum(1 for ship in player_ships if ship.sunk),
            "enemy_lost": sum(1 for ship in enemy_ships if ship.sunk),
        }

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nickname": self.nickname,
            "started_at": self.started_at,
            "updated_at": self.updated_at,
            "size": self.size,
            "player": self.player.to_dict(),
            "enemy": self.enemy.to_dict(),
            "mode": self.mode,
            "salvo_axis": self.salvo_axis,
            "selected_ship_id": self.selected_ship.id if self.selected_ship else None,
            "message": self.message,
            "game_over": self.game_over,
            "winner": self.winner,
            "cheat_enabled": self.cheat_enabled,
            "actions": self.actions,
            "statistics": self.statistics(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Game":
        game = cls.__new__(cls)
        game.id = data["id"]
        game.nickname = data.get("nickname", "Speler")
        game.started_at = data.get("started_at", datetime.now().isoformat(timespec="seconds"))
        game.updated_at = data.get("updated_at", game.started_at)
        game.size = data["size"]
        game.player = Player.from_dict(data["player"])
        game.enemy = AIPlayer.from_dict(data["enemy"])
        game.mode = data.get("mode", "attack")
        game.salvo_axis = tuple(data.get("salvo_axis", (1, 0)))
        selected_id = data.get("selected_ship_id")
        game.selected_ship = next((ship for ship in game.player.board.ships if ship.id == selected_id), None)
        game.player.selected_ship = game.selected_ship
        game.message = data.get("message", "Spel geladen.")
        game.game_over = data.get("game_over", False)
        game.winner = data.get("winner")
        game.cheat_enabled = data.get("cheat_enabled", False)
        game.actions = data.get("actions", [])
        game.audit_log = []
        return game

    def save(self) -> None:
        self.updated_at = datetime.now().isoformat(timespec="seconds")
        save_game_data(self.to_dict())

    @property
    def selected_ship(self) -> Ship | None:
        return self.player.selected_ship

    @selected_ship.setter
    def selected_ship(self, ship: Ship | None) -> None:
        self.player.selected_ship = ship

    @audit_action()
    def end_player_turn(self) -> None:
        if self.enemy.fleet_destroyed():
            self.message = "Gewonnen: de vijandelijke vloot is vernietigd."
            self.game_over = True
            self.winner = self.nickname
            self.record_action("systeem", self.message, autosave=False)
            return

        ai_message = self.enemy.take_turn(self.player)
        asteroid_messages = self.player.move_asteroids() + self.enemy.move_asteroids()
        self.record_action("AI", ai_message, autosave=False)
        for message in asteroid_messages:
            self.record_action("systeem", message, autosave=False)
        self.player.tick_disables()
        self.enemy.tick_disables()
        if self.player.fleet_destroyed():
            self.message = "Verloren: jouw vloot is vernietigd."
            self.game_over = True
            self.winner = "AI"
            self.record_action("systeem", self.message, autosave=False)
        else:
            extra = f" {' '.join(asteroid_messages)}" if asteroid_messages else ""
            self.message = f"{ai_message}.{extra}"

    @audit_action()
    def select_ship(self, pos: Coord, own_board: bool) -> None:
        board = self.player if own_board else self.enemy
        ship = board.select_ship(pos)
        if not ship:
            self.message = "Geen schip geselecteerd."
            return
        self.selected_ship = ship
        self.message = f"{ship.name} geselecteerd. Power: {ship.power}. Klik op een bordvak om de power te gebruiken of gebruik pijltjes om te bewegen."

    @audit_action()
    def deselect_ship(self) -> None:
        self.selected_ship = None
        self.message = "Selectie gewist. Klik op een eigen schip om te selecteren."

    @audit_action()
    def use_attack(self, pos: Coord) -> None:
        move = Move("attack", target=pos)
        self.message = move.apply(self.player, self.enemy, self.salvo_axis)
        self.record_move(self.nickname, move, self.message, autosave=False)
        self.end_player_turn()
        self.save()

    @audit_action()
    def use_power(self, pos: Coord, own_board: bool) -> None:
        ship = self.selected_ship
        if not ship:
            self.message = "Selecteer eerst een eigen schip met linkermuisknop."
            return
        move = Move("power", target=pos, own_board=own_board)
        valid, message = move.validate(self.player.board, ship)
        if not valid:
            self.message = message
            return
        self.message = move.apply(self.player, self.enemy, self.salvo_axis)
        self.record_move(self.nickname, move, self.message, autosave=False)
        self.end_player_turn()
        self.save()

    @audit_action()
    def move_selected(self, direction: Coord) -> None:
        if not self.selected_ship:
            self.message = "Selecteer eerst een eigen schip."
            return
        move = Move("move", direction=direction)
        valid, message = move.validate(self.player.board, self.selected_ship)
        if not valid:
            self.message = message
            return
        self.message = move.apply(self.player, self.enemy, self.salvo_axis)
        self.record_move(self.nickname, move, f"{self.selected_ship.name} beweegt {direction}: {self.message}", autosave=False)
        self.end_player_turn()
        self.save()
