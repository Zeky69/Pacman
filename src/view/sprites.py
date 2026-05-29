import pygame
from .settings import SMALL_BLOCK, LARGE_BLOCK

class SpriteSheet:
    def __init__(self, filename):
        """Charge l'image principale en mémoire."""
        try:
            self.sheet = pygame.image.load(filename).convert()
        except pygame.error as e:
            print(f"Erreur : Impossible de charger l'image {filename}")
            raise SystemExit(e)

    def _extract(self, x, y, width, height, scale):
        """Fonction interne qui découpe la surface et l'agrandit."""
        
        image = pygame.Surface((width, height)).convert()
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        image.set_colorkey((0, 0, 0))
        
        if scale != 1:
            image = pygame.transform.scale(image, (width * scale, height * scale))
            
        return image

    def get_small_sprite(self, macro_row, palette_index, col, row, scale=1):
        """
        Extrait un sprite de 8x8 pixels.
        - macro_row : La grande ligne (0 à 3)
        - palette_index : Le tableau/couleur (0 à 4, de gauche à droite)
        - col, row : Les coordonnées dans le tableau
        - scale : Facteur d'agrandissement (ex: 2 ou 3)
        """
        start_y = macro_row * 186
        
        start_x = palette_index * (SMALL_BLOCK['block_w'] + SMALL_BLOCK['block_margin'])

        x = start_x + SMALL_BLOCK['cell_margin'] + col * (SMALL_BLOCK['cell_w'] + SMALL_BLOCK['cell_margin'])
        y = start_y + SMALL_BLOCK['cell_margin'] + row * (SMALL_BLOCK['cell_h'] + SMALL_BLOCK['cell_margin'])

        return self._extract(x, y, SMALL_BLOCK['cell_w'], SMALL_BLOCK['cell_h'], scale)

    def get_large_sprite(self, macro_row, palette_index, col, row, scale=1):
        """
        Extrait un sprite de 16x16 pixels.
        - macro_row : La grande ligne (0 à 3)
        - palette_index : Le tableau/couleur (0 à 4, de gauche à droite)
        - col, row : Les coordonnées dans le tableau
        - scale : Facteur d'agrandissement (ex: 2 ou 3)
        """
        start_y = 82 + (macro_row * 186)
        
        section_w = LARGE_BLOCK['block_w'] + LARGE_BLOCK['palette_w'] + LARGE_BLOCK['block_margin']
        start_x = palette_index * section_w

        x = start_x + LARGE_BLOCK['cell_margin'] + col * (LARGE_BLOCK['cell_w'] + LARGE_BLOCK['cell_margin'])
        y = start_y + LARGE_BLOCK['cell_margin'] + row * (LARGE_BLOCK['cell_h'] + LARGE_BLOCK['cell_margin'])

        return self._extract(x, y, LARGE_BLOCK['cell_w'], LARGE_BLOCK['cell_h'], scale)