import pygame
from collections import deque

_DELTA = {
    "right": ( 1,  0),
    "left":  (-1,  0),
    "up":    ( 0, -1),
    "down":  ( 0,  1),
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


def _bfs(maze, col, row, forbidden_dir, target_col, target_row):
    """Chemin le plus court de (col,row) vers la cible via BFS.

    forbidden_dir : direction interdite au premier pas (règle anti-demi-tour).
    Retourne la liste de cases (col,row) du début jusqu'à la cible,
    ou une liste avec uniquement le départ si la cible est inatteignable.
    """
    if col == target_col and row == target_row:
        return [(col, row)]

    parent = {(col, row): None}
    queue = deque()

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
            cur = (c, r)
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
    def __init__(self, x=0.0, y=0.0, tile_px=16, speed=2.0, direction="right", color="red"):
        self.x = float(x)
        self.y = float(y)
        self._tile = tile_px
        self.size = tile_px // 2
        self.speed = speed
        self.direction = direction
        self.color = color
        self.frightened = False

    @property
    def col(self):
        return int(self.x // self._tile)

    @property
    def row(self):
        return int(self.y // self._tile)

    @property
    def rect(self):
        h = self.size // 2
        return pygame.Rect(int(self.x) - h, int(self.y) - h, self.size, self.size)

    def _tile_center(self):
        """Centre pixel de la case courante (col, row)."""
        return (self.col * 2 + 1.5) * self.size, (self.row * 2 + 1.5) * self.size

    def _can_enter(self, direction, maze):
        """True si la cellule voisine dans `direction` est accessible."""
        dcol, drow = _WALL_OFFSET[direction]
        gx = self.col * 2 + dcol
        gy = self.row * 2 + drow
        return not maze.is_wall(gx, gy)

    def _target(self, pacman):
        """Case cible du fantôme (par défaut : la case de Pac-Man)."""
        return pacman.col, pacman.row

    def _clamp_target(self, col, row, maze):
        """Ramène (col, row) dans les bornes valides de la grille de passages."""
        max_col = maze.width  // 2 - 1
        max_row = maze.height // 2 - 1
        return max(0, min(col, max_col)), max(0, min(row, max_row))

    def compute_path(self, maze, pacman):
        """Chemin le plus court vers la cible via BFS."""
        tc, tr = self._clamp_target(*self._target(pacman), maze)
        return _bfs(maze, self.col, self.row, _OPPOSITE[self.direction], tc, tr)

    def _choose_direction(self, maze, target_col, target_row):
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

    def update(self, maze, pacman):
        dx, dy = _DELTA[self.direction]
        cx, cy = self._tile_center()

        # Snap sur l'axe perpendiculaire (évite la dérive de couloir)
        if dx:
            self.y = cy
        else:
            self.x = cx

        pos   = self.x if dx else self.y
        t_c   = cx     if dx else cy
        ahead = (dx > 0 and t_c >= pos) or (dx < 0 and t_c <= pos) \
             or (dy > 0 and t_c >= pos) or (dy < 0 and t_c <= pos)
        dist  = abs(t_c - pos)

        if ahead and dist <= self.speed:
            # Snap au centre de case
            if dx:
                self.x = t_c
            else:
                self.y = t_c
            remaining = self.speed - dist

            # Décision seulement quand le fantôme peut effectivement bouger.
            # Si remaining == 0 (dist == speed exactement), on reporte à la
            # frame suivante où dist == 0 et remaining == speed > 0.
            # Sans ce garde, deux décisions consécutives depuis le même centre
            # peuvent libérer la direction opposée et provoquer un demi-tour.
            if remaining > 0:
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
            self.x += dx * self.speed
            self.y += dy * self.speed


class Blinky(Ghost):
    def __init__(self, x=0.0, y=0.0, tile_px=16, speed=2.0, direction="right"):
        super().__init__(x, y, tile_px, speed, direction, color="red")


class Pinky(Ghost):
    def __init__(self, x=0.0, y=0.0, tile_px=16, speed=2.0, direction="right"):
        super().__init__(x, y, tile_px, speed, direction, color="pink")

    def _target(self, pacman):
        dc, dr = _DELTA[pacman.direction]
        return pacman.col + 2 * dc, pacman.row + 2 * dr


class Inky(Ghost):
    def __init__(self, x=0.0, y=0.0, tile_px=16, speed=2.0, direction="right"):
        super().__init__(x, y, tile_px, speed, direction, color="cyan")
        self.blinky = None  # set externally after construction

    def _target(self, pacman):
        if self.blinky is None:
            return pacman.col, pacman.row
        return (2 * pacman.col - self.blinky.col,
                2 * pacman.row - self.blinky.row)


class Clyde(Ghost):
    def __init__(self, x=0.0, y=0.0, tile_px=16, speed=2.0, direction="right"):
        super().__init__(x, y, tile_px, speed, direction, color="orange")
