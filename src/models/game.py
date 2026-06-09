"""État global du jeu : agrège le labyrinthe et les entités."""

import pygame

from .maze import Maze
from .pacman import Pacman
from .ghost import Blinky, Pinky, Inky, Clyde, FRIGHTENED_DURATION, EATEN_DURATION

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

    def entities(self):
        return [self.pacman, *self.ghosts]

    def update(self, now=0):
        self.pacman.update(self.maze)
        for ghost in self.ghosts:
            ghost.update(self.maze, self.pacman, now)
        self._collect(now)
        self._check_ghost_collisions(now)

    def _check_ghost_collisions(self, now):
        fps = self.config.get("fps", 60)
        pac_rect = self.pacman.rect
        for ghost in self.ghosts:
            if ghost.eaten:
                continue
            if pac_rect.colliderect(ghost.rect):
                if ghost.frightened:
                    ghost.eat(now, fps)
                    self.score += self.config.get("points_per_ghost", 200)

    def _collect(self, now=0):
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
            until = now + FRIGHTENED_DURATION
            for ghost in self.ghosts:
                ghost.frighten(until)
