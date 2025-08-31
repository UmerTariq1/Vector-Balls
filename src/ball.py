"""
Ball entity for Vector Balls. Each ball owns a set of boundary-anchored lines.
"""

from __future__ import annotations

import math
import random
from typing import List

import pygame
from pygame.math import Vector2

import src.config as config
from src.physics import reflect
from src.settings import Settings


class Ball:
    """Represents a moving ball with lines attached to fixed boundary points."""

    def __init__(
        self,
        ball_id: int,
        position: Vector2,
        velocity: Vector2,
        color: tuple[int, int, int],
        radius: int = config.BALL_RADIUS,
        *,
        settings: Settings,
    ) -> None:
        self.id: int = ball_id
        self.position: Vector2 = Vector2(position)
        self.velocity: Vector2 = Vector2(velocity)
        self.color = color
        self.radius: int = int(radius)
        # Lines are stored as fixed anchor points on the boundary (Vector2)
        self.lines: List[Vector2] = []
        # Cooldown to prevent multiple line spawns on one sustained contact
        self._boundary_cooldown: float = 0.0
        # Settings snapshot relevant to this ball
        self._lines_per_hit: int = settings.lines_per_boundary_hit
        self._boundary_speed_increase: float = settings.boundary_collision_speed_increase
        # Stats
        self.lines_removed_by_me: int = 0
        self.my_lines_removed_by_others: int = 0

    def add_random_lines(self, boundary_center: Vector2, boundary_radius: float, count: int) -> None:
        """Attach 'count' new lines anchored at random boundary points.
        The anchor points never move after being created.
        """
        for _ in range(count):
            angle = random.random() * math.tau
            anchor = Vector2(
                boundary_center.x + math.cos(angle) * boundary_radius,
                boundary_center.y + math.sin(angle) * boundary_radius,
            )
            self.lines.append(anchor)

    def update(self, dt: float, boundary_center: Vector2, boundary_radius: float) -> None:
        """Advance physics, handle boundary collisions and line generation."""
        # Integrate position
        self.position += self.velocity * dt

        # Tick cooldown timer
        if self._boundary_cooldown > 0.0:
            self._boundary_cooldown = max(0.0, self._boundary_cooldown - dt)

        # Check boundary collision
        offset: Vector2 = self.position - boundary_center
        dist_from_center: float = offset.length()
        if dist_from_center + self.radius > boundary_radius:
            # Compute surface normal and place ball just inside boundary
            normal = offset.normalize() if dist_from_center != 0 else Vector2(1.0, 0.0)
            self.position = boundary_center + normal * (boundary_radius - self.radius)

            # Reflect velocity and boost speed
            self.velocity = reflect(self.velocity, normal)
            speed = self.velocity.length()
            if speed > 0:
                speed = min(speed + self._boundary_speed_increase, config.MAX_SPEED)
                self.velocity.scale_to_length(speed)

            # Spawn new lines if cooldown expired
            if self._boundary_cooldown <= 0.0:
                self.add_random_lines(boundary_center, boundary_radius, self._lines_per_hit)
                self._boundary_cooldown = config.BOUNDARY_BOUNCE_COOLDOWN

    def draw(self, surface: pygame.Surface) -> None:
        """Render the ball and its lines."""
        # Slightly lighter line color for readability
        line_color = tuple(min(255, int(c * 0.85 + 255 * 0.15)) for c in self.color)
        for anchor in self.lines:
            pygame.draw.line(surface, line_color, anchor, self.position, config.LINE_WIDTH)

        pygame.draw.circle(surface, self.color, (int(self.position.x), int(self.position.y)), self.radius)


