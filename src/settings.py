from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

import src.config as config


Color = Tuple[int, int, int]


@dataclass
class Settings:
    """Runtime-tunable game settings collected from the pre-game setup UI."""

    num_balls: int = config.NUM_BALLS
    lines_per_boundary_hit: int = config.LINES_PER_BOUNDARY_HIT
    ball_collision_speed_increase_factor: float = config.BALL_COLLISION_SPEED_INCREASE_FACTOR
    boundary_collision_speed_increase: float = config.BOUNDARY_COLLISION_SPEED_INCREASE
    boundary_radius_ratio: float = 0.8  # 0.3 .. 1.0

    # One unique color per ball; provided by setup UI
    colors: List[Color] = field(default_factory=list)


