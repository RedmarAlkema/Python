from __future__ import annotations

import pygame

from config.colors import Colors
from config.settings import GameSettings
from domain.board import Board
from domain.geometry import Coord
from domain.ships import Ship
from game import Game
from presentation.layout import board_rect, fullscreen_button, fullscreen_label, main_menu_button


def draw_text(surface: pygame.Surface, font: pygame.font.Font, text: str, pos: Coord, color=Colors.TEXT) -> None:
    surface.blit(font.render(text, True, color), pos)


def draw_wrapped_text(surface: pygame.Surface, font: pygame.font.Font, text: str, rect: pygame.Rect, color=Colors.TEXT) -> None:
    lines = _wrap_lines(font, text, rect.width)
    for index, line_text in enumerate(lines):
        y = rect.y + index * font.get_linesize()
        if y + font.get_linesize() > rect.bottom:
            break
        surface.blit(font.render(line_text, True, color), (rect.x, y))


def draw_panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    fill: tuple[int, int, int] = Colors.PANEL_BG,
    border: tuple[int, int, int] = Colors.GRID,
) -> None:
    pygame.draw.rect(surface, fill, rect, border_radius=12)
    pygame.draw.rect(surface, border, rect, width=1, border_radius=12)


def draw_fullscreen_button(surface: pygame.Surface, font: pygame.font.Font) -> pygame.Rect:
    rect = fullscreen_button(surface)
    pygame.draw.rect(surface, Colors.BLUE, rect, border_radius=6)
    text = font.render(fullscreen_label(), True, Colors.TEXT)
    surface.blit(text, text.get_rect(center=rect.center))
    return rect


def draw_main_menu_button(surface: pygame.Surface, font: pygame.font.Font) -> pygame.Rect:
    rect = main_menu_button(surface)
    pygame.draw.rect(surface, Colors.PANEL_BG, rect, border_radius=6)
    pygame.draw.rect(surface, Colors.GRID, rect, width=1, border_radius=6)
    text = font.render("Hoofdmenu", True, Colors.TEXT)
    surface.blit(text, text.get_rect(center=rect.center))
    return rect


def draw_board(surface: pygame.Surface, board: Board, rect: pygame.Rect, reveal: bool, selected: Ship | None, font: pygame.font.Font) -> None:
    draw_panel(surface, rect.inflate(12, 12))
    for y in range(board.size):
        for x in range(board.size):
            _draw_cell(surface, board, rect, (x, y), reveal, selected, font)


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
    draw_panel(surface, pygame.Rect(pos[0] - 12, pos[1] - 12, 230, 170))
    draw_text(surface, font, "Legenda", pos, Colors.TEXT)
    _draw_marker(surface, (pos[0], pos[1] + 34), Colors.GREEN, "schipvak", font)
    _draw_marker(surface, (pos[0], pos[1] + 62), Colors.RED, "geraakt", font)
    _draw_marker(surface, (pos[0], pos[1] + 90), Colors.MUTED, "mis / onderzocht", font)
    _draw_marker(surface, (pos[0], pos[1] + 118), Colors.ORANGE, "asteroide", font)


def draw_game_screen(surface: pygame.Surface, game: Game, font: pygame.font.Font, small: pygame.font.Font) -> None:
    surface.fill(Colors.BG)
    _draw_game_header(surface, game, font, small)
    _draw_boards(surface, game, font, small)
    _draw_side_panels(surface, game, font, small)
    _draw_message(surface, game, font)


def _draw_game_header(surface: pygame.Surface, game: Game, font: pygame.font.Font, small: pygame.font.Font) -> None:
    draw_panel(surface, pygame.Rect(14, 14, surface.get_width() - 28, 126))
    draw_text(surface, pygame.font.SysFont("arial", 32), "Cosmic Confrontation", (GameSettings.LEFT, 24), Colors.TEXT)
    draw_text(surface, small, "Klik eigen schip = selecteren | Pijltjes = bewegen | Klik bordvak = power/aanval | Esc = deselect | C cheat | R herstart", (GameSettings.LEFT, 70), Colors.MUTED)
    draw_main_menu_button(surface, small)
    draw_text(surface, font, _mode_text(game), (GameSettings.LEFT, 104), Colors.BLUE)


def _draw_boards(surface: pygame.Surface, game: Game, font: pygame.font.Font, small: pygame.font.Font) -> None:
    draw_text(surface, font, "Eigen vloot", (GameSettings.LEFT, GameSettings.TOP - 44))
    draw_text(surface, font, "Vijand", (board_rect(game.size, True).x, GameSettings.TOP - 44))
    draw_board(surface, game.player, board_rect(game.size, False), True, game.selected_ship, small)
    draw_board(surface, game.enemy, board_rect(game.size, True), game.cheat_enabled or game.game_over, None, small)


def _draw_side_panels(surface: pygame.Surface, game: Game, font: pygame.font.Font, small: pygame.font.Font) -> None:
    panel_x = board_rect(game.size, True).right + 24
    panel_top = GameSettings.TOP - 30
    draw_panel(surface, pygame.Rect(panel_x - 14, panel_top, 258, 500))
    draw_text(surface, font, "Schepen", (panel_x, panel_top + 14))
    draw_ship_list(surface, small, game.player.ships, (panel_x, panel_top + 58))
    draw_legend(surface, small, (panel_x + 284, panel_top + 14))


def _draw_message(surface: pygame.Surface, game: Game, font: pygame.font.Font) -> None:
    boards_right = board_rect(game.size, True).right
    message_rect = pygame.Rect(GameSettings.LEFT, board_rect(game.size, False).bottom + 26, boards_right - GameSettings.LEFT, 82)
    draw_panel(surface, message_rect)
    draw_wrapped_text(surface, font, game.message, message_rect.inflate(-28, -20), Colors.YELLOW)


def _draw_cell(
    surface: pygame.Surface,
    board: Board,
    rect: pygame.Rect,
    pos: Coord,
    reveal: bool,
    selected: Ship | None,
    font: pygame.font.Font,
) -> None:
    cell = pygame.Rect(rect.x + pos[0] * GameSettings.CELL, rect.y + pos[1] * GameSettings.CELL, GameSettings.CELL - 2, GameSettings.CELL - 2)
    ship = board.ship_at(pos)
    pygame.draw.rect(surface, _cell_color(board, pos, reveal, selected, ship), cell)
    pygame.draw.rect(surface, Colors.GRID, cell, 1)
    _draw_cell_marker(surface, board, cell, pos, reveal, ship, font)


def _draw_cell_marker(surface: pygame.Surface, board: Board, cell: pygame.Rect, pos: Coord, reveal: bool, ship: Ship | None, font: pygame.font.Font) -> None:
    if ship and pos in ship.hits:
        pygame.draw.circle(surface, Colors.RED, cell.center, GameSettings.CELL // 3)
    elif (reveal or pos in board.exposed or pos in board.scans) and ship:
        pygame.draw.circle(surface, Colors.GREEN, cell.center, GameSettings.CELL // 4)
    elif pos in board.exposed:
        pygame.draw.circle(surface, Colors.MUTED, cell.center, 5)
    if _asteroid_visible(board, pos, reveal):
        _draw_asteroid(surface, board, cell, pos, reveal, font)


def _cell_color(board: Board, pos: Coord, reveal: bool, selected: Ship | None, ship: Ship | None) -> tuple[int, int, int]:
    if selected and pos in selected.cells:
        return Colors.SELECTED
    if reveal and ship:
        return Colors.SHIP
    if pos in board.scans:
        return Colors.SCAN
    if pos in board.exposed:
        return Colors.EXPOSED
    return Colors.UNKNOWN


def _asteroid_visible(board: Board, pos: Coord, reveal: bool) -> bool:
    return board.asteroid_at(pos) is not None and (reveal or pos in board.exposed or pos in board.scans)


def _draw_asteroid(surface: pygame.Surface, board: Board, cell: pygame.Rect, pos: Coord, reveal: bool, font: pygame.font.Font) -> None:
    asteroid = board.asteroid_at(pos)
    if not asteroid:
        return
    pygame.draw.circle(surface, Colors.ORANGE, cell.center, GameSettings.CELL // 3)
    label = _asteroid_arrow(asteroid.direction) if reveal else "A"
    draw_text(surface, font, label, (cell.x + 8, cell.y + 10), Colors.TEXT)


def _mode_text(game: Game) -> str:
    if game.selected_ship:
        text = f"Geselecteerd: {game.selected_ship.name}  (Power: {game.selected_ship.power})"
    else:
        text = "Geen schip geselecteerd. Klik op vijandelijk bord om standaard aan te vallen."
    return f"{text}     Cheat: aan" if game.cheat_enabled else text


def _draw_marker(surface: pygame.Surface, pos: Coord, color: tuple[int, int, int], label: str, font: pygame.font.Font) -> None:
    pygame.draw.circle(surface, color, (pos[0] + 7, pos[1] + 9), 7)
    draw_text(surface, font, label, (pos[0] + 20, pos[1]), Colors.MUTED)


def _wrap_lines(font: pygame.font.Font, text: str, width: int) -> list[str]:
    lines: list[str] = []
    line = ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if font.size(candidate)[0] <= width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def _asteroid_arrow(direction: Coord) -> str:
    return {
        (-1, -1): "NW",
        (1, -1): "NE",
        (-1, 1): "SW",
        (1, 1): "SE",
    }.get(direction, "*")
