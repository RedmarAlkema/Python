from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from domain.board import GameBoard
from domain.geometry import Coord, Direction, in_bounds, line

if TYPE_CHECKING:
    from domain.player import Player
    from domain.ships import Ship


@dataclass(slots=True)
class Move:
    kind: str
    target: Coord | None = None
    direction: Direction | None = None
    own_board: bool = False

    def to_log_entry(self, actor: str, description: str) -> dict[str, str]:
        return {
            "time": datetime.now().isoformat(timespec="seconds"),
            "actor": actor,
            "kind": self.kind,
            "target": str(self.target) if self.target is not None else "",
            "direction": str(self.direction) if self.direction is not None else "",
            "description": description,
        }

    def validate(self, board: GameBoard, ship: Ship | None = None) -> tuple[bool, str]:
        if self.kind == "attack":
            if self.target is None:
                return False, "Geen aanvalsdoel geselecteerd"
            if not in_bounds(board.size, self.target):
                return False, "Aanval buiten het bord"
            return True, "Aanval is geldig"
        if self.kind == "move":
            if ship is None:
                return False, "Selecteer eerst een eigen schip."
            if self.direction is None:
                return False, "Geen richting opgegeven"
            return board.can_move_ship(ship, self.direction)
        if self.kind == "power":
            if ship is None:
                return False, "Selecteer eerst een eigen schip."
            if ship.power_used:
                return False, f"{ship.name} heeft de speciale kracht al gebruikt."
            if ship.disabled_turns > 0:
                return False, f"{ship.name} is uitgeschakeld."
            if self.target is None:
                return False, "Geen doel geselecteerd"
            if ship.power == "Radar Scan" and self.own_board:
                return False, "Deze kracht werkt niet op dat bord."
            if ship.power in {"Homing Missile", "EMP Uitschakeling", "Salvo Aanval"} and self.own_board:
                return False, "Deze kracht werkt niet op dat bord."
            if ship.power == "Space Smoke" and not self.own_board:
                return False, "Deze kracht werkt niet op dat bord."
            return True, "Kracht is geldig"
        return False, "Onbekende actie"

    def apply(self, player: Player, enemy: Player, salvo_axis: Direction) -> str:
        ship = player.selected_ship

        if self.kind == "attack":
            result, target_ship = enemy.receive_attack(self.target or (0, 0))
            suffix = f" op {target_ship.name}" if target_ship else ""
            return f"Aanval {self.target}: {result}{suffix}."

        if self.kind == "move":
            if not ship or self.direction is None:
                return "Selecteer eerst een eigen schip."
            return player.move_ship(ship, self.direction)

        if self.kind != "power" or not ship:
            return "Onbekende actie"

        if ship.power == "Radar Scan":
            hits = enemy.board.scan(self.target or (0, 0))
            found = sum(1 for _, has_ship in hits if has_ship)
            ship.power_used = True
            return f"Radar scan rond {self.target}: {found} schipvakje(s) gevonden."
        if ship.power == "Homing Missile":
            target = enemy.board.nearest_ship_cell(self.target or (0, 0))
            if target is None:
                return "Geen doelwit gevonden."
            result, target_ship = enemy.board.receive_attack(target)
            ship.power_used = True
            return f"Homing missile raakt {target}: {result} op {target_ship.name}."
        if ship.power == "EMP Uitschakeling":
            target_ship = enemy.board.ship_at(self.target or (0, 0))
            if not target_ship or (self.target or (0, 0)) not in enemy.board.exposed:
                return "EMP kan alleen op een zichtbaar vijandelijk schip."
            target_ship.disabled_turns = 3
            ship.power_used = True
            return f"EMP schakelt {target_ship.name} drie beurten uit."
        if ship.power == "Salvo Aanval":
            results = enemy.board.attack_many(line(self.target or (0, 0), salvo_axis, 3))
            ship.power_used = True
            return f"Salvo uitgevoerd: {', '.join(results)}."
        if ship.power == "Space Smoke":
            player.board.hide_area(self.target or (0, 0))
            ship.power_used = True
            return f"Space Smoke verbergt 3x3 gebied rond {self.target}."
        return "Deze kracht werkt niet op dat bord."
