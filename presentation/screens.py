from __future__ import annotations

import sys

import pygame

from config.colors import Colors
from config.fleet_blueprints import FLEET_BLUEPRINTS
from config.settings import GameSettings
from domain.ships import SHIP_TYPES, Ship
from game import Game
from presentation.drawing import draw_board, draw_fullscreen_button, draw_panel, draw_text
from presentation.layout import board_rect, cell_from_mouse, game_window_size, set_display, toggle_fullscreen
from storage import load_game_statistics, load_saved_games


def fleet_queue() -> list[type[Ship]]:
    queue: list[type[Ship]] = []
    for blueprint in FLEET_BLUEPRINTS:
        queue.extend(SHIP_TYPES[blueprint.name] for _ in range(blueprint.amount))
    return queue


def place_player_fleet(screen: pygame.Surface, clock: pygame.time.Clock, game: Game) -> Game:
    font = pygame.font.SysFont("arial", 28)
    small = pygame.font.SysFont("arial", 19)
    ships_to_place = fleet_queue()
    horizontal = True

    while ships_to_place:
        _draw_placement_screen(screen, game, ships_to_place, horizontal, font, small)
        pygame.display.flip()
        screen, horizontal = _handle_placement_events(screen, game, ships_to_place, horizontal)
        clock.tick(30)

    game.finish_player_setup()
    return game


def save_state_screen(screen: pygame.Surface, clock: pygame.time.Clock, save: dict) -> None:
    font = pygame.font.SysFont("arial", 28)
    small = pygame.font.SysFont("arial", 16)
    preview = Game.from_dict(save)
    while True:
        _draw_save_preview(screen, preview, font, small)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_f, pygame.K_F11):
                    screen = toggle_fullscreen(game_window_size(preview.size))
                elif event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                    return
        clock.tick(30)


def start_screen(screen: pygame.Surface, clock: pygame.time.Clock) -> Game:
    font = pygame.font.SysFont("arial", 34)
    small = pygame.font.SysFont("arial", 22)
    state = {"size": GameSettings.START_SIZE, "nickname": "Speler", "selected_save": 0, "show_statistics": False}
    while True:
        saves = load_saved_games()
        statistics = load_game_statistics()
        state["selected_save"] = min(state["selected_save"], max(0, len(saves) - 1))
        fullscreen_rect = _draw_start_screen(screen, state, saves, statistics, font, small)
        pygame.display.flip()

        game = _handle_start_events(screen, clock, state, saves, fullscreen_rect)
        if game:
            return game
        clock.tick(30)


def _draw_placement_screen(
    screen: pygame.Surface,
    game: Game,
    ships_to_place: list[type[Ship]],
    horizontal: bool,
    font: pygame.font.Font,
    small: pygame.font.Font,
) -> None:
    ship_cls = ships_to_place[0]
    screen.fill(Colors.BG)
    draw_panel(screen, pygame.Rect(14, 14, screen.get_width() - 28, 126))
    draw_text(screen, font, "Plaats je vloot", (GameSettings.LEFT, 28), Colors.TEXT)
    draw_text(screen, small, "Klik op het bord. R = draaien. Backspace = terug. F = fullscreen. Esc = afsluiten.", (GameSettings.LEFT, 72), Colors.MUTED)
    direction = "horizontaal" if horizontal else "verticaal"
    draw_text(screen, small, f"Nu: {ship_cls.ship_name} ({ship_cls.ship_length} vakjes), {direction}", (GameSettings.LEFT, 104), Colors.BLUE)
    draw_text(screen, font, "Eigen vloot", (GameSettings.LEFT, GameSettings.TOP - 44), Colors.TEXT)
    draw_board(screen, game.player, board_rect(game.size, False), True, None, small)
    _draw_placement_queue(screen, ships_to_place, font, small, board_rect(game.size, False).right + 40)


def _draw_placement_queue(screen: pygame.Surface, ships_to_place: list[type[Ship]], font: pygame.font.Font, small: pygame.font.Font, panel_x: int) -> None:
    panel_top = GameSettings.TOP - 30
    draw_panel(screen, pygame.Rect(panel_x - 14, panel_top, 258, 320))
    draw_text(screen, font, "Nog te plaatsen", (panel_x, panel_top + 14), Colors.TEXT)
    for index, queued_cls in enumerate(ships_to_place[:9]):
        draw_text(screen, small, f"{queued_cls.ship_name} - {queued_cls.ship_length}", (panel_x, panel_top + 58 + index * 28), Colors.MUTED)


def _handle_placement_events(screen: pygame.Surface, game: Game, ships_to_place: list[type[Ship]], horizontal: bool) -> tuple[pygame.Surface, bool]:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            screen, horizontal = _handle_placement_key(screen, game, ships_to_place, horizontal, event.key)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            _place_ship_from_mouse(event.pos, game, ships_to_place, horizontal)
    return screen, horizontal


def _handle_placement_key(screen: pygame.Surface, game: Game, ships_to_place: list[type[Ship]], horizontal: bool, key: int) -> tuple[pygame.Surface, bool]:
    if key == pygame.K_ESCAPE:
        pygame.quit()
        sys.exit()
    if key in (pygame.K_f, pygame.K_F11):
        screen = toggle_fullscreen(game_window_size(game.size))
    if key == pygame.K_r:
        return screen, not horizontal
    if key == pygame.K_BACKSPACE and game.player.board.ships:
        removed = game.player.board.ships.pop()
        game.player.board.next_ship_id -= 1
        ships_to_place.insert(0, type(removed))
    return screen, horizontal


def _place_ship_from_mouse(pos: tuple[int, int], game: Game, ships_to_place: list[type[Ship]], horizontal: bool) -> None:
    hit = cell_from_mouse(pos, game.size)
    if not hit:
        return
    is_enemy, cell = hit
    if not is_enemy and game.player.board.place_ship(ships_to_place[0], cell, horizontal):
        ships_to_place.pop(0)


def _draw_save_preview(screen: pygame.Surface, preview: Game, font: pygame.font.Font, small: pygame.font.Font) -> None:
    screen.fill(Colors.BG)
    pygame.draw.rect(screen, Colors.PANEL_BG, pygame.Rect(0, 0, screen.get_width(), 138))
    draw_text(screen, font, "Laatste opgeslagen staat", (GameSettings.LEFT, 28), Colors.TEXT)
    draw_text(screen, small, "Esc = terug naar menu. F = fullscreen.", (GameSettings.LEFT, 78), Colors.MUTED)
    draw_text(screen, small, f"{preview.nickname} - {preview.started_at} - winnaar: {preview.winner or 'nog bezig'}", (GameSettings.LEFT, 106), Colors.BLUE)
    draw_text(screen, font, "Eigen vloot", (GameSettings.LEFT, GameSettings.TOP - 44))
    draw_text(screen, font, "Vijand", (board_rect(preview.size, True).x, GameSettings.TOP - 44))
    draw_board(screen, preview.player, board_rect(preview.size, False), True, preview.selected_ship, small)
    draw_board(screen, preview.enemy, board_rect(preview.size, True), True, None, small)


def _draw_start_screen(
    screen: pygame.Surface,
    state: dict,
    saves: list[dict],
    statistics: list[dict],
    font: pygame.font.Font,
    small: pygame.font.Font,
) -> pygame.Rect:
    screen.fill(Colors.BG)
    draw_text(screen, font, "Cosmic Confrontation", (80, 80))
    fullscreen_rect = draw_fullscreen_button(screen, small)
    draw_text(screen, small, f"Nickname: {state['nickname']}", (80, 140), Colors.TEXT)
    draw_text(screen, small, f"Nieuw bord: {state['size']}x{state['size']}", (80, 174), Colors.TEXT)
    draw_text(screen, small, "Typ je naam. Links/rechts = grootte. N = nieuw spel. F = fullscreen.", (80, 208), Colors.MUTED)
    draw_text(screen, small, "Omhoog/omlaag = opgeslagen spel. Enter = verder spelen. V = inzien. S = statistieken.", (80, 236), Colors.MUTED)
    _draw_start_rows(screen, state, saves, statistics, small)
    return fullscreen_rect


def _draw_start_rows(screen: pygame.Surface, state: dict, saves: list[dict], statistics: list[dict], small: pygame.font.Font) -> None:
    rows = statistics if state["show_statistics"] else saves
    draw_text(screen, small, "Statistieken" if state["show_statistics"] else "Opgeslagen spellen", (80, 294), Colors.TEXT)
    if not saves:
        draw_text(screen, small, "Nog geen opgeslagen spellen.", (80, 330), Colors.MUTED)
    for index, row in enumerate(rows[-8:]):
        real_index = len(rows) - min(8, len(rows)) + index
        color = Colors.YELLOW if real_index == state["selected_save"] else Colors.MUTED
        draw_text(screen, small, _start_row_text(row, real_index, state), (80, 330 + index * 28), color)


def _start_row_text(row: dict, real_index: int, state: dict) -> str:
    prefix = "> " if real_index == state["selected_save"] else "  "
    if state["show_statistics"]:
        result = _result_text(row)
        return (
            f"{prefix}{row.get('nickname')} - {result} - {row.get('size')}x{row.get('size')} - "
            f"beurten {row.get('turns')} - jij geraakt {row.get('player_hits')} - "
            f"vijand geraakt {row.get('enemy_hits')}"
        )
    winner = row.get("winner") or "nog bezig"
    return f"{prefix}{row.get('nickname', 'Speler')} - {row.get('updated_at', row.get('started_at', '?'))} - {row.get('size', '?')}x{row.get('size', '?')} - {winner}"


def _result_text(row: dict) -> str:
    winner = row.get("winner")
    if winner in (None, "", "nog bezig"):
        return "Nog bezig"
    if winner == "AI":
        return "Verloren van AI"
    if winner == row.get("nickname"):
        return "Gewonnen van AI"
    return f"Winnaar: {winner}"


def _handle_start_events(screen: pygame.Surface, clock: pygame.time.Clock, state: dict, saves: list[dict], fullscreen_rect: pygame.Rect) -> Game | None:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and fullscreen_rect.collidepoint(event.pos):
            toggle_fullscreen(GameSettings.START_WINDOW)
        if event.type == pygame.KEYDOWN:
            game = _handle_start_key(screen, clock, state, saves, event)
            if game:
                return game
    return None


def _handle_start_key(screen: pygame.Surface, clock: pygame.time.Clock, state: dict, saves: list[dict], event: pygame.event.Event) -> Game | None:
    if event.key in (pygame.K_f, pygame.K_F11):
        toggle_fullscreen(GameSettings.START_WINDOW)
    elif event.key == pygame.K_LEFT:
        state["size"] = max(GameSettings.MIN_SIZE, state["size"] - 1)
    elif event.key == pygame.K_RIGHT:
        state["size"] = min(GameSettings.MAX_SIZE, state["size"] + 1)
    elif event.key == pygame.K_UP and saves:
        state["selected_save"] = max(0, state["selected_save"] - 1)
    elif event.key == pygame.K_DOWN and saves:
        state["selected_save"] = min(len(saves) - 1, state["selected_save"] + 1)
    elif event.key == pygame.K_s:
        state["show_statistics"] = not state["show_statistics"]
    elif event.key == pygame.K_BACKSPACE:
        state["nickname"] = state["nickname"][:-1] or "Speler"
    elif event.key == pygame.K_n:
        screen = set_display(game_window_size(state["size"]))
        return place_player_fleet(screen, clock, Game(state["size"], state["nickname"], randomize_player=False))
    elif event.key == pygame.K_v and saves:
        _show_selected_save(screen, clock, state, saves)
    elif event.key in (pygame.K_RETURN, pygame.K_SPACE) and saves:
        return Game.from_dict(saves[state["selected_save"]])
    elif event.unicode and event.unicode.isprintable() and len(state["nickname"]) < 18:
        state["nickname"] = ("" if state["nickname"] == "Speler" else state["nickname"]) + event.unicode
    return None


def _show_selected_save(screen: pygame.Surface, clock: pygame.time.Clock, state: dict, saves: list[dict]) -> None:
    selected = saves[state["selected_save"]]
    screen = set_display(game_window_size(selected.get("size", state["size"])))
    save_state_screen(screen, clock, selected)
    set_display(GameSettings.START_WINDOW)
