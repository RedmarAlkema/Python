from __future__ import annotations

from ai import random_ai_turn
from domain.geometry import Coord, line
from domain.models import Board, Ship


class Game:
    def __init__(self, size: int) -> None:
        self.size = size
        self.player = Board(size)
        self.enemy = Board(size)
        for board in (self.player, self.enemy):
            board.randomize_fleet()
            board.place_asteroids()
        self.mode = "attack"
        self.salvo_axis = (1, 0)
        self.selected_ship: Ship | None = None
        self.message = "Klik op het vijandelijke bord om aan te vallen."
        self.game_over = False

    def end_player_turn(self) -> None:
        if self.enemy.fleet_destroyed():
            self.message = "Gewonnen: de vijandelijke vloot is vernietigd."
            self.game_over = True
            return
        messages = self.player.move_asteroids() + self.enemy.move_asteroids()
        ai_message = random_ai_turn(self.enemy, self.player)
        self.player.tick_disables()
        self.enemy.tick_disables()
        if self.player.fleet_destroyed():
            self.message = "Verloren: jouw vloot is vernietigd."
            self.game_over = True
        else:
            extra = f" {' '.join(messages)}" if messages else ""
            self.message = f"{ai_message}.{extra}"

    def select_ship(self, pos: Coord, own_board: bool) -> None:
        board = self.player if own_board else self.enemy
        ship = board.ship_at(pos)
        if not ship:
            self.message = "Geen schip geselecteerd."
            return
        self.selected_ship = ship
        self.message = f"{ship.name} geselecteerd ({ship.power})."

    def use_attack(self, pos: Coord) -> None:
        result, ship = self.enemy.receive_attack(pos)
        name = f" op {ship.name}" if ship else ""
        self.message = f"Aanval {pos}: {result}{name}."
        self.end_player_turn()

    def use_power(self, pos: Coord, own_board: bool) -> None:
        ship = self.selected_ship
        if not ship:
            self.message = "Selecteer eerst een eigen schip met linkermuisknop."
            return
        if ship.power_used:
            self.message = f"{ship.name} heeft de speciale kracht al gebruikt."
            return
        if ship.disabled_turns > 0:
            self.message = f"{ship.name} is uitgeschakeld."
            return

        power = ship.power
        if power == "Radar Scan" and not own_board:
            hits = self.enemy.scan(pos)
            found = sum(1 for _, has_ship in hits if has_ship)
            self.message = f"Radar scan rond {pos}: {found} schipvakje(s) gevonden."
        elif power == "Homing Missile" and not own_board:
            target = self.enemy.nearest_ship_cell(pos)
            if target is None:
                self.message = "Geen doelwit gevonden."
                return
            result, target_ship = self.enemy.receive_attack(target)
            self.message = f"Homing missile raakt {target}: {result} op {target_ship.name}."
        elif power == "EMP Uitschakeling" and not own_board:
            target_ship = self.enemy.ship_at(pos)
            if not target_ship or pos not in self.enemy.exposed:
                self.message = "EMP kan alleen op een zichtbaar vijandelijk schip."
                return
            target_ship.disabled_turns = 3
            self.message = f"EMP schakelt {target_ship.name} drie beurten uit."
        elif power == "Salvo Aanval" and not own_board:
            results = self.enemy.attack_many(line(pos, self.salvo_axis, 3))
            self.message = f"Salvo uitgevoerd: {', '.join(results)}."
        elif power == "Space Smoke" and own_board:
            self.player.hide_area(pos)
            self.message = f"Space Smoke verbergt 3x3 gebied rond {pos}."
        else:
            self.message = "Deze kracht werkt niet op dat bord."
            return
        ship.power_used = True
        self.end_player_turn()

    def move_selected(self, direction: Coord) -> None:
        if not self.selected_ship:
            self.message = "Selecteer eerst een eigen schip."
            return
        self.message = self.player.move_ship(self.selected_ship, direction)
        self.end_player_turn()