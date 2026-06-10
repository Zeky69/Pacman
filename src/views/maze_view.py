"""Rendu du labyrinthe : auto-tiling des murs à partir du modèle `Maze`.

Pour chaque coin de la grille, on calcule un masque (cf. `Maze.corner_mask`)
puis on choisit la tuile à dessiner via les tables de correspondance.
"""

import pygame

from .settings import MAZE_TILE, COLORS, BORDER_MAPS, CORNER_MAP
from .sprites import FALLBACK_CORNER_MAP, FALLBACK_BORDER_MAPS


class MazeView:
    """Dessine un `Maze` en tuiles à partir d'une sprite-sheet."""

    def __init__(self, sheet, scale=4, color="blue"):
        self.scale = scale
        self.tile_size = 8 * scale
        palette_index, macro_row = COLORS[color]
        self.tile_sprites = {
            name: sheet.get_small_sprite(macro_row, palette_index, coords[0], coords[1], scale)
            for name, coords in MAZE_TILE.items()
        }
        if getattr(sheet, "_fallback", False):
            self._corner_map  = FALLBACK_CORNER_MAP
            self._border_maps = FALLBACK_BORDER_MAPS
        else:
            self._corner_map  = CORNER_MAP
            self._border_maps = BORDER_MAPS

    def _active_map(self, maze, cx, cy):
        """Table de tuiles applicable à ce coin (None hors limites)."""
        if cx == 0 or cx == maze.width or cy == 0 or cy == maze.height:
            return None
        border = maze.border_type(cx, cy)
        return self._border_maps[border] if border else self._corner_map

    def draw(self, surface, maze, offset_x=0, offset_y=0):
        """Dessine tout le labyrinthe sur `surface`."""
        half = self.tile_size // 2
        for cy in range(maze.height + 1):
            for cx in range(maze.width + 1):
                amap = self._active_map(maze, cx, cy)
                if amap is None:
                    continue
                name = amap.get(maze.corner_mask(cx, cy))
                if not name or name not in self.tile_sprites:
                    continue
                px = offset_x + cx * self.tile_size - half
                py = offset_y + cy * self.tile_size - half
                surface.blit(self.tile_sprites[name], (px, py))
