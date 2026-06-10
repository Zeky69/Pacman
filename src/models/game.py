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
        self.godmode = bool(config.get("godmode", False))
        self.ghost_freeze = False
        self.speed_boost = False
        self._base_pacman_speed = pacman_speed

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
        if not self.ghost_freeze:
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
        size = self.pacman.size
        h = size // 2

        # Construire la liste complète des positions pixel à tester :
        # snap points + toutes les cases de la grille doublée entre eux.
        check_px = []
        positions = self.pacman.cells_visited
        for i, (px, py) in enumerate(positions):
            gx = int(px // HALF)
            gy = int(py // HALF)
            if i > 0:
                pgx = int(positions[i - 1][0] // HALF)
                pgy = int(positions[i - 1][1] // HALF)
                if pgx != gx:
                    for cx in range(min(pgx, gx), max(pgx, gx) + 1):
                        check_px.append(((cx + 0.5) * HALF, py))
                elif pgy != gy:
                    for cy in range(min(pgy, gy), max(pgy, gy) + 1):
                        check_px.append((px, (cy + 0.5) * HALF))
            check_px.append((px, py))

        for px, py in check_px:
            pac_rect      = pygame.Rect(int(px) - h, int(py) - h, size, size)
            pac_kill_rect = pac_rect.inflate(-h, -h)
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
                    if not self.godmode and pac_kill_rect.colliderect(ghost.rect):
                        self.pacman.die(now)
                        return  # une seule mort par frame

    def _try_collect(self, cell, now):
        if cell in self.maze.pacgums:
            self.maze.pacgums.discard(cell)
            self.score += self.config.get("points_per_pacgum", 10)
        elif cell in self.maze.super_pacgums:
            self.maze.super_pacgums.discard(cell)
            self.score += self.config.get("points_per_super_pacgum", 50)
            until = now + FRIGHTENED_DURATION
            for ghost in self.ghosts:
                ghost.frighten(until)

    def _collect(self, now=0):
        # Itérer TOUTES les cases de la grille doublée traversées ce frame,
        # y compris les cases de passage (gx/gy pairs) entre deux centres.
        seen = set()
        positions = self.pacman.cells_visited
        for i, (px, py) in enumerate(positions):
            gx = int(px // HALF)
            gy = int(py // HALF)
            if i > 0:
                pgx = int(positions[i - 1][0] // HALF)
                pgy = int(positions[i - 1][1] // HALF)
                if pgx != gx:  # déplacement horizontal : interpoler gx
                    for cx in range(min(pgx, gx), max(pgx, gx) + 1):
                        cell = (cx, gy)
                        if cell not in seen:
                            seen.add(cell)
                            self._try_collect(cell, now)
                elif pgy != gy:  # déplacement vertical : interpoler gy
                    for cy in range(min(pgy, gy), max(pgy, gy) + 1):
                        cell = (gx, cy)
                        if cell not in seen:
                            seen.add(cell)
                            self._try_collect(cell, now)
            cell = (gx, gy)
            if cell not in seen:
                seen.add(cell)
                self._try_collect(cell, now)
