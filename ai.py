from __future__ import annotations

from random import choice, random

from models import Board, Coord


def all_cells(size: int) -> list[Coord]:
    return [(x, y) for y in range(size) for x in range(size)]


def random_unknown_cell(board: Board) -> Coord:
    options = [cell for cell in all_cells(board.size) if cell not in board.exposed]
    return choice(options or all_cells(board.size))


def random_ai_turn(own: Board, enemy: Board) -> str:
    movable = [ship for ship in own.living_ships() if ship.disabled_turns == 0]
    if movable and random() < 0.25:
        ship = choice(movable)
        axis = ship.orientation
        return own.move_ship(ship, choice((axis, (-axis[0], -axis[1]))))

    target = random_unknown_cell(enemy)
    result, ship = enemy.receive_attack(target)
    name = f" op {ship.name}" if ship else ""
    return f"AI valt {target} aan: {result}{name}"
