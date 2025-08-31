"""
Vector Balls - A minimal 2D physics game using pygame.

Run:
  python main.py
"""

from src.game_manager import GameManager


def main() -> None:
    """Main entry point for the Vector Balls game."""
    game_manager = GameManager()
    game_manager.run()


if __name__ == "__main__":
    main()

