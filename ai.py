from __future__ import annotations

from random import choice, random

from domain.board import Board
from domain.geometry import Coord, line


def all_cells(size: int) -> list[Coord]:
    return [(x, y) for y in range(size) for x in range(size)]


def random_unknown_cell(board: Board) -> Coord:
    options = [cell for cell in all_cells(board.size) if cell not in board.exposed]
    return choice(options or all_cells(board.size))


def random_ai_turn(own: Board, enemy: Board) -> str:
    movable = [ship for ship in own.living_ships() if ship.disabled_turns == 0]
    power_ships = [ship for ship in movable if not ship.power_used]

    if power_ships and random() < 0.25:
        ship = choice(power_ships)
        target = random_unknown_cell(enemy)
        if ship.power == "Radar Scan":
            hits = enemy.scan(target)
            ship.power_used = True
            found = sum(1 for _, has_ship in hits if has_ship)
            return f"AI gebruikt radar scan rond {target}: {found} schipvakje(s) gevonden"
        if ship.power == "Homing Missile":
            target = enemy.nearest_ship_cell(target)
            if target is not None:
                result, target_ship = enemy.receive_attack(target)
                ship.power_used = True
                name = f" op {target_ship.name}" if target_ship else ""
                return f"AI gebruikt homing missile op {target}: {result}{name}"
        if ship.power == "EMP Uitschakeling":
            exposed_ships = [target_ship for target_ship in enemy.living_ships() if any(cell in enemy.exposed for cell in target_ship.cells)]
            if exposed_ships:
                target_ship = choice(exposed_ships)
                target_ship.disabled_turns = 3
                ship.power_used = True
                return f"AI gebruikt EMP op {target_ship.name}"
        if ship.power == "Salvo Aanval":
            results = enemy.attack_many(line(target, choice(((1, 0), (0, 1))), 3))
            ship.power_used = True
            return f"AI gebruikt salvo rond {target}: {', '.join(results)}"
        if ship.power == "Space Smoke":
            own.hide_area(choice(all_cells(own.size)))
            ship.power_used = True
            return "AI gebruikt Space Smoke"

    if movable and random() < 0.25:
        ship = choice(movable)
        axis = ship.orientation
        return own.move_ship(ship, choice((axis, (-axis[0], -axis[1]))))

    target = random_unknown_cell(enemy)
    result, ship = enemy.receive_attack(target)
    name = f" op {ship.name}" if ship else ""
    return f"AI valt {target} aan: {result}{name}"
