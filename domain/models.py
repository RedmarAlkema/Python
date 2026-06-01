from __future__ import annotations

from dataclasses import dataclass, field
from random import choice, randint, shuffle

from config.fleet_blueprints import FLEET_BLUEPRINTS
from domain.geometry import DIAGONALS, Coord, Direction, add_pos, area, in_bounds


@dataclass
class Ship:
    id: int
    name: str
    length: int
    cells: list[Coord]
    power: str
    hits: set[Coord] = field(default_factory=set)
    power_used: bool = False
    disabled_turns: int = 0

    @property
    def sunk(self) -> bool:
        return set(self.cells) <= self.hits

    @property
    def orientation(self) -> Direction:
        if self.length == 1 or self.cells[0][0] == self.cells[-1][0]:
            return (0, 1)
        return (1, 0)


@dataclass
class Asteroid:
    pos: Coord
    direction: Direction


class Board:
    def __init__(self, size: int) -> None:
        self.size = size
        self.ships: list[Ship] = []
        self.asteroids: list[Asteroid] = []
        self.exposed: set[Coord] = set()
        self.scans: set[Coord] = set()
        self.next_ship_id = 1

    def ship_at(self, pos: Coord) -> Ship | None:
        return next((ship for ship in self.ships if pos in ship.cells and not ship.sunk), None)

    def asteroid_at(self, pos: Coord) -> Asteroid | None:
        return next((asteroid for asteroid in self.asteroids if asteroid.pos == pos), None)

    def occupied_cells(self, ignore: Ship | None = None) -> set[Coord]:
        return {cell for ship in self.ships if ship is not ignore and not ship.sunk for cell in ship.cells}

    def can_place(self, cells: list[Coord]) -> bool:
        return all(in_bounds(self.size, cell) for cell in cells) and not self.occupied_cells().intersection(cells)

    def place_ship(self, name: str, length: int, start: Coord, horizontal: bool, power: str) -> bool:
        dx, dy = (1, 0) if horizontal else (0, 1)
        cells = [(start[0] + dx * i, start[1] + dy * i) for i in range(length)]
        if not self.can_place(cells):
            return False
        self.ships.append(Ship(self.next_ship_id, name, length, cells, power))
        self.next_ship_id += 1
        return True

    def randomize_fleet(self) -> None:
        for blueprint in FLEET_BLUEPRINTS:
            for _ in range(blueprint.amount):
                placed = False
                while not placed:
                    placed = self.place_ship(
                        blueprint.name,
                        blueprint.length,
                        (randint(0, self.size - 1), randint(0, self.size - 1)),
                        choice((True, False)),
                        blueprint.power,
                    )

    def place_asteroids(self, amount: int = 4) -> None:
        candidates = [(x, y) for y in range(self.size) for x in range(self.size)]
        shuffle(candidates)
        blocked = self.occupied_cells()
        for pos in candidates:
            if len(self.asteroids) == amount:
                break
            too_close = any(cell in blocked for cell in area(pos, 1))
            if pos not in blocked and not too_close:
                self.asteroids.append(Asteroid(pos, choice(DIAGONALS)))

    def receive_attack(self, pos: Coord) -> tuple[str, Ship | None]:
        if not in_bounds(self.size, pos):
            return "buiten het bord", None
        self.exposed.add(pos)
        asteroid = self.asteroid_at(pos)
        if asteroid:
            asteroid.direction = choice([direction for direction in DIAGONALS if direction != asteroid.direction])
            return "asteroide geraakt", None
        ship = self.ship_at(pos)
        if not ship:
            return "mis", None
        ship.hits.add(pos)
        return ("vernietigd" if ship.sunk else "raak"), ship

    def attack_many(self, cells: list[Coord]) -> list[str]:
        return [self.receive_attack(cell)[0] for cell in cells if in_bounds(self.size, cell)]

    def scan(self, center: Coord) -> list[tuple[Coord, bool]]:
        cells = [cell for cell in area(center, 1) if in_bounds(self.size, cell)]
        self.scans.update(cells)
        return [(cell, self.ship_at(cell) is not None) for cell in cells]

    def hide_area(self, center: Coord) -> None:
        for cell in area(center, 1):
            self.exposed.discard(cell)
            self.scans.discard(cell)

    def move_ship(self, ship: Ship, direction: Direction) -> str:
        if ship.sunk:
            return "schip is vernietigd"
        if ship.disabled_turns > 0:
            return f"{ship.name} is nog {ship.disabled_turns} beurt(en) uitgeschakeld"
        axis = ship.orientation
        if direction not in (axis, (-axis[0], -axis[1])):
            return "schip kan alleen in de lengterichting bewegen"
        new_cells = [add_pos(cell, direction) for cell in ship.cells]
        if not all(in_bounds(self.size, cell) for cell in new_cells):
            return "rand van het bord"
        if self.occupied_cells(ignore=ship).intersection(new_cells):
            return "geblokkeerd door schip"
        moved_hits = {add_pos(hit, direction) for hit in ship.hits}
        asteroid = next((a for a in self.asteroids if a.pos in new_cells), None)
        if asteroid:
            self.asteroids.remove(asteroid)
            ship.cells = new_cells
            ship.hits = moved_hits | {asteroid.pos}
            return "asteroide geraakt tijdens beweging"
        ship.cells = new_cells
        ship.hits = moved_hits
        return "schip verplaatst"

    def move_asteroids(self) -> list[str]:
        messages: list[str] = []
        for asteroid in list(self.asteroids):
            target = add_pos(asteroid.pos, asteroid.direction)
            if not in_bounds(self.size, target):
                asteroid.direction = (-asteroid.direction[0], -asteroid.direction[1])
                target = add_pos(asteroid.pos, asteroid.direction)
            ship = self.ship_at(target)
            if ship:
                ship.hits.add(target)
                self.asteroids.remove(asteroid)
                messages.append(f"Asteroide botst op {ship.name}")
            elif not self.asteroid_at(target):
                asteroid.pos = target
        return messages

    def tick_disables(self) -> None:
        for ship in self.ships:
            if ship.disabled_turns > 0:
                ship.disabled_turns -= 1

    def living_ships(self) -> list[Ship]:
        return [ship for ship in self.ships if not ship.sunk]

    def nearest_ship_cell(self, pos: Coord) -> Coord | None:
        cells = [cell for ship in self.living_ships() for cell in ship.cells if cell not in ship.hits]
        if not cells:
            return None
        return min(cells, key=lambda cell: abs(cell[0] - pos[0]) + abs(cell[1] - pos[1]))

    def fleet_destroyed(self) -> bool:
        return not self.living_ships()
