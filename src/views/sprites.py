"""Chargement de la sprite-sheet et extraction des sprites individuels."""

import pygame

from .settings import (
    SMALL_BLOCK, LARGE_BLOCK,
    MACRO_ROW_HEIGHT, LARGE_BLOCK_Y_OFFSET,
)


class SpriteSheet:
    """Découpe une image (sprite-sheet) en sprites réutilisables.

    Les sprites extraits sont mis en cache : chaque (taille, position, scale)
    n'est découpé et redimensionné qu'une seule fois.
    """

    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert()
        except pygame.error as e:
            print(f"Erreur : impossible de charger l'image {filename}")
            raise SystemExit(e)
        self._cache = {}

    # -- Extraction bas niveau ------------------------------------------------
    def _extract(self, x, y, width, height, scale):
        """Découpe une zone de la planche et l'agrandit selon `scale`."""
        image = pygame.Surface((width, height)).convert()
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        image.set_colorkey((0, 0, 0))
        if scale != 1:
            image = pygame.transform.scale(image, (width * scale, height * scale))
        return image

    @staticmethod
    def _cell_position(start_x, start_y, col, row, cfg):
        """Position (x, y) en pixels d'une cellule (col, row) dans un bloc."""
        x = start_x + cfg["cell_margin"] + col * (cfg["cell_w"] + cfg["cell_margin"])
        y = start_y + cfg["cell_margin"] + row * (cfg["cell_h"] + cfg["cell_margin"])
        return x, y

    # -- API publique ---------------------------------------------------------
    def get_small_sprite(self, macro_row, palette_index, col, row, scale=1):
        """Extrait un sprite 8x8 (mis en cache)."""
        key = ("small", macro_row, palette_index, col, row, scale)
        if key not in self._cache:
            start_y = macro_row * MACRO_ROW_HEIGHT
            start_x = palette_index * (SMALL_BLOCK["block_w"] + SMALL_BLOCK["block_margin"])
            x, y = self._cell_position(start_x, start_y, col, row, SMALL_BLOCK)
            self._cache[key] = self._extract(
                x, y, SMALL_BLOCK["cell_w"], SMALL_BLOCK["cell_h"], scale
            )
        return self._cache[key]

    def get_large_sprite(self, macro_row, palette_index, col, row, scale=1):
        """Extrait un sprite 16x16 (mis en cache)."""
        key = ("large", macro_row, palette_index, col, row, scale)
        if key not in self._cache:
            start_y = LARGE_BLOCK_Y_OFFSET + macro_row * MACRO_ROW_HEIGHT
            section_w = (LARGE_BLOCK["block_w"] + LARGE_BLOCK["palette_w"]
                         + LARGE_BLOCK["block_margin"])
            start_x = palette_index * section_w
            x, y = self._cell_position(start_x, start_y, col, row, LARGE_BLOCK)
            self._cache[key] = self._extract(
                x, y, LARGE_BLOCK["cell_w"], LARGE_BLOCK["cell_h"], scale
            )
        return self._cache[key]
