"""État global du jeu : agrège le labyrinthe et les entités."""

import pygame

from .maze import Maze
from .pacman import Pacman
from .ghost import Blinky, Pinky, Inky, Clyde

TILE_PX = 16   # case d'origine en pixels-modèle
HALF    = TILE_PX // 2  # cellule de la grille doublée = hitbox des entités


def _center(col, row):
    """Centre pixel du passage d'origine (col, row) dans l'espace modèle."""
    return (col * 2 + 1.5) * HALF, (row * 2 + 1.5) * HALF


class Game:
    """Conteneur de l'état de jeu (modèle racine)."""

    def __init__(self, config):
        self.config = config
        # seed depuis la config ; PERFECT=False -> couloirs Pac-Man.
        self.maze = Maze(
            cols=config["width"],
            rows=config["height"],
            seed=config.get("seed", 42),
            perfect=False,
        )
        self.lives = config.get("lives", 3)

        # Pré-calcul des rectangles de murs (grille doublée → pixels-modèle).
        self.maze.wall_rects = [
            pygame.Rect(gx * HALF, gy * HALF, HALF, HALF)
            for gy in range(self.maze.height)
            for gx in range(self.maze.width)
            if self.maze.grid[gy][gx] == 1
        ]

        pac_col = config["width"] // 2 - (1 if config["width"] % 2 == 0 else 0)
        pacman_speed = config.get("pacman_speed", 1.0)
        self.pacman = Pacman(*_center(pac_col, config["height"] // 2),
                             speed=pacman_speed)

        ghost_speed = config.get("ghost_speed", 1.0)
        cx, cy = config["width"] - 1, config["height"] - 1
        blinky = Blinky(*_center(cx, cy), speed=ghost_speed, direction="up")
        inky   = Inky(*_center(cx,  0),   speed=ghost_speed, direction="down")
        inky.blinky = blinky
        self.ghosts = [
            blinky,
            Pinky(*_center(0,  cy),  speed=ghost_speed, direction="up"),
            inky,
            Clyde(*_center(0,   0),  speed=ghost_speed, direction="down"),
        ]
        self.score = 0
        self.level = 1

        # Timer de niveau (en ms). Le temps n'avance que pendant update() :
        # la pause (qui ne fait pas d'update) gèle donc naturellement le timer.
        self.max_time = config.get("level_max_time", 90)
        self.elapsed_ms = 0
        self._last_now = None

    @property
    def time_remaining(self):
        """Secondes restantes sur le niveau (jamais négatif)."""
        return max(0, self.max_time - self.elapsed_ms // 1000)

    def entities(self):
        return [self.pacman, *self.ghosts]

    def update(self, now):
        self._tick_timer(now)
        self.pacman.update(self.maze)
        for ghost in self.ghosts:
            ghost.update(self.maze, self.pacman)
        self._collect()

    def _tick_timer(self, now):
        """Accumule le temps écoulé, en clampant les sauts (pause, lag)."""
        if self._last_now is None:
            self._last_now = now
        dt = now - self._last_now
        self._last_now = now
        # Clamp : après une pause ou un freeze, le delta peut être énorme.
        self.elapsed_ms += max(0, min(dt, 100))

    def _collect(self):
        pac = self.pacman
        gx = int(pac.x // HALF)
        gy = int(pac.y // HALF)
        cell = (gx, gy)
        if cell in self.maze.pacgums:
            self.maze.pacgums.discard(cell)
            self.score += self.config.get("points_per_pacgum", 10)
        elif cell in self.maze.super_pacgums:
            self.maze.super_pacgums.discard(cell)
            self.score += self.config.get("points_per_super_pacgum", 50)
