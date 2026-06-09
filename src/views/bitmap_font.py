"""Police bitmap issue de la planche de sprites Pac-Man.

Les glyphes (A-Z, 0-9 et quelques ponctuations : ``! " / - .``) sont extraits
du bloc de couleur choisi via ``ASCII_TILE`` + ``COLORS``. Le rendu compose
une surface en blittant les glyphes 8x8 mis à l'échelle.

Police à chasse fixe : le texte est mis en majuscules et tout caractère
inconnu laisse simplement un blanc (jamais d'erreur).
"""

import pygame

from .settings import ASCII_TILE, COLORS

GLYPH_PX = 8  # côté d'un glyphe dans la planche


class BitmapFont:
    """Rend du texte avec la police sprite de Pac-Man, dans une couleur."""

    def __init__(self, sheet, color="white", scale=4, spacing=0):
        palette_index, macro_row = COLORS[color]
        self.scale = scale
        self.cell = GLYPH_PX * scale
        self.spacing = spacing * scale
        self.height = self.cell
        self._glyphs = {
            ch: sheet.get_small_sprite(macro_row, palette_index, c, r, scale)
            for ch, (c, r) in ASCII_TILE.items()
        }

    def measure(self, text):
        """Largeur en px du texte rendu (hauteur = self.height)."""
        n = len(text)
        if n == 0:
            return 0
        return n * self.cell + (n - 1) * self.spacing

    def render(self, text):
        """Renvoie une Surface SRCALPHA contenant `text` (en majuscules)."""
        text = text.upper()
        width = max(1, self.measure(text))
        surf = pygame.Surface((width, self.height), pygame.SRCALPHA)
        step = self.cell + self.spacing
        for i, ch in enumerate(text):
            glyph = self._glyphs.get(ch)
            if glyph is not None:
                surf.blit(glyph, (i * step, 0))
        return surf

    def draw(self, surface, text, **anchor):
        """Rend `text` et le blitte selon l'ancre Rect fournie.

        `anchor` est un mot-clé de positionnement de Rect, par exemple
        ``center=(x, y)``, ``midleft=(x, y)`` ou ``topleft=(x, y)``.
        """
        img = self.render(text)
        rect = img.get_rect(**anchor)
        surface.blit(img, rect)
        return rect
