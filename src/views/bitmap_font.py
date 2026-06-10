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

_COLOR_RGB = {
    "white":  (255, 255, 255),
    "yellow": (255, 255,   0),
    "red":    (255,   0,   0),
    "blue":   ( 33,  33, 255),
    "cyan":   (  0, 255, 255),
    "pink":   (255, 184, 255),
    "orange": (255, 184,  81),
}


class BitmapFont:
    """Rend du texte avec la police sprite de Pac-Man, dans une couleur.

    Si la sprite-sheet est absente (_fallback), utilise une police système.
    """

    def __init__(self, sheet, color="white", scale=4, spacing=0):
        self._fallback = getattr(sheet, "_fallback", False)
        self._rgb = _COLOR_RGB.get(color, (255, 255, 255))

        if self._fallback:
            pt = max(8, GLYPH_PX * scale)
            self._sysfont = pygame.font.SysFont("monospace", pt, bold=True)
            self.height = self._sysfont.get_height()
            self.cell = pt
            self.spacing = spacing * scale
        else:
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
        if self._fallback:
            return self._sysfont.size(text.upper())[0]
        n = len(text)
        if n == 0:
            return 0
        return n * self.cell + (n - 1) * self.spacing

    def render(self, text):
        if self._fallback:
            return self._sysfont.render(text.upper(), True, self._rgb)
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
        img = self.render(text)
        rect = img.get_rect(**anchor)
        surface.blit(img, rect)
        return rect
