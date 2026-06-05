"""Modèle du labyrinthe : généré dynamiquement via `mazegenerator`.

Le package `MazeGenerator` (lib/mazegenerator-2.0.2) renvoie une grille 2D
d'entiers où chaque cellule encode ses murs sur 4 bits (N=1, E=2, S=4, W=8).
On la transforme en une grille "doublée" où 1 = mur et 0 = passage, ce qui
permet collisions et auto-tiling.
"""

from mazegenerator import MazeGenerator

# Bits de direction d'un mur (identiques à l'encodage de MazeGenerator).
NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8


class Maze:
    """Grille de murs du labyrinthe (1 = mur, 0 = passage)."""

    def __init__(self, cols=20, rows=20, seed=0, perfect=False):
        generator = MazeGenerator(size=(cols, rows), seed=seed, perfect=perfect)
        self.entry = generator.maze_entry          # (col, row) d'entrée
        self.exit = generator.maze_exit            # (col, row) de sortie
        self.shortest_path = generator.shortest_path

        self.grid = self._build_wall_grid(generator.maze)
        self.height = len(self.grid)
        self.width = len(self.grid[0])

    @staticmethod
    def _build_wall_grid(code_grid):
        """Convertit la grille de codes en grille doublée (murs = 1)."""
        h = len(code_grid)
        w = len(code_grid[0])
        grid = [[1] * (w * 2 + 1) for _ in range(h * 2 + 1)]

        for y in range(h):
            for x in range(w):
                cell = code_grid[y][x]
                gx, gy = x * 2 + 1, y * 2 + 1

                grid[gy][gx] = 0  # le centre de la cellule est toujours un passage
                if not (cell & NORTH) and y > 0:     grid[gy - 1][gx] = 0
                if not (cell & EAST) and x < w - 1:   grid[gy][gx + 1] = 0
                if not (cell & SOUTH) and y < h - 1:  grid[gy + 1][gx] = 0
                if not (cell & WEST) and x > 0:       grid[gy][gx - 1] = 0
        return grid

    def is_wall(self, gx, gy):
        """True si la case (gx, gy) est un mur (hors-grille = mur)."""
        if 0 <= gx < self.width and 0 <= gy < self.height:
            return self.grid[gy][gx] == 1
        return False

    def corner_mask(self, cx, cy):
        """Masque 4 bits des murs autour du coin (cx, cy) : NW NE SW SE."""
        nw = self.is_wall(cx - 1, cy - 1)
        ne = self.is_wall(cx,     cy - 1)
        sw = self.is_wall(cx - 1, cy)
        se = self.is_wall(cx,     cy)
        return (nw << 3) | (ne << 2) | (sw << 1) | se

    def border_type(self, cx, cy):
        """Renvoie le type de bordure ('TL', 'T', 'L'...) ou None si intérieur."""
        on_t = cy == 1
        on_b = cy == self.height - 1
        on_l = cx == 1
        on_r = cx == self.width - 1

        if on_t and on_l: return "TL"
        if on_t and on_r: return "TR"
        if on_b and on_l: return "BL"
        if on_b and on_r: return "BR"
        if on_t: return "T"
        if on_b: return "B"
        if on_l: return "L"
        if on_r: return "R"
        return None
