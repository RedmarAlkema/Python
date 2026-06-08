from __future__ import annotations

import sys

import pygame

from config.settings import GameSettings
from game import Game
from presentation.drawing import draw_game_screen
from presentation.layout import cell_from_mouse, game_window_size, main_menu_button, set_display, toggle_fullscreen
from presentation.screens import start_screen


def handle_key(game: Game, key: int) -> None:
    if key == pygame.K_ESCAPE:
        game.deselect_ship()
    elif key == pygame.K_c:
        game.cheat_enabled = not game.cheat_enabled
        game.message = f"Cheatcode {'aan' if game.cheat_enabled else 'uit'}."
        game.record_action("systeem", game.message)
    elif key == pygame.K_r:
        game.__init__(game.size, game.nickname)
    elif game.selected_ship and not game.game_over:
        _move_selected_ship(game, key)


def play_game(screen: pygame.Surface, clock: pygame.time.Clock, game: Game) -> pygame.Surface:
    screen = set_display(game_window_size(game.size))
    font = pygame.font.SysFont("arial", 24)
    small = pygame.font.SysFont("arial", 18)

    while True:
        for event in pygame.event.get():
            if _quit_requested(event):
                pygame.quit()
                sys.exit()
            if _return_to_menu_requested(screen, event):
                return screen
            screen = _handle_game_event(screen, game, event)

        draw_game_screen(screen, game, font, small)
        pygame.display.flip()
        clock.tick(60)


def run() -> None:
    pygame.init()
    pygame.display.set_caption("Cosmic Confrontation")
    screen = set_display(GameSettings.START_WINDOW)
    clock = pygame.time.Clock()

    while True:
        screen = set_display(GameSettings.START_WINDOW)
        game = start_screen(screen, clock)
        screen = play_game(screen, clock, game)


def _handle_game_event(screen: pygame.Surface, game: Game, event: pygame.event.Event) -> pygame.Surface:
    if event.type == pygame.KEYDOWN:
        if event.key in (pygame.K_f, pygame.K_F11):
            screen = toggle_fullscreen(game_window_size(game.size))
        else:
            handle_key(game, event.key)
    if event.type == pygame.MOUSEBUTTONDOWN and not game.game_over:
        _handle_board_click(game, event)
    return screen


def _handle_board_click(game: Game, event: pygame.event.Event) -> None:
    hit = cell_from_mouse(event.pos, game.size)
    if event.button != 1 or not hit:
        return
    is_enemy, cell = hit
    if not is_enemy:
        game.select_ship(cell, own_board=True)
    elif game.selected_ship:
        game.use_power(cell, own_board=False)
    else:
        game.use_attack(cell)


def _move_selected_ship(game: Game, key: int) -> None:
    directions = {
        pygame.K_LEFT: (-1, 0),
        pygame.K_RIGHT: (1, 0),
        pygame.K_UP: (0, -1),
        pygame.K_DOWN: (0, 1),
    }
    if key in directions:
        game.move_selected(directions[key])


def _return_to_menu_requested(screen: pygame.Surface, event: pygame.event.Event) -> bool:
    return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and main_menu_button(screen).collidepoint(event.pos)


def _quit_requested(event: pygame.event.Event) -> bool:
    return event.type == pygame.QUIT
