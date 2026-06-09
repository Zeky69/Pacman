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
        self.level = 1
        self.score_popups = []  # [{x, y, value, until}]

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

    @property
    def game_over(self):
        return self.lives <= 0 and not self.pacman.dead

    def update(self, now=0):
        self._tick_timer(now)
        self.score_popups = [p for p in self.score_popups if p['until'] > now]

        if self.pacman.dead:
            if now >= self.pacman.dead_until:
                self._do_respawn()
            return  # gel complet pendant la mort

        self.pacman.update(self.maze)
        for ghost in self.ghosts:
            ghost.update(self.maze, self.pacman, now)
        self._collect(now)
        self._check_ghost_collisions(now)

    def _do_respawn(self):
        self.lives -= 1
        if self.lives <= 0:
            self.pacman.dead = False  # débloquer la détection de game over
            return
        self.pacman.respawn()
        for ghost in self.ghosts:
            ghost.eaten = False
            ghost.frightened = False
            ghost.frightened_until = 0
            ghost.x = ghost.spawn_x
            ghost.y = ghost.spawn_y
            ghost.direction = ghost.spawn_direction

    def _tick_timer(self, now):
        """Accumule le temps écoulé, en clampant les sauts (pause, lag)."""
        if self._last_now is None:
            self._last_now = now
        dt = now - self._last_now
        self._last_now = now
        # Clamp : après une pause ou un freeze, le delta peut être énorme.
        self.elapsed_ms += max(0, min(dt, 100))

    def _check_ghost_collisions(self, now):
        fps = self.config.get("fps", 60)
        pac_rect = self.pacman.rect
        # Hitbox réduite (50 %) pour être tué — plus indulgente que la hitbox normale
        pac_kill_rect = pac_rect.inflate(-self.pacman.size // 2, -self.pacman.size // 2)
        for ghost in self.ghosts:
            if ghost.eaten:
                continue
            if ghost.frightened:
                if pac_rect.colliderect(ghost.rect):
                    ghost.eat(now, fps)
                    pts = self.config.get("points_per_ghost", 200)
                    self.score += pts
                    self.score_popups.append({
                        'x': ghost.x, 'y': ghost.y,
                        'value': pts, 'until': now + 1000,
                    })
            else:
                if pac_kill_rect.colliderect(ghost.rect):
                    self.pacman.die(now)
                    return  # une seule mort par frame

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
