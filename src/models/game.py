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
        self.maze = Maze(cols=config["width"], rows=config["height"])

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
        self.ghosts = [
            Blinky(*_center(cx, cy), speed=ghost_speed, direction="up"),
            Pinky(*_center(0,  cy),  speed=ghost_speed, direction="up"),
            Inky(*_center(cx,  0),   speed=ghost_speed, direction="down"),
            Clyde(*_center(0,   0),  speed=ghost_speed, direction="down"),
        ]
        self.score = 0

    def entities(self):
        return [self.pacman, *self.ghosts]

    def update(self):
        self.pacman.update(self.maze)
        for ghost in self.ghosts:
            ghost.update(self.maze, self.pacman)
        self._collect()

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
