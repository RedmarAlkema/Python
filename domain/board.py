from __future__ import annotations

from random import choice, randint, shuffle

from config.fleet_blueprints import FLEET_BLUEPRINTS
from domain.asteroid import Asteroid
from domain.decorators import audit_action
from domain.geometry import DIAGONALS, Coord, Direction, add_pos, area, in_bounds
from domain.ships import SHIP_TYPES, Ship


class GameBoard:
    def __init__(self, size: int) -> None:
        self.size = size
        self.ships: list[Ship] = []
        self.asteroids: list[Asteroid] = []
        self.exposed: set[Coord] = set()
        self.scans: set[Coord] = set()
        self.next_ship_id = 1
        self.audit_log: list[dict[str, str]] = []

    def ship_at(self, pos: Coord) -> Ship | None:
        return next((ship for ship in self.ships if pos in ship.cells and not ship.sunk), None)

    def asteroid_at(self, pos: Coord) -> Asteroid | None:
        return next((asteroid for asteroid in self.asteroids if asteroid.pos == pos), None)

    def occupied_cells(self, ignore: Ship | None = None) -> set[Coord]:
        return {cell for ship in self.ships if ship is not ignore and not ship.sunk for cell in ship.cells}

    def can_place(self, cells: list[Coord]) -> bool:
        return all(in_bounds(self.size, cell) for cell in cells) and not self.occupied_cells().intersection(cells)

    def can_move_ship(self, ship: Ship, direction: Direction) -> tuple[bool, str]:
        if ship.sunk:
            return False, "schip is vernietigd"
        if ship.disabled_turns > 0:
            return False, f"{ship.name} is nog {ship.disabled_turns} beurt(en) uitgeschakeld"
        axis = ship.orientation
        if direction not in (axis, (-axis[0], -axis[1])):
            return False, "schip kan alleen in de lengterichting bewegen"
        new_cells = [add_pos(cell, direction) for cell in ship.cells]
        if not all(in_bounds(self.size, cell) for cell in new_cells):
            return False, "rand van het bord"
        if self.occupied_cells(ignore=ship).intersection(new_cells):
            return False, "geblokkeerd door schip"
        return True, "schip verplaatst"

    @audit_action()
    def place_ship(self, ship_cls: type[Ship], start: Coord, horizontal: bool) -> bool:
        dx, dy = (1, 0) if horizontal else (0, 1)
        cells = [(start[0] + dx * i, start[1] + dy * i) for i in range(ship_cls.ship_length)]
        if not self.can_place(cells):
            return False
        self.ships.append(ship_cls(self.next_ship_id, cells))
        self.next_ship_id += 1
        return True

    def randomize_fleet(self) -> None:
        for blueprint in FLEET_BLUEPRINTS:
            ship_cls = SHIP_TYPES[blueprint.name]
            for _ in range(blueprint.amount):
                placed = False
                while not placed:
                    placed = self.place_ship(ship_cls, (randint(0, self.size - 1), randint(0, self.size - 1)), choice((True, False)))

    def place_asteroids(self, amount: int = 4) -> None:
        candidates = [(x, y) for y in range(self.size) for x in range(self.size)]
        shuffle(candidates)
        blocked = self._asteroid_spawn_blocked_cells()
        for pos in candidates:
            if len(self.asteroids) == amount:
                break
            if pos not in blocked:
                self.asteroids.append(Asteroid(pos, choice(DIAGONALS)))
                blocked.add(pos)

    def add_random_asteroids(self, amount: int) -> None:
        candidates = [(x, y) for y in range(self.size) for x in range(self.size)]
        shuffle(candidates)
        blocked = self._asteroid_spawn_blocked_cells()
        for pos in candidates:
            if amount == 0:
                break
            if pos not in blocked:
                self.asteroids.append(Asteroid(pos, choice(DIAGONALS)))
                blocked.add(pos)
                amount -= 1

    @audit_action()
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

    @audit_action()
    def move_ship(self, ship: Ship, direction: Direction) -> str:
        valid, message = self.can_move_ship(ship, direction)
        if not valid:
            return message
        new_cells = [add_pos(cell, direction) for cell in ship.cells]
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

    @audit_action()
    def move_asteroids(self) -> list[str]:
        messages: list[str] = []
        targets = {asteroid: self._asteroid_target_after_bounce(asteroid) for asteroid in self.asteroids}
        collision_events = self._asteroid_collision_events(targets)
        collided = {asteroid for event in collision_events for asteroid in event}

        if collided:
            self.asteroids = [asteroid for asteroid in self.asteroids if asteroid not in collided]
            self.add_random_asteroids(4 * len(collision_events))
            messages.append("Asteroiden botsen: beide verdwijnen en er verschijnen nieuwe asteroiden")

        for asteroid in list(self.asteroids):
            target = targets.get(asteroid)
            if target is None:
                continue
            ship = self.ship_at(target)
            if ship:
                ship.hits.add(target)
                self.asteroids.remove(asteroid)
                messages.append(f"Asteroide botst op {ship.name}: schade op {target} en de asteroide verdwijnt")
            elif not self.asteroid_at(target):
                asteroid.pos = target
        return messages

    def _asteroid_spawn_blocked_cells(self) -> set[Coord]:
        blocked = {asteroid.pos for asteroid in self.asteroids}
        for ship_cell in self.occupied_cells():
            blocked.update(cell for cell in area(ship_cell, 1) if in_bounds(self.size, cell))
        return blocked

    def _asteroid_target_after_bounce(self, asteroid: Asteroid) -> Coord:
        next_x = asteroid.pos[0] + asteroid.direction[0]
        next_y = asteroid.pos[1] + asteroid.direction[1]
        dx, dy = asteroid.direction
        if not 0 <= next_x < self.size:
            dx *= -1
        if not 0 <= next_y < self.size:
            dy *= -1
        asteroid.direction = (dx, dy)
        return add_pos(asteroid.pos, asteroid.direction)

    def _asteroid_collision_events(self, targets: dict[Asteroid, Coord]) -> set[frozenset[Asteroid]]:
        collision_events = self._same_target_collisions(targets)
        collision_events.update(self._swap_collisions(targets))
        return collision_events

    def _same_target_collisions(self, targets: dict[Asteroid, Coord]) -> set[frozenset[Asteroid]]:
        events: set[frozenset[Asteroid]] = set()
        for target in set(targets.values()):
            asteroids = {asteroid for asteroid, asteroid_target in targets.items() if asteroid_target == target}
            if len(asteroids) > 1:
                events.add(frozenset(asteroids))
        return events

    def _swap_collisions(self, targets: dict[Asteroid, Coord]) -> set[frozenset[Asteroid]]:
        events: set[frozenset[Asteroid]] = set()
        for asteroid, target in targets.items():
            other = self.asteroid_at(target)
            if other and other is not asteroid and targets.get(other) == asteroid.pos:
                events.add(frozenset({asteroid, other}))
        return events

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

    def to_dict(self) -> dict:
        return {
            "size": self.size,
            "ships": [ship.to_dict() for ship in self.ships],
            "asteroids": [asteroid.to_dict() for asteroid in self.asteroids],
            "exposed": [list(cell) for cell in self.exposed],
            "scans": [list(cell) for cell in self.scans],
            "next_ship_id": self.next_ship_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GameBoard":
        board = cls(data["size"])
        board.ships = [Ship.from_dict(ship) for ship in data.get("ships", [])]
        board.asteroids = [Asteroid.from_dict(asteroid) for asteroid in data.get("asteroids", [])]
        board.exposed = {tuple(cell) for cell in data.get("exposed", [])}
        board.scans = {tuple(cell) for cell in data.get("scans", [])}
        board.next_ship_id = data.get("next_ship_id", len(board.ships) + 1)
        return board


Board = GameBoard
