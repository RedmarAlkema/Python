from __future__ import annotations

import pygame

from config.settings import GameSettings
from domain.geometry import Coord

FULLSCREEN = False
WINDOW_SIZE = GameSettings.START_WINDOW


def set_display(size: tuple[int, int] | None = None) -> pygame.Surface:
    global WINDOW_SIZE
    if size is not None:
        WINDOW_SIZE = size
    flags = pygame.FULLSCREEN if FULLSCREEN else 0
    display_size = (0, 0) if FULLSCREEN else WINDOW_SIZE
    return pygame.display.set_mode(display_size, flags)


def toggle_fullscreen(size: tuple[int, int] | None = None) -> pygame.Surface:
    global FULLSCREEN
    FULLSCREEN = not FULLSCREEN
    return set_display(size)


def fullscreen_label() -> str:
    return "Venster" if FULLSCREEN else "Fullscreen"


def fullscreen_button(surface: pygame.Surface) -> pygame.Rect:
    return pygame.Rect(surface.get_width() - 190, 28, 150, 42)


def main_menu_button(surface: pygame.Surface) -> pygame.Rect:
    return pygame.Rect(surface.get_width() - 370, 28, 150, 42)


def game_window_size(size: int) -> tuple[int, int]:
    board_width = GameSettings.CELL * size * 2
    width = max(GameSettings.MIN_WINDOW[0], GameSettings.LEFT * 2 + board_width + GameSettings.GAP + GameSettings.PANEL)
    height = max(GameSettings.MIN_WINDOW[1], GameSettings.TOP + GameSettings.CELL * size + 110)
    return width, height


def board_rect(size: int, enemy: bool) -> pygame.Rect:
    x = GameSettings.LEFT + (GameSettings.CELL * size + GameSettings.GAP) * int(enemy)
    return pygame.Rect(x, GameSettings.TOP, GameSettings.CELL * size, GameSettings.CELL * size)


def cell_from_mouse(pos: Coord, size: int) -> tuple[bool, Coord] | None:
    for is_enemy in (False, True):
        rect = board_rect(size, is_enemy)
        if rect.collidepoint(pos):
            return is_enemy, ((pos[0] - rect.x) // GameSettings.CELL, (pos[1] - rect.y) // GameSettings.CELL)
    return None
