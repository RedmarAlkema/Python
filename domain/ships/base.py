from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import ClassVar

from domain.geometry import Coord, Direction


@dataclass(slots=True)
class Ship(ABC):
    id: int
    cells: list[Coord]
    hits: set[Coord] = field(default_factory=set)
    power_used: bool = False
    disabled_turns: int = 0

    ship_name: ClassVar[str] = ""
    ship_length: ClassVar[int] = 0
    ship_power: ClassVar[str] = ""

    def __post_init__(self) -> None:
        if type(self) is Ship:
            raise TypeError("Ship is abstract")
        if not self.ship_name or not self.ship_length or not self.ship_power:
            raise TypeError("Ship subclasses must define name, length and power")

    def __len__(self) -> int:
        return self.length

    def __contains__(self, pos: Coord) -> bool:
        return pos in self.cells

    @property
    def name(self) -> str:
        return self.ship_name

    @property
    def length(self) -> int:
        return self.ship_length

    @property
    def power(self) -> str:
        return self.ship_power

    @property
    def sunk(self) -> bool:
        return set(self.cells) <= self.hits

    @property
    def orientation(self) -> Direction:
        if self.length == 1 or self.cells[0][0] == self.cells[-1][0]:
            return (0, 1)
        return (1, 0)

    def to_dict(self) -> dict:
        return {
            "type": self.name,
            "id": self.id,
            "cells": [list(cell) for cell in self.cells],
            "hits": [list(cell) for cell in self.hits],
            "power_used": self.power_used,
            "disabled_turns": self.disabled_turns,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Ship":
        from domain.ships import SHIP_TYPES

        ship_cls = SHIP_TYPES[data.get("type") or data.get("name")]
        ship = ship_cls(data["id"], [tuple(cell) for cell in data["cells"]])
        ship.hits = {tuple(cell) for cell in data.get("hits", [])}
        ship.power_used = data.get("power_used", False)
        ship.disabled_turns = data.get("disabled_turns", 0)
        return ship
