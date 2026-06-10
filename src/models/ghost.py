import random
from typing import Any, Optional

import pygame
from collections import deque

FRIGHTENED_DURATION = 5000
FRIGHTENED_BLINK = 1500
EATEN_DURATION = 3000

_DELTA = {
    "right": (1, 0),
    "left": (-1, 0),
    "up": (0, -1),
    "down": (0, 1),
}

_WALL_OFFSET = {
    "right": (2, 1),
    "left":  (0, 1),
    "down":  (1, 2),
    "up":    (1, 0),
}

_OPPOSITE = {
    "right": "left",
    "left":  "right",
    "up":    "down",
    "down":  "up",
}

# Ordre de priorité en cas d'égalité de distance : Haut > Gauche > Bas > Droite
_PRIORITY = ["up", "left", "down", "right"]

_DIR_FROM_DELTA = {v: k for k, v in _DELTA.items()}


def _bfs(
    maze: Any, col: int, row: int,
    forbidden_dir: Optional[str], target_col: int, target_row: int
) -> list[tuple[int, int]]:
    """Chemin le plus court de (col,row) vers la cible via BFS.

    forbidden_dir : direction interdite au premier pas (règle anti-demi-tour).
    Retourne la liste de cases (col,row) du début jusqu'à la cible,
    ou une liste avec uniquement le départ si la cible est inatteignable.
    """
    if col == target_col and row == target_row:
        return [(col, row)]

    parent: dict[tuple[int, int], Optional[tuple[int, int]]] = {(col, row): None}
    queue: deque[tuple[int, int]] = deque()

    for d in _PRIORITY:
        if d == forbidden_dir:
            continue
        gx = col * 2 + _WALL_OFFSET[d][0]
        gy = row * 2 + _WALL_OFFSET[d][1]
        if maze.is_wall(gx, gy):
            continue
        dc, dr = _DELTA[d]
        nc, nr = col + dc, row + dr
        if (nc, nr) not in parent:
            parent[(nc, nr)] = (col, row)
            queue.append((nc, nr))

    while queue:
        c, r = queue.popleft()
        if c == target_col and r == target_row:
            path = []
            cur: Optional[tuple[int, int]] = (c, r)
            while cur is not None:
                path.append(cur)
                cur = parent[cur]
            path.reverse()
            return path
        for d in _PRIORITY:
            dc, dr = _DELTA[d]
            nc, nr = c + dc, r + dr
            if (nc, nr) not in parent:
                gx = c * 2 + _WALL_OFFSET[d][0]
                gy = r * 2 + _WALL_OFFSET[d][1]
                if not maze.is_wall(gx, gy):
                    parent[(nc, nr)] = (c, r)
                    queue.append((nc, nr))

    return [(col, row)]


class Ghost:
    def __init__(
        self, x: float = 0.0, y: float = 0.0, tile_px: int = 16,
        speed: float = 2.0, direction: str = "right", color: str = "red"
    ) -> None:
        self.x = float(x)
        self.y = float(y)
        self._tile = tile_px
        self.size = tile_px // 2
        self.speed = speed
        self.direction = direction
        self.color = color
        self.frightened = False
        self.frightened_until = 0  # timestamp absolu (ms) de fin d'état effrayé
        self.eaten = False
        self.eaten_until = 0    # timestamp absolu (ms) de fin d'état eaten
        self.eaten_speed = speed  # vitesse calculée au moment du eat()
        self.spawn_x = float(x)
        self.spawn_y = float(y)
        self.spawn_direction = direction
        self._pending_reverse = False

    @property
    def col(self) -> int:
        return int(self.x // self._tile)

    @property
    def row(self) -> int:
        return int(self.y // self._tile)

    @property
    def rect(self) -> pygame.Rect:
        h = self.size // 2
        return pygame.Rect(int(self.x) - h, int(self.y) - h, self.size, self.size)

    def _tile_center(self) -> tuple[float, float]:
        """Centre pixel de la case courante (col, row)."""
        return (self.col * 2 + 1.5) * self.size, (self.row * 2 + 1.5) * self.size

    def _can_enter(self, direction: str, maze: Any) -> bool:
        """True si la cellule voisine dans `direction` est accessible."""
        dcol, drow = _WALL_OFFSET[direction]
        gx = self.col * 2 + dcol
        gy = self.row * 2 + drow
        return not maze.is_wall(gx, gy)

    def _target(self, pacman: Any) -> tuple[int, int]:
        """Case cible du fantôme (par défaut : la case de Pac-Man)."""
        return pacman.col, pacman.row

    def frighten(self, until: int) -> None:
        """Active le mode effrayé jusqu'au timestamp `until` (ms)."""
        if not self.eaten:
            self.frightened = True
            self.frightened_until = until
            self._pending_reverse = True

    def is_blinking(self, now: int) -> bool:
        """True pendant la phase de clignotement (fin du mode effrayé)."""
        return self.frightened and now >= self.frightened_until - FRIGHTENED_BLINK

    def compute_spawn_path(self, maze: Any) -> list[tuple[int, int]]:
        """Chemin BFS depuis la position courante jusqu'au spawn."""
        spawn_col = int(self.spawn_x // self._tile)
        spawn_row = int(self.spawn_y // self._tile)
        return _bfs(maze, self.col, self.row, _OPPOSITE[self.direction], spawn_col, spawn_row)

    def eat(self, now: int, fps: int = 60) -> None:
        """Pac-Man mange ce fantôme : il rentre à son spawn en mode 'eaten'."""
        self.frightened = False
        self.frightened_until = 0
        self.eaten = True
        self.eaten_until = now + EATEN_DURATION
        self._eaten_fps = fps
        self.eaten_speed = self.speed  # recalculé à chaque centre de case dans update()

    def _clamp_target(self, col: int, row: int, maze: Any) -> tuple[int, int]:
        """Ramène (col, row) dans les bornes valides de la grille de passages."""
        max_col = maze.width // 2 - 1
        max_row = maze.height // 2 - 1
        return max(0, min(col, max_col)), max(0, min(row, max_row))

    def compute_path(self, maze: Any, pacman: Any) -> list[tuple[int, int]]:
        """Chemin le plus court vers la cible via BFS."""
        tc, tr = self._clamp_target(*self._target(pacman), maze)
        return _bfs(maze, self.col, self.row, _OPPOSITE[self.direction], tc, tr)

    def _choose_direction(self, maze: Any, target_col: int, target_row: int) -> str:
        """Premier pas du chemin BFS vers la cible (sans demi-tour)."""
        path = _bfs(maze, self.col, self.row, _OPPOSITE[self.direction],
                    target_col, target_row)
        if len(path) >= 2:
            dc = path[1][0] - path[0][0]
            dr = path[1][1] - path[0][1]
            return _DIR_FROM_DELTA[(dc, dr)]
        # BFS n'a pas trouvé de chemin : toute direction valide sauf demi-tour.
        opposite = _OPPOSITE[self.direction]
        for d in _PRIORITY:
            if d != opposite and self._can_enter(d, maze):
                return d
        return opposite  # cul-de-sac : demi-tour en dernier recours

    def _choose_random_direction(self, maze: Any) -> str:
        """Direction aléatoire valide à l'intersection (sans demi-tour)."""
        opposite = _OPPOSITE[self.direction]
        valid = [d for d in _PRIORITY if d != opposite and self._can_enter(d, maze)]
        if valid:
            return random.choice(valid)
        return opposite  # cul-de-sac : demi-tour contraint

    def update(self, maze: Any, pacman: Any, now: int = 0) -> None:
        # Expiration de l'état effrayé
        if self.frightened and now > 0 and now >= self.frightened_until:
            self.frightened = False
            self.frightened_until = 0

        # Expiration de l'état eaten : snap au spawn et retour à la normale
        if self.eaten and now > 0 and now >= self.eaten_until:
            self.eaten = False
            self.eaten_until = 0
            self.x = self.spawn_x
            self.y = self.spawn_y
            self.direction = self.spawn_direction

        spd = self.eaten_speed if self.eaten else self.speed

        dx, dy = _DELTA[self.direction]
        cx, cy = self._tile_center()

        # Snap sur l'axe perpendiculaire (évite la dérive de couloir)
        if dx:
            self.y = cy
        else:
            self.x = cx

        pos = self.x if dx else self.y
        t_c = cx if dx else cy

        # Prochain centre devant : corriger si on a déjà dépassé le centre courant.
        d = dx + dy
        if d > 0 and pos > t_c + 1e-6:
            t_c += self._tile
        elif d < 0 and pos < t_c - 1e-6:
            t_c -= self._tile
        dist = abs(t_c - pos)

        if dist <= spd:
            # Snap au centre de case
            if dx:
                self.x = t_c
            else:
                self.y = t_c
            remaining = spd - dist

            # Décision seulement quand le fantôme peut effectivement bouger.
            # Si remaining == 0 (dist == speed exactement), on reporte à la
            # frame suivante où dist == 0 et remaining == speed > 0.
            # Sans ce garde, deux décisions consécutives depuis le même centre
            # peuvent libérer la direction opposée et provoquer un demi-tour.
            if remaining > 0:
                if self.eaten:
                    spawn_col = int(self.spawn_x // self._tile)
                    spawn_row = int(self.spawn_y // self._tile)
                    target_col, target_row = self._clamp_target(spawn_col, spawn_row, maze)
                    # Recalculer la vitesse à chaque case pour arriver exactement à temps
                    spawn_path = _bfs(maze, self.col, self.row,
                                      _OPPOSITE[self.direction], spawn_col, spawn_row)
                    remaining_steps = len(spawn_path) - 1
                    remaining_ms = self.eaten_until - now
                    if remaining_steps > 0 and remaining_ms > 0:
                        remaining_frames = remaining_ms * self._eaten_fps / 1000
                        self.eaten_speed = remaining_steps * self._tile / remaining_frames
                    spd = self.eaten_speed
                    self.direction = self._choose_direction(maze, target_col, target_row)
                elif self.frightened:
                    if self._pending_reverse:
                        self._pending_reverse = False
                        opposite = _OPPOSITE[self.direction]
                        if self._can_enter(opposite, maze):
                            self.direction = opposite
                        else:
                            self.direction = self._choose_random_direction(maze)
                    else:
                        self.direction = self._choose_random_direction(maze)
                else:
                    target_col, target_row = self._clamp_target(*self._target(pacman), maze)
                    self.direction = self._choose_direction(maze, target_col, target_row)
                dx, dy = _DELTA[self.direction]

                # Snap perp. pour la nouvelle direction
                cx, cy = self._tile_center()
                if dx:
                    self.y = cy
                else:
                    self.x = cx

            if self._can_enter(self.direction, maze):
                self.x += dx * remaining
                self.y += dy * remaining
        else:
            self.x += dx * spd
            self.y += dy * spd

        # Sécurité : empêche de sortir de la carte.
        self.x = max(0.0, min(self.x, maze.width * self.size - 1.0))
        self.y = max(0.0, min(self.y, maze.height * self.size - 1.0))


class Blinky(Ghost):
    def __init__(
        self, x: float = 0.0, y: float = 0.0, tile_px: int = 16,
        speed: float = 2.0, direction: str = "right"
    ) -> None:
        super().__init__(x, y, tile_px, speed, direction, color="red")


class Pinky(Ghost):
    def __init__(
        self, x: float = 0.0, y: float = 0.0, tile_px: int = 16,
        speed: float = 2.0, direction: str = "right"
    ) -> None:
        super().__init__(x, y, tile_px, speed, direction, color="pink")

    def _target(self, pacman: Any) -> tuple[int, int]:
        dc, dr = _DELTA[pacman.direction]
        return pacman.col + 1 * dc, pacman.row + 1 * dr


class Inky(Ghost):
    def __init__(
        self, x: float = 0.0, y: float = 0.0, tile_px: int = 16,
        speed: float = 2.0, direction: str = "right"
    ) -> None:
        super().__init__(x, y, tile_px, speed, direction, color="cyan")
        self.blinky: Optional[Ghost] = None

    def _target(self, pacman: Any) -> tuple[int, int]:
        if self.blinky is None:
            return pacman.col, pacman.row
        return (2 * pacman.col - self.blinky.col,
                2 * pacman.row - self.blinky.row)


class Clyde(Ghost):
    FLEE_RADIUS = 2

    def __init__(
        self, x: float = 0.0, y: float = 0.0, tile_px: int = 16,
        speed: float = 2.0, direction: str = "right"
    ) -> None:
        super().__init__(x, y, tile_px, speed, direction, color="orange")

    def _target(self, pacman: Any) -> tuple[int, int]:
        dc = pacman.col - self.col
        dr = pacman.row - self.row
        dist = (dc * dc + dr * dr) ** 0.5
        if dist <= self.FLEE_RADIUS:
            return 2 * self.col - pacman.col, 2 * self.row - pacman.row
        return pacman.col, pacman.row
