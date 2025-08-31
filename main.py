"""
Vector Balls - A minimal 2D physics game using pygame.

Run:
  python main.py
"""

from __future__ import annotations

import sys
import math
from typing import List, Tuple, Optional
import pygame

import config
from game import Game
from settings import Settings, Color


def draw_text_center(surface: pygame.Surface, text: str, font: pygame.font.Font, color: Tuple[int, int, int], center: Tuple[int, int]) -> None:
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=center)
    surface.blit(surf, rect)

class InputBox:
    def __init__(self, rect: pygame.Rect, label: str, default: str, allowed: str, is_float: bool, min_val: Optional[float], max_val: Optional[float]):
        self.rect = rect
        self.label = label
        self.value = default
        self.allowed = allowed
        self.is_float = is_float
        self.min_val = min_val
        self.max_val = max_val
        self.active = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            else:
                ch = event.unicode
                if ch and ch in self.allowed and len(self.value) < 10:
                    self.value += ch

    def parse(self) -> Optional[float]:
        try:
            v = float(self.value) if self.is_float else float(int(self.value))
            if self.min_val is not None:
                v = max(self.min_val, v)
            if self.max_val is not None:
                v = min(self.max_val, v)
            return v
        except Exception:
            return None

    def draw(self, surface: pygame.Surface, label_font: pygame.font.Font, value_font: pygame.font.Font) -> None:
        # Label
        label_surf = label_font.render(self.label, True, (220, 220, 220))
        surface.blit(label_surf, (self.rect.x, self.rect.y - 22))
        # Box
        pygame.draw.rect(surface, (60, 60, 60), self.rect, border_radius=6)
        pygame.draw.rect(surface, (200, 200, 200) if self.active else (100, 100, 100), self.rect, 2, border_radius=6)
        # Value
        text = self.value if self.value != "" else " "
        val_surf = value_font.render(text, True, (255, 255, 255))
        surface.blit(val_surf, (self.rect.x + 8, self.rect.y + 6))


def settings_form_screen(screen: pygame.Surface, clock: pygame.time.Clock, default_settings: Optional[Settings] = None) -> Settings:
    title_font = pygame.font.Font(config.FONT_NAME, 28)
    label_font = pygame.font.Font(config.FONT_NAME, 18)
    value_font = pygame.font.Font(config.FONT_NAME, 22)

    # Input boxes with defaults
    boxes = [
        InputBox(
            pygame.Rect(60, 120, 220, 36),
            "Number of balls (2-12)",
            str(default_settings.num_balls if default_settings else config.NUM_BALLS),
            "0123456789", False, 2, 12
        ),
        InputBox(
            pygame.Rect(60, 200, 220, 36),
            "Lines per boundary hit (1-10)",
            str(default_settings.lines_per_boundary_hit if default_settings else config.LINES_PER_BOUNDARY_HIT),
            "0123456789", False, 1, 10
        ),
        InputBox(
            pygame.Rect(60, 280, 220, 36),
            "Ball-ball speed factor",
            str(default_settings.ball_collision_speed_increase_factor if default_settings else config.BALL_COLLISION_SPEED_INCREASE_FACTOR),
            "0123456789.-", True, 0.0, None
        ),
        InputBox(
            pygame.Rect(60, 360, 220, 36),
            "Boundary speed increase",
            str(default_settings.boundary_collision_speed_increase if default_settings else config.BOUNDARY_COLLISION_SPEED_INCREASE),
            "0123456789.-", True, 0.0, None
        ),
        InputBox(
            pygame.Rect(60, 440, 220, 36),
            "Arena size % (30-100)",
            str(int(default_settings.boundary_radius_ratio * 100) if default_settings else 80),
            "0123456789", False, 30, 100
        ),
    ]

    # Color palette and slots
    # Use the same color palette as config.py for consistency
    palette: List[Color] = config.COLORS.copy()
    chosen_colors: List[Color] = list(default_settings.colors) if default_settings else []

    def assign_random_colors(num_balls: int) -> List[Color]:
        """Assign random unique colors from config.COLORS for the given number of balls"""
        import random
        available_colors = config.COLORS.copy()
        random.shuffle(available_colors)
        return available_colors[:num_balls]

    # If no default settings and no chosen colors, assign random colors for initial display
    if not default_settings and not chosen_colors:
        initial_nb = 6  # Default number of balls for initial display (between 2-12)
        chosen_colors = assign_random_colors(initial_nb)
    focused_slot: int = 0

    def get_num_balls() -> int:
        v = boxes[0].parse()
        if v is not None:
            num = int(v)
            # Special handling: if user enters 1 or 0, set to 2
            if num <= 1:
                return 2
            # Cap at maximum of 12
            elif num > 12:
                return 12
            else:
                return num
        return config.NUM_BALLS

    start_button = pygame.Rect(60, 620, 140, 44)
    exit_button = pygame.Rect(220, 620, 140, 44)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
            for b in boxes:
                b.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # Color slots area
                nb = get_num_balls()
                # Ensure chosen_colors length equals nb with random unique colors
                if len(chosen_colors) != nb:
                    chosen_colors = assign_random_colors(nb)
                # Slots grid
                slot_x, slot_y = 340, 120
                for i in range(nb):
                    r = pygame.Rect(slot_x, slot_y + i * 40, 200, 32)
                    if r.collidepoint(mx, my):
                        focused_slot = i
                # Palette grid
                cols = 6
                sw = 40
                px = 580
                py = 120
                for idx, color in enumerate(palette):
                    gx = idx % cols
                    gy = idx // cols
                    rect = pygame.Rect(px + gx * sw, py + gy * sw, 32, 32)
                    if rect.collidepoint(mx, my):
                        if color not in chosen_colors:
                            if focused_slot < len(chosen_colors):
                                chosen_colors[focused_slot] = color
                # Start button
                if start_button.collidepoint(mx, my):
                    # Validate and start
                    nb = get_num_balls()
                    unique = len(set(chosen_colors[:nb])) == nb
                    parsed = [boxes[i].parse() for i in range(len(boxes))]
                    if all(v is not None for v in parsed) and unique:
                        lines_hit = int(parsed[1])
                        ball_factor = float(parsed[2])
                        boundary_inc = float(parsed[3])
                        arena_ratio = float(parsed[4]) / 100.0
                        return Settings(
                            num_balls=nb,
                            lines_per_boundary_hit=lines_hit,
                            ball_collision_speed_increase_factor=ball_factor,
                            boundary_collision_speed_increase=boundary_inc,
                            boundary_radius_ratio=arena_ratio,
                            colors=chosen_colors[:nb],
                        )
                # Exit button
                elif exit_button.collidepoint(mx, my):
                    pygame.quit()
                    sys.exit(0)

        screen.fill(config.BACKGROUND_COLOR)
        draw_text_center(screen, "Vector Balls - Setup", title_font, (240, 240, 240), (config.WINDOW_WIDTH // 2, 60))

        # Draw input boxes
        for b in boxes:
            b.draw(screen, label_font, value_font)

        # Draw color slots
        nb = get_num_balls()
        # Ensure we have the right number of random colors
        if len(chosen_colors) != nb:
            chosen_colors = assign_random_colors(nb)
        slot_x, slot_y = 340, 120
        label = label_font.render("Ball colors (unique)", True, (220, 220, 220))
        screen.blit(label, (slot_x, slot_y - 22))
        for i in range(nb):
            r = pygame.Rect(slot_x, slot_y + i * 40, 200, 32)
            pygame.draw.rect(screen, (80, 80, 80), r, border_radius=6)
            pygame.draw.rect(screen, (255, 255, 255) if i == focused_slot else (120, 120, 120), r, 2, border_radius=6)
            # Swatch and text
            pygame.draw.rect(screen, chosen_colors[i], pygame.Rect(r.x + 6, r.y + 6, 20, 20))
            txt = value_font.render(f"Ball {i+1}", True, (230, 230, 230))
            screen.blit(txt, (r.x + 36, r.y + 4))

        # Palette grid
        cols = 6
        sw = 40
        px = 580
        py = 120
        palette_label = label_font.render("Palette", True, (220, 220, 220))
        screen.blit(palette_label, (px, py - 22))
        for idx, color in enumerate(palette):
            gx = idx % cols
            gy = idx // cols
            rect = pygame.Rect(px + gx * sw, py + gy * sw, 32, 32)
            pygame.draw.rect(screen, color, rect)
            used = color in chosen_colors[:nb]
            pygame.draw.rect(screen, (255, 255, 255) if used else (40, 40, 40), rect, 2)

        # Validation hint and Start button
        unique = len(set(chosen_colors[:nb])) == nb
        valid_parsed = [boxes[i].parse() for i in range(len(boxes))]
        all_valid = all(v is not None for v in valid_parsed) and unique

        msg = "All good. Click Start." if all_valid else ("Set unique colors and valid numbers." if not unique else "Enter valid numbers.")
        hint = label_font.render(msg, True, (200, 200, 200))
        screen.blit(hint, (60, 584))

        # Draw Start button
        pygame.draw.rect(screen, (60, 140, 60) if all_valid else (80, 80, 80), start_button, border_radius=8)
        btn_text = value_font.render("Start", True, (255, 255, 255))
        screen.blit(btn_text, (start_button.x + 35, start_button.y + 8))

        # Draw Exit button
        pygame.draw.rect(screen, (140, 60, 60), exit_button, border_radius=8)
        exit_text = value_font.render("Exit", True, (255, 255, 255))
        screen.blit(exit_text, (exit_button.x + 40, exit_button.y + 8))

        pygame.display.flip()
        clock.tick(60)


def draw_quit_confirmation(screen: pygame.Surface) -> None:
    """Draw a quit confirmation dialog"""
    # Semi-transparent overlay
    overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(128)  # 50% transparency
    screen.blit(overlay, (0, 0))

    # Dialog box
    dialog_width = 300
    dialog_height = 120
    dialog_x = config.WINDOW_WIDTH // 2 - dialog_width // 2
    dialog_y = config.WINDOW_HEIGHT // 2 - dialog_height // 2

    # Draw dialog background
    pygame.draw.rect(screen, (50, 50, 50), (dialog_x, dialog_y, dialog_width, dialog_height), border_radius=10)
    pygame.draw.rect(screen, (200, 200, 200), (dialog_x, dialog_y, dialog_width, dialog_height), 2, border_radius=10)

    # Dialog title
    title_font = pygame.font.Font(config.FONT_NAME, 24)
    title_surf = title_font.render("Return to Menu?", True, (255, 255, 255))
    title_rect = title_surf.get_rect(center=(config.WINDOW_WIDTH // 2, dialog_y + 25))
    screen.blit(title_surf, title_rect)

    # Dialog message
    msg_font = pygame.font.Font(config.FONT_NAME, 16)
    msg_surf = msg_font.render("Return to main menu?", True, (220, 220, 220))
    msg_rect = msg_surf.get_rect(center=(config.WINDOW_WIDTH // 2, dialog_y + 45))
    screen.blit(msg_surf, msg_rect)

    # Instructions
    instr_surf = msg_font.render("Y/Enter: Yes  |  N/Esc: No", True, (180, 180, 180))
    instr_rect = instr_surf.get_rect(center=(config.WINDOW_WIDTH // 2, dialog_y + 65))
    screen.blit(instr_surf, instr_rect)

    # Yes button
    yes_button = pygame.Rect(dialog_x + 40, dialog_y + 85, 80, 25)
    pygame.draw.rect(screen, (70, 130, 70), yes_button, border_radius=5)
    pygame.draw.rect(screen, (150, 200, 150), yes_button, 1, border_radius=5)
    yes_text = msg_font.render("Yes (Y)", True, (255, 255, 255))
    yes_text_rect = yes_text.get_rect(center=yes_button.center)
    screen.blit(yes_text, yes_text_rect)

    # No button
    no_button = pygame.Rect(dialog_x + 180, dialog_y + 85, 80, 25)
    pygame.draw.rect(screen, (130, 70, 70), no_button, border_radius=5)
    pygame.draw.rect(screen, (200, 150, 150), no_button, 1, border_radius=5)
    no_text = msg_font.render("No (N)", True, (255, 255, 255))
    no_text_rect = no_text.get_rect(center=no_button.center)
    screen.blit(no_text, no_text_rect)

    # Store button positions for click detection (will be used in event handling)
    global yes_button_rect, no_button_rect
    yes_button_rect = yes_button
    no_button_rect = no_button


# Global variables for button click detection
yes_button_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
no_button_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)


def main() -> None:
    pygame.init()
    try:
        screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption("Vector Balls")
        clock = pygame.time.Clock()

        previous_settings: Optional[Settings] = None

        while True:
            # Setup form with defaults
            settings = settings_form_screen(screen, clock, previous_settings)
            game = Game(screen, settings)

            running = True
            paused = False
            restart_to_menu = False
            show_quit_confirm = False

            while running and not restart_to_menu:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r and game.game_over:
                            restart_to_menu = True
                        elif event.key == pygame.K_SPACE:
                            if not show_quit_confirm:  # Don't pause if quit dialog is active
                                paused = not paused
                        elif event.key == pygame.K_ESCAPE:
                            if not game.game_over:
                                show_quit_confirm = True
                                paused = True  # Pause the game while showing dialog
                        elif show_quit_confirm:
                            if event.key == pygame.K_y or event.key == pygame.K_RETURN:  # Yes, return to menu
                                restart_to_menu = True
                                show_quit_confirm = False
                            elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:  # No, continue
                                show_quit_confirm = False
                                paused = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if show_quit_confirm:
                            # Handle quit confirmation dialog clicks
                            mouse_x, mouse_y = event.pos
                            dialog_x = config.WINDOW_WIDTH // 2 - 150
                            dialog_y = config.WINDOW_HEIGHT // 2 - 60

                            # Yes button
                            yes_button = pygame.Rect(dialog_x + 40, dialog_y + 85, 80, 25)
                            # No button
                            no_button = pygame.Rect(dialog_x + 180, dialog_y + 85, 80, 25)

                            if yes_button.collidepoint(mouse_x, mouse_y):
                                restart_to_menu = True
                                show_quit_confirm = False
                            elif no_button.collidepoint(mouse_x, mouse_y):
                                show_quit_confirm = False
                                paused = False
                        elif game.game_over:
                            # Handle stats screen exit button clicks
                            mouse_x, mouse_y = event.pos
                            exit_button_rect = pygame.Rect(config.WINDOW_WIDTH // 2 - 60, config.WINDOW_HEIGHT - 50, 120, 35)
                            if exit_button_rect.collidepoint(mouse_x, mouse_y):
                                pygame.quit()
                                sys.exit(0)

                dt = clock.tick(config.FPS) / 1000.0

                if not paused:
                    game.update(dt)

                screen.fill(config.BACKGROUND_COLOR)
                game.draw()

                # Draw pause indicator
                if paused and not show_quit_confirm:
                    draw_text_center(screen, "Paused (Space to resume)", pygame.font.Font(config.FONT_NAME, 28), (255, 255, 255), (config.WINDOW_WIDTH // 2, 40))

                # Draw quit confirmation dialog
                if show_quit_confirm:
                    draw_quit_confirmation(screen)

                pygame.display.flip()

            if not running:
                break
            previous_settings = settings
    finally:
        pygame.quit()
        # Ensure clean exit for some environments
        sys.exit(0)


if __name__ == "__main__":
    main()


