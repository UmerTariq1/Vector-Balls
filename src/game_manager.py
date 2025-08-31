"""
Game manager for Vector Balls - handles the main game loop and orchestration.
"""

from __future__ import annotations

import sys
from typing import Optional

import pygame

import src.config as config
from src.game import Game
from src.settings import Settings
from src.ui import settings_form_screen, draw_quit_confirmation, draw_text_center, yes_button_rect, no_button_rect


class GameManager:
    """Manages the overall game flow and main loop."""

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption("Vector Balls")
        self.clock = pygame.time.Clock()
        self.previous_settings: Optional[Settings] = None

    def run(self) -> None:
        """Main game loop that handles setup screen and game sessions."""
        try:
            while True:
                # Setup form with defaults
                settings = settings_form_screen(self.screen, self.clock, self.previous_settings)
                game = Game(self.screen, settings)

                self._run_game_session(game, settings)

                # Update previous settings for next session
                self.previous_settings = settings
        finally:
            pygame.quit()
            # Ensure clean exit for some environments
            sys.exit(0)

    def _run_game_session(self, game: Game, settings: Settings) -> None:
        """Run a single game session until it ends or user returns to menu."""
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

            dt = self.clock.tick(config.FPS) / 1000.0

            if not paused:
                game.update(dt)

            self.screen.fill(config.BACKGROUND_COLOR)
            game.draw()

            # Draw pause indicator
            if paused and not show_quit_confirm:
                draw_text_center(self.screen, "Paused (Space to resume)", pygame.font.Font(config.FONT_NAME, 28), (255, 255, 255), (config.WINDOW_WIDTH // 2, 40))

            # Draw quit confirmation dialog
            if show_quit_confirm:
                draw_quit_confirmation(self.screen)

            pygame.display.flip()

        if not running:
            pygame.quit()
            sys.exit(0)
