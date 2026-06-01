from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FleetBlueprint:
    name: str
    length: int
    amount: int
    power: str


FLEET_BLUEPRINTS: tuple[FleetBlueprint, ...] = (
    FleetBlueprint("Verkenner", 2, 2, "Radar Scan"),
    FleetBlueprint("Jager", 3, 2, "Homing Missile"),
    FleetBlueprint("Kruiser", 3, 2, "EMP Uitschakeling"),
    FleetBlueprint("Slagschip", 4, 1, "Salvo Aanval"),
    FleetBlueprint("Commandoschip", 5, 1, "Space Smoke"),
)
