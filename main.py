from __future__ import annotations

import sys

import pygame

from ai import random_ai_turn
from models import Board, Coord, Ship, line

CELL = 40
GAP = 56
TOP = 188
LEFT = 28
PANEL = 300
BG = (13, 18, 28)
PANEL_BG = (18, 27, 42)
GRID = (91, 112, 138)
TEXT = (242, 247, 252)
MUTED = (172, 185, 202)
BLUE = (96, 165, 250)
GREEN = (48, 209, 119)
RED = (255, 82, 82)
YELLOW = (234, 179, 8)
ORANGE = (249, 115, 22)
UNKNOWN = (22, 34, 52)
EXPOSED = (58, 75, 99)
SCAN = (50, 88, 122)
SHIP = (36, 135, 105)
SELECTED = (26, 165, 180)


class Game:
    def __init__(self, size: int) -> None:
        self.size = size
        self.player = Board(size)
        self.enemy = Board(size)
        for board in (self.player, self.enemy):
            board.randomize_fleet()
            board.place_asteroids()
        self.mode = "attack"
        self.salvo_axis = (1, 0)
        self.selected_ship: Ship | None = None
        self.message = "Klik op het vijandelijke bord om aan te vallen."
        self.game_over = False

    def end_player_turn(self) -> None:
        if self.enemy.fleet_destroyed():
            self.message = "Gewonnen: de vijandelijke vloot is vernietigd."
            self.game_over = True
            return
        messages = self.player.move_asteroids() + self.enemy.move_asteroids()
        ai_message = random_ai_turn(self.enemy, self.player)
        self.player.tick_disables()
        self.enemy.tick_disables()
        if self.player.fleet_destroyed():
            self.message = "Verloren: jouw vloot is vernietigd."
            self.game_over = True
        else:
            extra = f" {' '.join(messages)}" if messages else ""
            self.message = f"{ai_message}.{extra}"

    def select_ship(self, pos: Coord, own_board: bool) -> None:
        board = self.player if own_board else self.enemy
        ship = board.ship_at(pos)
        if not ship:
            self.message = "Geen schip geselecteerd."
            return
        self.selected_ship = ship
        self.message = f"{ship.name} geselecteerd ({ship.power})."

    def use_attack(self, pos: Coord) -> None:
        result, ship = self.enemy.receive_attack(pos)
        name = f" op {ship.name}" if ship else ""
        self.message = f"Aanval {pos}: {result}{name}."
        self.end_player_turn()

    def use_power(self, pos: Coord, own_board: bool) -> None:
        ship = self.selected_ship
        if not ship:
            self.message = "Selecteer eerst een eigen schip met linkermuisknop."
            return
        if ship.power_used:
            self.message = f"{ship.name} heeft de speciale kracht al gebruikt."
            return
        if ship.disabled_turns > 0:
            self.message = f"{ship.name} is uitgeschakeld."
            return

        power = ship.power
        if power == "Radar Scan" and not own_board:
            hits = self.enemy.scan(pos)
            found = sum(1 for _, has_ship in hits if has_ship)
            self.message = f"Radar scan rond {pos}: {found} schipvakje(s) gevonden."
        elif power == "Homing Missile" and not own_board:
            target = self.enemy.nearest_ship_cell(pos)
            if target is None:
                self.message = "Geen doelwit gevonden."
                return
            result, target_ship = self.enemy.receive_attack(target)
            self.message = f"Homing missile raakt {target}: {result} op {target_ship.name}."
        elif power == "EMP Uitschakeling" and not own_board:
            target_ship = self.enemy.ship_at(pos)
            if not target_ship or pos not in self.enemy.exposed:
                self.message = "EMP kan alleen op een zichtbaar vijandelijk schip."
                return
            target_ship.disabled_turns = 3
            self.message = f"EMP schakelt {target_ship.name} drie beurten uit."
        elif power == "Salvo Aanval" and not own_board:
            results = self.enemy.attack_many(line(pos, self.salvo_axis, 3))
            self.message = f"Salvo uitgevoerd: {', '.join(results)}."
        elif power == "Space Smoke" and own_board:
            self.player.hide_area(pos)
            self.message = f"Space Smoke verbergt 3x3 gebied rond {pos}."
        else:
            self.message = "Deze kracht werkt niet op dat bord."
            return
        ship.power_used = True
        self.end_player_turn()

    def move_selected(self, direction: Coord) -> None:
        if not self.selected_ship:
            self.message = "Selecteer eerst een eigen schip."
            return
        self.message = self.player.move_ship(self.selected_ship, direction)
        self.end_player_turn()


def board_rect(size: int, enemy: bool) -> pygame.Rect:
    x = LEFT + (CELL * size + GAP) * int(enemy)
    return pygame.Rect(x, TOP, CELL * size, CELL * size)


def cell_from_mouse(pos: Coord, size: int) -> tuple[bool, Coord] | None:
    for is_enemy in (False, True):
        rect = board_rect(size, is_enemy)
        if rect.collidepoint(pos):
            return is_enemy, ((pos[0] - rect.x) // CELL, (pos[1] - rect.y) // CELL)
    return None


def draw_text(surface: pygame.Surface, font: pygame.font.Font, text: str, pos: Coord, color=TEXT) -> None:
    surface.blit(font.render(text, True, color), pos)


def draw_marker(surface: pygame.Surface, pos: Coord, color: tuple[int, int, int], label: str, font: pygame.font.Font) -> None:
    pygame.draw.circle(surface, color, (pos[0] + 7, pos[1] + 9), 7)
    draw_text(surface, font, label, (pos[0] + 20, pos[1]), MUTED)


def draw_board(surface: pygame.Surface, board: Board, rect: pygame.Rect, reveal: bool, selected: Ship | None) -> None:
    pygame.draw.rect(surface, PANEL_BG, rect.inflate(10, 10))
    for y in range(board.size):
        for x in range(board.size):
            pos = (x, y)
            cell = pygame.Rect(rect.x + x * CELL, rect.y + y * CELL, CELL - 2, CELL - 2)
            color = UNKNOWN
            ship = board.ship_at(pos)
            if pos in board.exposed:
                color = EXPOSED
            if pos in board.scans:
                color = SCAN
            if reveal and ship:
                color = SHIP
            if selected and pos in selected.cells:
                color = SELECTED
            pygame.draw.rect(surface, color, cell)
            pygame.draw.rect(surface, GRID, cell, 1)
            if ship and pos in ship.hits:
                pygame.draw.circle(surface, RED, cell.center, CELL // 3)
            elif (reveal or pos in board.exposed or pos in board.scans) and ship:
                pygame.draw.circle(surface, GREEN, cell.center, CELL // 4)
            elif pos in board.exposed:
                pygame.draw.circle(surface, MUTED, cell.center, 5)
            if reveal and board.asteroid_at(pos):
                pygame.draw.circle(surface, ORANGE, cell.center, CELL // 3)


def draw_ship_list(surface: pygame.Surface, font: pygame.font.Font, ships: list[Ship], start: Coord) -> None:
    y = start[1]
    for ship in ships:
        status = "X" if ship.sunk else f"{len(ship.hits)}/{ship.length}"
        power = "gebruikt" if ship.power_used else "klaar"
        disabled = f", EMP {ship.disabled_turns}" if ship.disabled_turns else ""
        color = RED if ship.sunk else MUTED
        draw_text(surface, font, f"{ship.id}. {ship.name}", (start[0], y), TEXT)
        draw_text(surface, font, f"{status} - {power}{disabled}", (start[0], y + 20), color)
        y += 50


def draw_legend(surface: pygame.Surface, font: pygame.font.Font, pos: Coord) -> None:
    pygame.draw.rect(surface, PANEL_BG, pygame.Rect(pos[0] - 12, pos[1] - 12, 230, 170))
    draw_text(surface, font, "Legenda", pos, TEXT)
    draw_marker(surface, (pos[0], pos[1] + 34), GREEN, "schipvak", font)
    draw_marker(surface, (pos[0], pos[1] + 62), RED, "geraakt", font)
    draw_marker(surface, (pos[0], pos[1] + 90), MUTED, "mis / onderzocht", font)
    draw_marker(surface, (pos[0], pos[1] + 118), ORANGE, "asteroide", font)


def draw_ui(surface: pygame.Surface, game: Game, font: pygame.font.Font, small: pygame.font.Font) -> None:
    surface.fill(BG)
    pygame.draw.rect(surface, PANEL_BG, pygame.Rect(0, 0, surface.get_width(), 138))
    draw_text(surface, pygame.font.SysFont("arial", 32), "Cosmic Confrontation", (LEFT, 24), TEXT)
    draw_text(surface, small, "A = aanval    P = speciale kracht    M = bewegen    O = salvo richting    R = herstart", (LEFT, 70), MUTED)
    mode_text = f"Modus: {game.mode}     Salvo: {'horizontaal' if game.salvo_axis == (1, 0) else 'verticaal'}"
    draw_text(surface, font, mode_text, (LEFT, 108), BLUE)
    draw_text(surface, font, "Eigen vloot", (LEFT, TOP - 44))
    draw_text(surface, font, "Vijand", (board_rect(game.size, True).x, TOP - 44))
    draw_board(surface, game.player, board_rect(game.size, False), True, game.selected_ship)
    draw_board(surface, game.enemy, board_rect(game.size, True), False, None)
    panel_x = board_rect(game.size, True).right + 24
    draw_text(surface, font, "Schepen", (panel_x, TOP - 44))
    draw_ship_list(surface, small, game.player.ships, (panel_x, TOP))
    draw_legend(surface, small, (panel_x, TOP + 430))
    boards_right = board_rect(game.size, True).right
    message_rect = pygame.Rect(LEFT, board_rect(game.size, False).bottom + 26, boards_right - LEFT, 50)
    pygame.draw.rect(surface, PANEL_BG, message_rect)
    draw_text(surface, font, game.message, (message_rect.x + 14, message_rect.y + 11), YELLOW)


def start_screen(screen: pygame.Surface, clock: pygame.time.Clock) -> int:
    font = pygame.font.SysFont("arial", 34)
    small = pygame.font.SysFont("arial", 22)
    size = 10
    while True:
        screen.fill(BG)
        draw_text(screen, font, "Cosmic Confrontation", (80, 80))
        draw_text(screen, small, f"Bordgrootte: {size}x{size}", (80, 140), TEXT)
        draw_text(screen, small, "Gebruik pijltjes links/rechts en druk op Enter.", (80, 174), MUTED)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    size = max(8, size - 1)
                elif event.key == pygame.K_RIGHT:
                    size = min(16, size + 1)
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


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Cosmic Confrontation")
    screen = pygame.display.set_mode((1280, 760))
    clock = pygame.time.Clock()
    size = start_screen(screen, clock)
    width = max(1360, LEFT * 2 + CELL * size * 2 + GAP + PANEL)
    height = max(860, TOP + CELL * size + 110)
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


if __name__ == "__main__":
    main()
