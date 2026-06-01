from __future__ import annotations

Coord = tuple[int, int]
Direction = tuple[int, int]

DIAGONALS: tuple[Direction, ...] = ((-1, -1), (1, -1), (-1, 1), (1, 1))


def in_bounds(size: int, pos: Coord) -> bool:
    x, y = pos
    return 0 <= x < size and 0 <= y < size


def add_pos(a: Coord, b: Direction) -> Coord:
    return a[0] + b[0], a[1] + b[1]


def area(center: Coord, radius: int = 1) -> list[Coord]:
    cx, cy = center
    return [(x, y) for y in range(cy - radius, cy + radius + 1) for x in range(cx - radius, cx + radius + 1)]


def line(center: Coord, direction: Direction, length: int = 3) -> list[Coord]:
    half = length // 2
    return [(center[0] + direction[0] * step, center[1] + direction[1] * step) for step in range(-half, half + 1)]
