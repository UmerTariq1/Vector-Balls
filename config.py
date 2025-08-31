"""
Global configuration for the Vector Balls game.
Edit these values to tweak gameplay and presentation.
"""

from __future__ import annotations

# --- Window / Rendering ---
WINDOW_WIDTH: int = 1000
WINDOW_HEIGHT: int = 1000
FPS: int = 60

BACKGROUND_COLOR = (15, 18, 22)
BOUNDARY_COLOR = (230, 230, 230)
BOUNDARY_LINE_WIDTH: int = 6
LINE_WIDTH: int = 3

# --- Arena (circular boundary) ---
BOUNDARY_MARGIN: int = 40  # pixels from window edge
BOUNDARY_CENTER = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
BOUNDARY_RADIUS: int = int((min(WINDOW_WIDTH, WINDOW_HEIGHT) // 2 - BOUNDARY_MARGIN) * 0.75)

# --- Gameplay / Balls ---
NUM_BALLS: int = 6
BALL_RADIUS: int = 12

# Initial random speed range (pixels/second)
INITIAL_SPEED_MIN: float = 160.0
INITIAL_SPEED_MAX: float = 240.0

# Cap on absolute speed to keep simulation stable
MAX_SPEED: float = 700.0

# Lines setup
INITIAL_LINES_PER_BALL: int = 3
LINES_PER_BOUNDARY_HIT: int = 3

# --- Collision speed tuning (key configurable values) ---
# Multiply both balls' speeds by (1 + factor) after a ball-ball collision
BALL_COLLISION_SPEED_INCREASE_FACTOR: float = 0.12

# Add this many pixels/second to a ball's speed on boundary hit
BOUNDARY_COLLISION_SPEED_INCREASE: float = 25.0

# Cooldown to avoid re-triggering boundary logic on the same contact (seconds)
BOUNDARY_BOUNCE_COOLDOWN: float = 0.12

# Grace period at game start where no lines can be removed (seconds)
GRACE_PERIOD_DURATION: float = 1.0

# --- Visuals ---
# A simple palette; more balls will reuse colors modulo this list.
COLORS = [
    (231, 76, 60),   # red
    (34, 139, 34),   # forest green (darker than original green)
    (52, 152, 219),  # blue
    (241, 196, 15),  # yellow
    (255, 20, 147),  # magenta
    (64, 224, 208),  # turquoise (different from cyan)
    (255, 140, 0),   # orange
    (138, 43, 226),  # purple
    (255, 215, 0),   # gold (brighter alternative to yellow)
    (255, 105, 180), # hot pink
    (25, 25, 112),   # navy blue (darker than original blue)
    (128, 0, 128),   # dark magenta (deeper purple alternative)
]

FONT_NAME: str = "freesansbold.ttf"


