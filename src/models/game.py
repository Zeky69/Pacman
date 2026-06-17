"""État global du jeu : agrège le labyrinthe et les entités."""

import random
from typing import Any, Optional

import pygame

from .maze import Maze
from .pacman import Pacman
from .ghost import Blinky, Pinky, Inky, Clyde, FRIGHTENED_DURATION

TILE_PX = 16
HALF = TILE_PX // 2

DEFAULT_LEVEL_COUNT = 10
GHOST_SPEEDUP_PER_LEVEL = 0.1
FRIGHTENED_REDUCTION_PER_LEVEL = 500  # ms de moins par niveau
READY_MS = 2000

# Fruits bonus (comme Pac-Man original) : (nom, points).
# L'index correspond à level-1, clampé au dernier élément.
FRUIT_TABLE: list[tuple[str, int]] = [
    ("cherry",     100),
    ("strawberry", 300),
    ("orange",     500),
    ("orange",     500),
    ("apple",      700),
    ("apple",      700),
    ("grape",     1000),
    ("grape",     1000),
    ("galaxian",  2000),
    ("galaxian",  2000),
]
FRUIT_DURATION = 9000   # ms de présence du fruit sur le plateau
FRUIT_TRIGGER_1 = 0.30  # ratio de gommes mangées → 1re apparition
FRUIT_TRIGGER_2 = 0.70  # ratio de gommes mangées → 2e apparition


def _center(col: int, row: int) -> tuple[float, float]:
    """Centre pixel du passage d'origine (col, row) dans l'espace modèle."""
    return (col * 2 + 1.5) * HALF, (row * 2 + 1.5) * HALF


class Game:
    """Conteneur de l'état de jeu (modèle racine)."""

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.lives = config.get("lives", 3)
        self.score = 0
        self.level = 1
        self.max_level = config.get("level_count", DEFAULT_LEVEL_COUNT)
        self.score_popups: list[dict[str, Any]] = []  # [{x, y, value, until}]
        self.invincible = bool(config.get("invincible", False))
        self.ghost_freeze = False
        self.speed_boost = False
        self.show_paths = False
        self.show_targets = False

        # Vitesses de base ; les fantômes accélèrent à chaque niveau.
        self._pacman_speed: float = config.get("pacman_speed", 1.0)
        self._base_ghost_speed: float = config.get("ghost_speed", 1.0)
        self._seed: int = config.get("seed", 42)

        self.fruit: Optional[dict[str, Any]] = None
        self._fruit_spawned = 0
        self._total_dots = 0

        self._build_maze()
        self._reset_fruit_state()
        self._spawn_entities()

        # Timer de niveau (en ms). Le temps n'avance que pendant update() :
        # la pause (qui ne fait pas d'update) gèle donc naturellement le timer.
        self.max_time: int = config.get("level_max_time", 90)
        self.elapsed_ms = 0
        self._last_now: Optional[int] = None
        self.ready = True
        self._ready_until: Optional[int] = None

    def _ghost_speed(self) -> float:
        """Vitesse des fantômes au niveau courant (accélère par palier)."""
        factor = 1 + GHOST_SPEEDUP_PER_LEVEL * (self.level - 1)
        return self._base_ghost_speed * factor

    def _build_maze(self) -> None:
        """(Re)construit le labyrinthe du niveau + ses rectangles de murs.

        Niveau 1 : graine fixe de la config (42 par défaut), tableau
        reproductible. Niveaux suivants : graine aléatoire, donc un labyrinthe
        différent à chaque fois. PERFECT=False donne les couloirs Pac-Man.
        """
        seed = self._seed if self.level == 1 else random.randint(0, 2**31 - 1)
        self.maze = Maze(
            cols=self.config["width"],
            rows=self.config["height"],
            seed=seed,
            perfect=False,
        )
        # Pré-calcul des rectangles de murs (grille doublée → pixels-modèle).
        self.maze.wall_rects = [
            pygame.Rect(gx * HALF, gy * HALF, HALF, HALF)
            for gy in range(self.maze.height)
            for gx in range(self.maze.width)
            if self.maze.grid[gy][gx] == 1
        ]

    def _spawn_entities(self) -> None:
        """(Re)place Pac-Man et les fantômes à leurs positions de départ."""
        config = self.config
        pac_col = config["width"] // 2 - (1 if config["width"] % 2 == 0 else 0)
        effective_speed = self._pacman_speed * (2.5 if self.speed_boost else 1.0)
        self.pacman = Pacman(*_center(pac_col, config["height"] // 2),
                             speed=effective_speed)

        gs = self._ghost_speed()
        cx, cy = config["width"] - 1, config["height"] - 1
        blinky = Blinky(*_center(cx, cy), speed=gs, direction="up")
        inky = Inky(*_center(cx, 0), speed=gs, direction="down")
        inky.blinky = blinky
        self.ghosts = [
            blinky,
            Pinky(*_center(0,  cy),  speed=gs, direction="up"),
            inky,
            Clyde(*_center(0,   0),  speed=gs, direction="down"),
        ]

    def _reset_fruit_state(self) -> None:
        self.fruit = None
        self._fruit_spawned = 0
        all_cells = self.maze.pacgums | self.maze.super_pacgums
        self._total_dots = len(all_cells)
        # Case atteignable la plus proche du centre (comme les gums)
        if all_cells:
            tgx = self.config["width"] // 2 * 2 + 1
            tgy = self.config["height"] // 2 * 2 + 1
            cgx, cgy = min(all_cells, key=lambda p: (p[0] - tgx) ** 2 + (p[1] - tgy) ** 2)
            self._fruit_pos: tuple[float, float] = (
                (cgx + 0.5) * HALF, (cgy + 0.5) * HALF
            )
        else:
            self._fruit_pos = _center(self.config["width"] // 2, self.config["height"] // 2)

    def _maybe_spawn_fruit(self, now: int) -> None:
        if self._fruit_spawned >= 2 or self._total_dots == 0 or self.fruit is not None:
            return
        eaten = self._total_dots - len(self.maze.pacgums) - len(self.maze.super_pacgums)
        ratio = eaten / self._total_dots
        trigger = FRUIT_TRIGGER_1 if self._fruit_spawned == 0 else FRUIT_TRIGGER_2
        if ratio >= trigger:
            idx = min(self.level - 1, len(FRUIT_TABLE) - 1)
            name, pts = FRUIT_TABLE[idx]
            fx, fy = self._fruit_pos
            self.fruit = {"x": fx, "y": fy, "name": name, "points": pts,
                          "until": now + FRUIT_DURATION}
            self._fruit_spawned += 1

    def _check_fruit_collection(self, now: int) -> None:
        if self.fruit is None:
            return
        if now >= self.fruit["until"]:
            self.fruit = None
            return
        dx = self.pacman.x - self.fruit["x"]
        dy = self.pacman.y - self.fruit["y"]
        if (dx * dx + dy * dy) ** 0.5 < self.pacman.size:
            pts = self.fruit["points"]
            self.score += pts
            self.score_popups.append({
                "x": self.fruit["x"], "y": self.fruit["y"],
                "value": pts, "until": now + 1500,
            })
            self.fruit = None

    def skip_level(self) -> None:
        """Vide toutes les gommes : l'update détectera level_cleared et avancera."""
        self.maze.pacgums.clear()
        self.maze.super_pacgums.clear()

    def _advance_level(self, now: int) -> None:
        """Passe au niveau suivant : nouveau tableau, fantômes plus rapides.

        Le score et les vies sont conservés ; le timer du niveau repart à zéro.
        """
        self.level += 1
        self._build_maze()
        self._reset_fruit_state()
        self._spawn_entities()
        self.score_popups = []
        self.elapsed_ms = 0
        self._last_now = now
        self.ready = True
        self._ready_until = None

    @property
    def time_remaining(self) -> int:
        """Secondes restantes sur le niveau (jamais négatif)."""
        return max(0, self.max_time - self.elapsed_ms // 1000)

    def entities(self) -> list[Any]:
        return [self.pacman, *self.ghosts]

    @property
    def game_over(self) -> bool:
        return self.lives <= 0 and not self.pacman.dead

    @property
    def level_cleared(self) -> bool:
        """Toutes les gommes du tableau courant ont été mangées."""
        return not self.maze.pacgums and not self.maze.super_pacgums

    @property
    def won(self) -> bool:
        """Victoire finale : le dernier niveau vient d'être terminé."""
        return self.level_cleared and self.level >= self.max_level

    def update(self, now: int = 0) -> None:
        if self.ready:
            if self._ready_until is None:
                self._ready_until = now + READY_MS
            if now < self._ready_until:
                return
            self.ready = False

        self._tick_timer(now)
        self.score_popups = [p for p in self.score_popups if p['until'] > now]

        if self.pacman.dead:
            if now >= self.pacman.dead_until:
                self._do_respawn()
            return  # gel complet pendant la mort

        if self.elapsed_ms >= self.max_time * 1000:
            self.pacman.die(now)
            return

        self.pacman.update(self.maze)
        if not self.ghost_freeze:
            for ghost in self.ghosts:
                ghost.update(self.maze, self.pacman, now)
        else:
            for ghost in self.ghosts:
                ghost.tick_timers(now)
        self._collect(now)
        self._maybe_spawn_fruit(now)
        self._check_fruit_collection(now)
        self._check_ghost_collisions(now)

        # Tableau vidé : on enchaîne le niveau suivant tant qu'il en reste.
        # Le dernier niveau laisse `won` passer à True (géré par la scène).
        if (not self.pacman.dead and self.level_cleared
                and self.level < self.max_level):
            self._advance_level(now)

    def _do_respawn(self) -> None:
        self.lives -= 1
        self.elapsed_ms = 0
        self._last_now = None
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
        self.ready = True
        self._ready_until = None

    def _tick_timer(self, now: int) -> None:
        """Accumule le temps écoulé, en clampant les sauts (pause, lag)."""
        if self._last_now is None:
            self._last_now = now
        dt = now - self._last_now
        self._last_now = now
        # Clamp : après une pause ou un freeze, le delta peut être énorme.
        self.elapsed_ms += max(0, min(dt, 100))

    def _check_ghost_collisions(self, now: int) -> None:
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
            pac_rect = pygame.Rect(int(px) - h, int(py) - h, size, size)
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
                    if not self.invincible and pac_kill_rect.colliderect(ghost.rect):
                        self.pacman.die(now)
                        return  # une seule mort par frame

    def _try_collect(self, cell: tuple[int, int], now: int) -> None:
        if cell in self.maze.pacgums:
            self.maze.pacgums.discard(cell)
            self.score += self.config.get("points_per_pacgum", 10)
        elif cell in self.maze.super_pacgums:
            self.maze.super_pacgums.discard(cell)
            self.score += self.config.get("points_per_super_pacgum", 50)
            reduction = FRIGHTENED_REDUCTION_PER_LEVEL * (self.level - 1)
            duration = max(1000, FRIGHTENED_DURATION - reduction)
            for ghost in self.ghosts:
                ghost.frighten(now + duration)

    def _collect(self, now: int = 0) -> None:
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
