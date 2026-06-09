import pygame

_DELTA = {
    "right": ( 1,  0),
    "left":  (-1,  0),
    "up":    ( 0, -1),
    "down":  ( 0,  1),
}

# Offsets dans la grille doublée pour tester le mur entre la case courante
# et la case voisine dans chaque direction.
_WALL_OFFSET = {
    "right": ( 2,  1),
    "left":  ( 0,  1),
    "down":  ( 1,  2),
    "up":    ( 1,  0),
}


DEATH_DURATION = 1500  # ms de gel après la mort avant le respawn


class Pacman:
    def __init__(self, x=0.0, y=0.0, tile_px=16, speed=2.0, direction="right"):
        self.x = float(x)
        self.y = float(y)
        self._tile = tile_px        # case d'origine en pixels (= 16)
        self.size = tile_px // 2    # cellule grille doublée (= 8) — hitbox
        self.speed = speed
        self.direction = direction
        self.queued_direction = None
        self.alive = True
        self.spawn_x = float(x)
        self.spawn_y = float(y)
        self.spawn_direction = direction
        self.dead = False
        self.dead_until = 0
        self.moved = False
        self.cells_visited = []  # positions (x, y) franchies ce frame, dans l'ordre

    # ── position dans la grille d'origine ────────────────────────────────────

    @property
    def col(self):
        return int(self.x // self._tile)

    @property
    def row(self):
        return int(self.y // self._tile)

    @property
    def next_col(self):
        if self.direction == "right": return self.col + 1
        if self.direction == "left":  return self.col - 1
        return self.col

    @property
    def next_row(self):
        if self.direction == "down": return self.row + 1
        if self.direction == "up":   return self.row - 1
        return self.row

    @property
    def rect(self):
        h = self.size // 2
        return pygame.Rect(int(self.x) - h, int(self.y) - h, self.size, self.size)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _tile_center(self):
        """Centre pixel de la case courante (col, row)."""
        return (self.col * 2 + 1.5) * self.size, (self.row * 2 + 1.5) * self.size

    def _can_enter(self, direction, maze):
        """True si la cellule voisine dans `direction` est accessible."""
        dcol, drow = _WALL_OFFSET[direction]
        gx = self.col * 2 + dcol
        gy = self.row * 2 + drow
        return not maze.is_wall(gx, gy)

    # ── mort / respawn ────────────────────────────────────────────────────────

    def die(self, now):
        self.dead = True
        self.dead_until = now + DEATH_DURATION

    def respawn(self):
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.direction = self.spawn_direction
        self.queued_direction = None
        self.dead = False
        self.dead_until = 0

    # ── mouvement (style arcade original) ────────────────────────────────────

    def update(self, maze):
        start_x, start_y = self.x, self.y
        self.cells_visited = [(self.x, self.y)]  # position de départ du frame
        if self.dead:
            self.moved = False
            return
        dx, dy = _DELTA[self.direction]

        # 1. Demi-tour immédiat (sans attendre le centre de case).
        if self.queued_direction:
            qdx, qdy = _DELTA[self.queued_direction]
            if (dx and qdx == -dx) or (dy and qdy == -dy):
                self.direction = self.queued_direction
                self.queued_direction = None

        # 2. Déplacement case par case : on s'arrête TOUJOURS au prochain centre
        #    devant nous, qu'on soit avant ou après le centre de la case courante.
        budget = self.speed
        while budget > 0:
            dx, dy = _DELTA[self.direction]
            cx, cy = self._tile_center()

            # Snap sur l'axe perpendiculaire.
            if dx:
                self.y = cy
            else:
                self.x = cx

            # Prochain centre devant : si on a déjà dépassé le centre de la case
            # courante, viser le centre de la case suivante dans notre direction.
            pos = self.x if dx else self.y
            t_c = cx     if dx else cy
            d   = dx + dy  # ±1
            if d > 0 and pos > t_c + 1e-6:
                t_c += self._tile
            elif d < 0 and pos < t_c - 1e-6:
                t_c -= self._tile
            dist = abs(t_c - pos)

            if dist <= budget:
                # Snap au prochain centre.
                if dx:
                    self.x = t_c
                else:
                    self.y = t_c
                budget -= dist
                self.cells_visited.append((self.x, self.y))

                if budget > 0:
                    # Tentative de changement de direction au centre.
                    if self.queued_direction and self._can_enter(self.queued_direction, maze):
                        self.direction = self.queued_direction
                        self.queued_direction = None

                    dx, dy = _DELTA[self.direction]
                    cx, cy = self._tile_center()
                    if dx:
                        self.y = cy
                    else:
                        self.x = cx

                    if self._can_enter(self.direction, maze):
                        step = min(budget, float(self._tile))
                        self.x += dx * step
                        self.y += dy * step
                        budget -= step
                    else:
                        budget = 0  # bloqué.
            else:
                # Budget insuffisant pour atteindre le prochain centre.
                self.x += dx * budget
                self.y += dy * budget
                budget = 0

        # 3. Sécurité : empêche de sortir de la carte.
        self.x = max(0.0, min(self.x, maze.width  * self.size - 1.0))
        self.y = max(0.0, min(self.y, maze.height * self.size - 1.0))

        # Position finale toujours présente.
        if not self.cells_visited or self.cells_visited[-1] != (self.x, self.y):
            self.cells_visited.append((self.x, self.y))

        self.moved = (self.x != start_x or self.y != start_y)
