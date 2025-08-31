"""
Game orchestration: spawns balls, runs updates, handles collisions and victory.
"""

from __future__ import annotations

import math
import random
from typing import List, Optional

import pygame
from pygame.math import Vector2

import src.config as config
import src.physics as physics
from src.ball import Ball
from src.settings import Settings


class Game:
    def __init__(self, screen: pygame.Surface, settings: Settings) -> None:
        self.screen: pygame.Surface = screen
        self.boundary_center: Vector2 = Vector2(config.BOUNDARY_CENTER)
        self.boundary_radius: float = float(config.BOUNDARY_RADIUS)
        self.font: pygame.font.Font = pygame.font.Font(config.FONT_NAME, 28)
        self.small_font: pygame.font.Font = pygame.font.Font(config.FONT_NAME, 18)
        self.settings: Settings = settings

        self.balls: List[Ball] = []
        self.all_balls: List[Ball] = []
        self.eliminated_balls: List[Ball] = []
        self.winner: Optional[Ball] = None
        self.game_over: bool = False
        self.game_start_time: Optional[float] = None  # Track when competitive game starts

        self.reset()

    def reset(self) -> None:
        self.winner = None
        self.game_over = False
        self.balls = []
        # Apply boundary size ratio from settings
        ratio = max(0.3, min(1.0, self.settings.boundary_radius_ratio))
        self.boundary_radius = float(config.BOUNDARY_RADIUS) * ratio
        self.all_balls = []
        self.eliminated_balls = []
        self.game_start_time = None  # Reset game start time
        self._spawn_balls(self.settings.num_balls)

    # --- Spawning ---
    def _spawn_balls(self, count: int) -> None:
        attempts_per_ball = 1000
        for i in range(count):
            color = self.settings.colors[i]

            position: Optional[Vector2] = None
            for _ in range(attempts_per_ball):
                # Choose a random point well inside the boundary
                r = random.uniform(0.15, 0.75) * (self.boundary_radius - config.BALL_RADIUS - 2)
                theta = random.random() * math.tau
                candidate = self.boundary_center + Vector2(math.cos(theta), math.sin(theta)) * r
                if self._position_is_free(candidate):
                    position = candidate
                    break

            if position is None:
                # Fallback to center if we couldn't place (should be rare)
                position = Vector2(self.boundary_center)

            speed = random.uniform(config.INITIAL_SPEED_MIN, config.INITIAL_SPEED_MAX)
            angle = random.random() * math.tau
            velocity = Vector2(math.cos(angle), math.sin(angle)) * speed

            b = Ball(ball_id=i, position=position, velocity=velocity, color=color, settings=self.settings)
            b.add_random_lines(self.boundary_center, self.boundary_radius, config.INITIAL_LINES_PER_BALL)
            self.balls.append(b)
            self.all_balls.append(b)

    def _position_is_free(self, pos: Vector2) -> bool:
        # Inside boundary check
        if (pos - self.boundary_center).length() + config.BALL_RADIUS > self.boundary_radius:
            return False
        # No overlap with existing balls
        for other in self.balls:
            if (pos - other.position).length() < (config.BALL_RADIUS * 2.2):
                return False
        return True

    # --- Game loop steps ---
    def update(self, dt: float) -> None:
        if self.game_over:
            return

        # Move and handle boundary interactions
        for b in self.balls:
            b.update(dt, self.boundary_center, self.boundary_radius)

        # Ball-ball collisions
        n = len(self.balls)
        for i in range(n):
            for j in range(i + 1, n):
                a = self.balls[i]
                b = self.balls[j]
                # Quick bounding check
                if (a.position - b.position).length() <= (a.radius + b.radius):
                    physics.resolve_ball_ball_collision(a, b, self.settings.ball_collision_speed_increase_factor)

        # Line interactions: any ball vs lines owned by other balls
        # Check if we're in grace period (no line removal for first 1 second)
        current_time = pygame.time.get_ticks() / 1000.0  # Convert to seconds
        if self.game_start_time is None:
            self.game_start_time = current_time

        in_grace_period = (current_time - self.game_start_time) < config.GRACE_PERIOD_DURATION

        to_eliminate: List[Ball] = []
        if not in_grace_period:  # Only allow line removal after grace period
            for moving in self.balls:
                for owner in self.balls:
                    if moving.id == owner.id:
                        continue
                    # Iterate over a copy so we can remove from the real list
                    for anchor in owner.lines.copy():
                        if physics.circle_intersects_segment(moving.position, moving.radius, anchor, owner.position):
                            owner.lines.remove(anchor)
                            moving.lines_removed_by_me += 1
                            owner.my_lines_removed_by_others += 1
                            if len(owner.lines) == 0 and owner not in to_eliminate:
                                to_eliminate.append(owner)

        # Eliminate balls with no lines
        if to_eliminate:
            for dead in to_eliminate:
                if dead in self.balls:
                    self.balls.remove(dead)
                    self.eliminated_balls.append(dead)

        # Victory check
        if len(self.balls) == 1:
            self.winner = self.balls[0]
            self.game_over = True
        elif len(self.balls) == 0:
            self.winner = None
            self.game_over = True

    def draw(self) -> None:
        # Boundary
        pygame.draw.circle(
            self.screen,
            config.BOUNDARY_COLOR,
            (int(self.boundary_center.x), int(self.boundary_center.y)),
            int(self.boundary_radius),
            config.BOUNDARY_LINE_WIDTH,
        )

        # Lines first, then balls (handled in Ball.draw)
        for b in self.balls:
            b.draw(self.screen)

        if self.game_over:
            self._draw_stats_screen()
        else:
            self._draw_overlay()
            # Show grace period countdown if active
            if hasattr(self, 'game_start_time') and self.game_start_time is not None:
                current_time = pygame.time.get_ticks() / 1000.0
                grace_remaining = config.GRACE_PERIOD_DURATION - (current_time - self.game_start_time)
                if grace_remaining > 0 and grace_remaining <= config.GRACE_PERIOD_DURATION:
                    # Draw grace period countdown
                    countdown_text = f"Peace time remaining: {grace_remaining:.1f}"
                    countdown_surf = self.font.render(countdown_text, True, (255, 255, 0))  # Yellow text
                    countdown_rect = countdown_surf.get_rect(center=(config.WINDOW_WIDTH // 2, 80))
                    self.screen.blit(countdown_surf, countdown_rect)


    # --- UI helpers ---
    def _draw_stats_screen(self) -> None:
        """Draw a clean, full-screen stats display with rankings"""
        # Clear screen with a clean background
        self.screen.fill((20, 25, 30))  # Dark blue-gray background

        center_x = config.WINDOW_WIDTH // 2

        # Title and winner announcement
        title_y = 80
        if self.winner is not None:
            # Try to render with emoji support
            try:
                emoji_font = pygame.font.SysFont("segoe ui emoji", 28)
                if not emoji_font:
                    emoji_font = pygame.font.SysFont("arial", 28)
                if not emoji_font:
                    emoji_font = self.font
                title_surf = emoji_font.render("🏆 WINNER!", True, (255, 255, 255))
            except:
                title_surf = self.font.render("WINNER!", True, (255, 255, 255))
            title_rect = title_surf.get_rect(center=(center_x, title_y))
            self.screen.blit(title_surf, title_rect)

            winner_surf = self.small_font.render(f"Ball #{self.winner.id + 1}", True, self.winner.color)
            winner_rect = winner_surf.get_rect(center=(center_x, title_y + 35))
            self.screen.blit(winner_surf, winner_rect)
        else:
            title_surf = self.font.render("Everyone Eliminated!", True, (240, 240, 240))
            title_rect = title_surf.get_rect(center=(center_x, title_y))
            self.screen.blit(title_surf, title_rect)

        # Create ranked list: winner (1st) + eliminated balls in reverse order (last eliminated = 2nd, etc.)
        ranked_balls = []
        if self.winner:
            ranked_balls.append(("🏆 1st", self.winner))
        # Add eliminated balls in reverse order (last eliminated first)
        for i, ball in enumerate(reversed(self.eliminated_balls)):
            place = len(self.eliminated_balls) - i
            if place == 1 and not self.winner:
                ranked_balls.append((f"🏆 {place}rd", ball))  # Handle case where last eliminated is 1st
            elif place == 1:
                ranked_balls.append((f"🥈 2nd", ball))
            elif place == 2:
                ranked_balls.append((f"🥉 3rd", ball))
            else:
                ranked_balls.append((f"{place}th", ball))

        # Rankings display
        rank_start_y = 150
        rank_line_height = 30
        # Try to use a system font that supports emojis, fallback to consolas
        try:
            mono = pygame.font.SysFont("segoe ui emoji", 20)  # Windows emoji font
            if not mono:
                mono = pygame.font.SysFont("apple color emoji", 20)  # macOS emoji font
            if not mono:
                mono = pygame.font.SysFont("noto color emoji", 20)  # Linux emoji font
        except:
            pass
        
        # If emoji fonts don't work, use regular font
        if not mono or mono.get_ascent() == 0:
            mono = pygame.font.SysFont("arial", 20)  # Better than consolas for unicode
            if not mono:
                mono = pygame.font.SysFont("consolas", 20)

        rank_title_surf = self.small_font.render("Final Rankings:", True, (220, 220, 220))
        rank_title_rect = rank_title_surf.get_rect(center=(center_x, rank_start_y))
        self.screen.blit(rank_title_surf, rank_title_rect)

        for i, (place_text, ball) in enumerate(ranked_balls[:5]):  # Show top 5
            rank_y = rank_start_y + 40 + i * rank_line_height

            # Draw place and ball info
            color_name = physics.get_color_name(ball.color)
            rank_text = f"{place_text} - Ball #{ball.id + 1} ({color_name})"
            rank_surf = mono.render(rank_text, True, (230, 230, 230))
            rank_rect = rank_surf.get_rect(center=(center_x, rank_y))
            self.screen.blit(rank_surf, rank_rect)

            # Draw color square next to ranking
            square_size = 20
            square_x = rank_rect.left - 30
            pygame.draw.rect(self.screen, ball.color, (square_x, rank_y - 10, square_size, square_size))

        # Detailed stats table
        stats_start_y = rank_start_y + 200
        mono_small = pygame.font.SysFont("consolas", 16)
        headers = ["Ball", "Color", "Lines Removed", "Lines Lost"]

        # Create stats data
        all_balls_stats = []
        for b in self.all_balls:
            color_name = physics.get_color_name(b.color)
            all_balls_stats.append([f"#{b.id + 1}", color_name, str(b.lines_removed_by_me), str(b.my_lines_removed_by_others)])

        if all_balls_stats:
            # Calculate column positions for better alignment
            col_widths = [60, 100, 120, 100]  # Fixed widths for each column
            table_width = sum(col_widths) + len(col_widths) * 10  # Add padding
            table_start_x = center_x - table_width // 2

            # Draw headers
            header_y = stats_start_y
            for i, header in enumerate(headers):
                col_x = table_start_x + sum(col_widths[:i]) + i * 10
                header_surf = mono_small.render(header, True, (255, 255, 0))  # Yellow headers
                self.screen.blit(header_surf, (col_x, header_y))

            # Draw separator line
            pygame.draw.line(self.screen, (150, 150, 150),
                           (table_start_x, header_y + 25),
                           (table_start_x + table_width, header_y + 25), 1)

            # Draw data rows
            row_height = 25
            for row_idx, row_data in enumerate(all_balls_stats):
                row_y = header_y + 35 + row_idx * row_height

                for col_idx, cell_data in enumerate(row_data):
                    col_x = table_start_x + sum(col_widths[:col_idx]) + col_idx * 10

                    # Special handling for ball number column
                    if col_idx == 0:
                        ball = self.all_balls[row_idx]
                        # Draw color square first
                        square_size = 16
                        pygame.draw.rect(self.screen, ball.color, (col_x, row_y - 6, square_size, square_size))
                        # Then draw ball number
                        text_surf = mono_small.render(cell_data, True, (230, 230, 230))
                        self.screen.blit(text_surf, (col_x + 22, row_y))
                    else:
                        text_surf = mono_small.render(cell_data, True, (230, 230, 230))
                        self.screen.blit(text_surf, (col_x, row_y))

        # Instructions and buttons at bottom
        instr_surf = self.small_font.render("Press R to return to setup menu", True, (200, 200, 200))
        instr_rect = instr_surf.get_rect(center=(center_x, config.WINDOW_HEIGHT - 80))
        self.screen.blit(instr_surf, instr_rect)

        # Exit button
        exit_button_rect = pygame.Rect(center_x - 60, config.WINDOW_HEIGHT - 50, 120, 35)
        pygame.draw.rect(self.screen, (140, 60, 60), exit_button_rect, border_radius=5)
        exit_text = self.small_font.render("Exit Game", True, (255, 255, 255))
        exit_text_rect = exit_text.get_rect(center=exit_button_rect.center)
        self.screen.blit(exit_text, exit_text_rect)

    def _draw_overlay(self) -> None:
        """Draw minimal overlay for in-game messages (pause, etc.)"""
        pass  # Currently no in-game overlays needed




