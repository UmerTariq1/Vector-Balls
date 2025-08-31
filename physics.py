"""
Physics and geometry helpers for Vector Balls.

This module is intentionally small and focused:
- vector reflection for boundary bounces
- circle-circle collision resolution (equal mass elastic)
- circle-segment intersection test for line removal
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from pygame.math import Vector2

import config

# Color names mapped to RGB tuples for closest match (same as config.py COLORS)
COLOR_NAMES = {
    "Red": (231, 76, 60),
    "Forest Green": (34, 139, 34),
    "Blue": (52, 152, 219),
    "Yellow": (241, 196, 15),
    "Magenta": (255, 20, 147),
    "Turquoise": (64, 224, 208),
    "Orange": (255, 140, 0),
    "Purple": (138, 43, 226),
    "Gold": (255, 215, 0),
    "Hot Pink": (255, 105, 180),
    "Navy Blue": (25, 25, 112),
    "Dark Magenta": (128, 0, 128),
}

def get_color_name(rgb: tuple[int, int, int]) -> str:
    """Find the closest color name to the given RGB tuple using Euclidean distance."""
    min_dist = float('inf')
    closest_name = "Unknown"
    for name, color_rgb in COLOR_NAMES.items():
        dist = sum((a - b) ** 2 for a, b in zip(rgb, color_rgb))
        if dist < min_dist:
            min_dist = dist
            closest_name = name
    return closest_name


if TYPE_CHECKING:
    from ball import Ball


def reflect(velocity: Vector2, normal: Vector2) -> Vector2:
    """Reflect a velocity vector about a unit normal.

    normal must be normalized. The result is v - 2*(v·n)*n.
    """
    if normal.length_squared() == 0:
        return velocity
    n = normal.normalize()
    return velocity - 2.0 * velocity.dot(n) * n


def resolve_ball_ball_collision(a: "Ball", b: "Ball", speed_increase_factor: float) -> None:
    """Resolve an elastic collision between two equal-mass balls, then
    increase their speeds by the given multiplicative factor.

    The function also separates overlapping balls to avoid sticky collisions.
    """
    delta: Vector2 = b.position - a.position
    distance: float = delta.length()
    min_distance: float = a.radius + b.radius

    # If centers overlap exactly, choose an arbitrary small separation vector
    if distance == 0:
        delta = Vector2(1.0, 0.0)
        distance = 1.0

    # Separate if overlapping
    overlap: float = min_distance - distance
    if overlap > 0:
        correction: Vector2 = delta.normalize() * (overlap / 2.0 + 0.1)
        a.position -= correction
        b.position += correction

    # Compute collision response (equal masses, perfectly elastic)
    n: Vector2 = (b.position - a.position)
    if n.length_squared() == 0:
        return
    n = n.normalize()
    t: Vector2 = Vector2(-n.y, n.x)

    a_vn = a.velocity.dot(n)
    a_vt = a.velocity.dot(t)
    b_vn = b.velocity.dot(n)
    b_vt = b.velocity.dot(t)

    # Swap normal components, keep tangential components
    a_vn_prime = b_vn
    b_vn_prime = a_vn

    a.velocity = a_vn_prime * n + a_vt * t
    b.velocity = b_vn_prime * n + b_vt * t

    # Speed boost after collision
    if a.velocity.length_squared() > 0:
        new_speed_a = min(a.velocity.length() * (1.0 + speed_increase_factor), config.MAX_SPEED)
        if new_speed_a > 0:
            a.velocity.scale_to_length(new_speed_a)

    if b.velocity.length_squared() > 0:
        new_speed_b = min(b.velocity.length() * (1.0 + speed_increase_factor), config.MAX_SPEED)
        if new_speed_b > 0:
            b.velocity.scale_to_length(new_speed_b)


def distance_point_to_segment(point: Vector2, seg_a: Vector2, seg_b: Vector2) -> float:
    """Return the shortest distance from a point to a line segment AB.
    Uses projection and clamps to segment extents.
    """
    ab: Vector2 = seg_b - seg_a
    ap: Vector2 = point - seg_a
    ab_len_sq: float = ab.length_squared()
    if ab_len_sq == 0:
        # Degenerate segment
        return ap.length()
    t = max(0.0, min(1.0, ap.dot(ab) / ab_len_sq))
    closest: Vector2 = seg_a + ab * t
    return (point - closest).length()


def circle_intersects_segment(center: Vector2, radius: float, seg_a: Vector2, seg_b: Vector2) -> bool:
    """Check if a circle intersects a line segment.
    True if the minimum distance from circle center to the segment is <= radius.
    """
    return distance_point_to_segment(center, seg_a, seg_b) <= radius


