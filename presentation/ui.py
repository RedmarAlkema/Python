from __future__ import annotations

import sys

import pygame

from config.colors import Colors
from config.settings import GameSettings
from domain.geometry import Coord
from domain.models import Board, Ship
from game import Game


def board_rect(size: int, enemy: bool) -> pygame.Rect:
    x = GameSettings.LEFT + (GameSettings.CELL * size + GameSettings.GAP) * int(enemy)
    return pygame.Rect(x, GameSettings.TOP, GameSettings.CELL * size, GameSettings.CELL * size)


def cell_from_mouse(pos: Coord, size: int) -> tuple[bool, Coord] | None:
    for is_enemy in (False, True):
        rect = board_rect(size, is_enemy)
        if rect.collidepoint(pos):
            return is_enemy, ((pos[0] - rect.x) // GameSettings.CELL, (pos[1] - rect.y) // GameSettings.CELL)
    return None


def draw_text(surface: pygame.Surface, font: pygame.font.Font, text: str, pos: Coord, color=Colors.TEXT) -> None:
    surface.blit(font.render(text, True, color), pos)


def draw_marker(surface: pygame.Surface, pos: Coord, color: tuple[int, int, int], label: str, font: pygame.font.Font) -> None:
    pygame.draw.circle(surface, color, (pos[0] + 7, pos[1] + 9), 7)
    draw_text(surface, font, label, (pos[0] + 20, pos[1]), Colors.MUTED)


def draw_board(surface: pygame.Surface, board: Board, rect: pygame.Rect, reveal: bool, selected: Ship | None) -> None:
    pygame.draw.rect(surface, Colors.PANEL_BG, rect.inflate(10, 10))
    for y in range(board.size):
        for x in range(board.size):
            pos = (x, y)
            cell = pygame.Rect(rect.x + x * GameSettings.CELL, rect.y + y * GameSettings.CELL, GameSettings.CELL - 2, GameSettings.CELL - 2)
            color = Colors.UNKNOWN
            ship = board.ship_at(pos)
            if pos in board.exposed:
                color = Colors.EXPOSED
            if pos in board.scans:
                color = Colors.SCAN
            if reveal and ship:
                color = Colors.SHIP
            if selected and pos in selected.cells:
                color = Colors.SELECTED
            pygame.draw.rect(surface, color, cell)
            pygame.draw.rect(surface, Colors.GRID, cell, 1)
            if ship and pos in ship.hits:
                pygame.draw.circle(surface, Colors.RED, cell.center, GameSettings.CELL // 3)
            elif (reveal or pos in board.exposed or pos in board.scans) and ship:
                pygame.draw.circle(surface, Colors.GREEN, cell.center, GameSettings.CELL // 4)
            elif pos in board.exposed:
                pygame.draw.circle(surface, Colors.MUTED, cell.center, 5)
            if reveal and board.asteroid_at(pos):
                pygame.draw.circle(surface, Colors.ORANGE, cell.center, GameSettings.CELL // 3)


def draw_ship_list(surface: pygame.Surface, font: pygame.font.Font, ships: list[Ship], start: Coord) -> None:
    y = start[1]
    for ship in ships:
        status = "X" if ship.sunk else f"{len(ship.hits)}/{ship.length}"
        power = "gebruikt" if ship.power_used else "klaar"
        disabled = f", EMP {ship.disabled_turns}" if ship.disabled_turns else ""
        color = Colors.RED if ship.sunk else Colors.MUTED
        draw_text(surface, font, f"{ship.id}. {ship.name}", (start[0], y), Colors.TEXT)
        draw_text(surface, font, f"{status} - {power}{disabled}", (start[0], y + 20), color)
        y += 50


def draw_legend(surface: pygame.Surface, font: pygame.font.Font, pos: Coord) -> None:
    pygame.draw.rect(surface, Colors.PANEL_BG, pygame.Rect(pos[0] - 12, pos[1] - 12, 230, 170))
    draw_text(surface, font, "Legenda", pos, Colors.TEXT)
    draw_marker(surface, (pos[0], pos[1] + 34), Colors.GREEN, "schipvak", font)
    draw_marker(surface, (pos[0], pos[1] + 62), Colors.RED, "geraakt", font)
    draw_marker(surface, (pos[0], pos[1] + 90), Colors.MUTED, "mis / onderzocht", font)
    draw_marker(surface, (pos[0], pos[1] + 118), Colors.ORANGE, "asteroide", font)


def draw_ui(surface: pygame.Surface, game: Game, font: pygame.font.Font, small: pygame.font.Font) -> None:
    surface.fill(Colors.BG)
    pygame.draw.rect(surface, Colors.PANEL_BG, pygame.Rect(0, 0, surface.get_width(), 138))
    draw_text(surface, pygame.font.SysFont("arial", 32), "Cosmic Confrontation", (GameSettings.LEFT, 24), Colors.TEXT)
    draw_text(surface, small, "A = aanval    P = speciale kracht    M = bewegen    O = salvo richting    R = herstart", (GameSettings.LEFT, 70), Colors.MUTED)
    mode_text = f"Modus: {game.mode}     Salvo: {'horizontaal' if game.salvo_axis == (1, 0) else 'verticaal'}"
    draw_text(surface, font, mode_text, (GameSettings.LEFT, 108), Colors.BLUE)
    draw_text(surface, font, "Eigen vloot", (GameSettings.LEFT, GameSettings.TOP - 44))
    draw_text(surface, font, "Vijand", (board_rect(game.size, True).x, GameSettings.TOP - 44))
    draw_board(surface, game.player, board_rect(game.size, False), True, game.selected_ship)
    draw_board(surface, game.enemy, board_rect(game.size, True), False, None)
    panel_x = board_rect(game.size, True).right + 24
    draw_text(surface, font, "Schepen", (panel_x, GameSettings.TOP - 44))
    draw_ship_list(surface, small, game.player.ships, (panel_x, GameSettings.TOP))
    draw_legend(surface, small, (panel_x, GameSettings.TOP + 430))
    boards_right = board_rect(game.size, True).right
    message_rect = pygame.Rect(GameSettings.LEFT, board_rect(game.size, False).bottom + 26, boards_right - GameSettings.LEFT, 50)
    pygame.draw.rect(surface, Colors.PANEL_BG, message_rect)
    draw_text(surface, font, game.message, (message_rect.x + 14, message_rect.y + 11), Colors.YELLOW)


def start_screen(screen: pygame.Surface, clock: pygame.time.Clock) -> int:
    font = pygame.font.SysFont("arial", 34)
    small = pygame.font.SysFont("arial", 22)
    size = GameSettings.START_SIZE
    while True:
        screen.fill(Colors.BG)
        draw_text(screen, font, "Cosmic Confrontation", (80, 80))
        draw_text(screen, small, f"Bordgrootte: {size}x{size}", (80, 140), Colors.TEXT)
        draw_text(screen, small, "Gebruik pijltjes links/rechts en druk op Enter.", (80, 174), Colors.MUTED)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    size = max(GameSettings.MIN_SIZE, size - 1)
                elif event.key == pygame.K_RIGHT:
                    size = min(GameSettings.MAX_SIZE, size + 1)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return size
        clock.tick(30)


def handle_key(game: Game, key: int) -> None:
    if key == pygame.K_a:
        game.mode = "attack"
        game.message = "Klik op het vijandelijke bord om aan te vallen."
    elif key == pygame.K_p:
        game.mode = "power"
        game.message = "Selecteer een eigen schip en klik op het juiste bord voor de kracht."
    elif key == pygame.K_m:
        game.mode = "move"
        game.message = "Selecteer een eigen schip en gebruik de pijltjestoetsen."
    elif key == pygame.K_o:
        game.salvo_axis = (0, 1) if game.salvo_axis == (1, 0) else (1, 0)
    elif key == pygame.K_r:
        game.__init__(game.size)
    elif game.mode == "move":
        directions = {
            pygame.K_LEFT: (-1, 0),
            pygame.K_RIGHT: (1, 0),
            pygame.K_UP: (0, -1),
            pygame.K_DOWN: (0, 1),
        }
        if key in directions and not game.game_over:
            game.move_selected(directions[key])


def run() -> None:
    pygame.init()
    pygame.display.set_caption("Cosmic Confrontation")
    screen = pygame.display.set_mode(GameSettings.START_WINDOW)
    clock = pygame.time.Clock()
    size = start_screen(screen, clock)
    width = max(GameSettings.MIN_WINDOW[0], GameSettings.LEFT * 2 + GameSettings.CELL * size * 2 + GameSettings.GAP + GameSettings.PANEL)
    height = max(GameSettings.MIN_WINDOW[1], GameSettings.TOP + GameSettings.CELL * size + 110)
    screen = pygame.display.set_mode((width, height))
    game = Game(size)
    font = pygame.font.SysFont("arial", 24)
    small = pygame.font.SysFont("arial", 18)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                handle_key(game, event.key)
            if event.type == pygame.MOUSEBUTTONDOWN and not game.game_over:
                hit = cell_from_mouse(event.pos, game.size)
                if not hit:
                    continue
                is_enemy, cell = hit
                if event.button == 1 and not is_enemy:
                    game.select_ship(cell, own_board=True)
                elif game.mode == "attack" and is_enemy:
                    game.use_attack(cell)
                elif game.mode == "power":
                    game.use_power(cell, own_board=not is_enemy)
        draw_ui(screen, game, font, small)
        pygame.display.flip()
        clock.tick(60)
