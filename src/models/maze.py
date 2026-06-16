"""Modèle du labyrinthe : généré dynamiquement via `mazegenerator`.

Le package `MazeGenerator` (lib/mazegenerator-2.0.2) renvoie une grille 2D
d'entiers où chaque cellule encode ses murs sur 4 bits (N=1, E=2, S=4, W=8).
On la transforme en une grille "doublée" où 1 = mur et 0 = passage, ce qui
permet collisions et auto-tiling.
"""

from __future__ import annotations
import sys
from collections import deque
from typing import TYPE_CHECKING, Optional

from mazegenerator import MazeGenerator

if TYPE_CHECKING:
    import pygame

# Bits de direction d'un mur (identiques à l'encodage de MazeGenerator).
NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8


class Maze:
    """Grille de murs du labyrinthe (1 = mur, 0 = passage)."""

    def __init__(self, cols: int = 20, rows: int = 20,
                 seed: int = 0, perfect: bool = False) -> None:
        # MazeGenerator creuse le labyrinthe par un DFS *récursif* : la
        # profondeur peut atteindre le nombre de cellules (cols*rows). On
        # relève temporairement la limite de récursion pour couvrir la grille
        # (avec marge), puis on la restaure — sinon un grand labyrinthe lève
        # RecursionError. La taille est déjà bornée en amont (config), donc la
        # limite reste modeste (aucun risque de débordement de pile C).
        needed = cols * rows + 100
        old_limit = sys.getrecursionlimit()
        if needed > old_limit:
            sys.setrecursionlimit(needed)
        try:
            generator = MazeGenerator(size=(cols, rows), seed=seed, perfect=perfect)
        finally:
            sys.setrecursionlimit(old_limit)
        self.entry = generator.maze_entry          # (col, row) d'entrée
        self.exit = generator.maze_exit            # (col, row) de sortie
        self.shortest_path = generator.shortest_path

        self.grid = self._build_wall_grid(generator.maze)
        self.height = len(self.grid)
        self.width = len(self.grid[0])

        self.wall_rects: list[pygame.Rect] = []
        reachable = self._reachable_cells()
        self.pacgums: set[tuple[int, int]] = {
            (gx, gy)
            for gy in range(self.height)
            for gx in range(self.width)
            if self.grid[gy][gx] == 0 and (gx, gy) in reachable
        }
        self.super_pacgums: set[tuple[int, int]] = self._pick_super_pacgums()
        self.pacgums -= self.super_pacgums

    @staticmethod
    def _build_wall_grid(code_grid: list[list[int]]) -> list[list[int]]:
        """Convertit la grille de codes en grille doublée (murs = 1)."""
        h = len(code_grid)
        w = len(code_grid[0])
        grid = [[1] * (w * 2 + 1) for _ in range(h * 2 + 1)]

        for y in range(h):
            for x in range(w):
                cell = code_grid[y][x]
                gx, gy = x * 2 + 1, y * 2 + 1

                grid[gy][gx] = 0
                if not (cell & NORTH) and y > 0:
                    grid[gy - 1][gx] = 0
                if not (cell & EAST) and x < w - 1:
                    grid[gy][gx + 1] = 0
                if not (cell & SOUTH) and y < h - 1:
                    grid[gy + 1][gx] = 0
                if not (cell & WEST) and x > 0:
                    grid[gy][gx - 1] = 0
        return grid

    def _reachable_cells(self) -> set[tuple[int, int]]:
        """BFS depuis l'entrée — exclut les cases enclavées (ex: le '42' de MazeGenerator)."""
        start_gx = self.entry[0] * 2 + 1
        start_gy = self.entry[1] * 2 + 1
        visited: set[tuple[int, int]] = set()
        q: deque[tuple[int, int]] = deque([(start_gx, start_gy)])
        visited.add((start_gx, start_gy))
        while q:
            cx, cy = q.popleft()
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height \
                        and self.grid[ny][nx] == 0 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    q.append((nx, ny))
        return visited

    def _pick_super_pacgums(self) -> set[tuple[int, int]]:
        """4 cells les plus proches des coins (une par coin, sans doublon)."""
        corners = [
            (0, 0),
            (self.width - 1, 0),
            (0, self.height - 1),
            (self.width - 1, self.height - 1),
        ]
        result: set[tuple[int, int]] = set()
        available = set(self.pacgums)
        for cx, cy in corners:
            if not available:
                break
            best = min(available, key=lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2)
            result.add(best)
            available.discard(best)
        return result

    def cell_to_grid(self, col: int, row: int) -> tuple[int, int]:
        """Case d'origine (col, row) -> index (gx, gy) de son centre dans la grille doublée."""
        return col * 2 + 1, row * 2 + 1

    def is_wall(self, gx: int, gy: int) -> bool:
        """True si la case (gx, gy) est un mur (hors-grille = mur)."""
        if 0 <= gx < self.width and 0 <= gy < self.height:
            return self.grid[gy][gx] == 1
        return True

    def corner_mask(self, cx: int, cy: int) -> int:
        """Masque 4 bits des murs autour du coin (cx, cy) : NW NE SW SE."""
        nw = self.is_wall(cx - 1, cy - 1)
        ne = self.is_wall(cx,     cy - 1)
        sw = self.is_wall(cx - 1, cy)
        se = self.is_wall(cx,     cy)
        return (nw << 3) | (ne << 2) | (sw << 1) | se

    def border_type(self, cx: int, cy: int) -> Optional[str]:
        """Renvoie le type de bordure ('TL', 'T', 'L'...) ou None si intérieur."""
        on_t = cy == 1
        on_b = cy == self.height - 1
        on_l = cx == 1
        on_r = cx == self.width - 1

        if on_t and on_l:
            return "TL"
        if on_t and on_r:
            return "TR"
        if on_b and on_l:
            return "BL"
        if on_b and on_r:
            return "BR"
        if on_t:
            return "T"
        if on_b:
            return "B"
        if on_l:
            return "L"
        if on_r:
            return "R"
        return None
