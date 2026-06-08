from __future__ import annotations

from dataclasses import dataclass

from domain.geometry import Coord, Direction


@dataclass(slots=True, unsafe_hash=True)
class Asteroid:
    pos: Coord
    direction: Direction

    def to_dict(self) -> dict:
        return {"pos": list(self.pos), "direction": list(self.direction)}

    @classmethod
    def from_dict(cls, data: dict) -> "Asteroid":
        return cls(pos=tuple(data["pos"]), direction=tuple(data["direction"]))


Astroid = Asteroid
