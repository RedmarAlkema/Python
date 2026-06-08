from domain.ships.base import Ship
from domain.ships.commandoschip import Commandoschip
from domain.ships.jager import Jager
from domain.ships.kruiser import Kruiser
from domain.ships.slagschip import Slagschip
from domain.ships.verkenner import Verkenner

SHIP_TYPES: dict[str, type[Ship]] = {
    "Verkenner": Verkenner,
    "Jager": Jager,
    "Kruiser": Kruiser,
    "Slagschip": Slagschip,
    "Commandoschip": Commandoschip,
}

__all__ = [
    "Ship",
    "Verkenner",
    "Jager",
    "Kruiser",
    "Slagschip",
    "Commandoschip",
    "SHIP_TYPES",
]