"""Animation des sprites : rejoue une liste de frames déjà prêtes.

Les frames (transformées et mises à la taille voulue) sont produites en amont
par un ``Skin`` (voir `views.assets`). L'``Animator`` ne gère plus que le
cadencement et le type de boucle.
"""

import pygame

from .sprites import SpriteSheet


class Animator:
    """Joue une liste de frames prêtes selon un type de boucle.

    `loop_type` ∈ {"once", "pingpong", "none"} : "once" s'arrête sur la
    dernière frame (et passe `finished` à True) ; les autres bouclent. Le
    dépliage pingpong est déjà inclus dans `frames`.
    """

    def __init__(self, frames: list[pygame.Surface],
                 loop_type: str = "none", speed: int = 100) -> None:
        self.loop_type = loop_type
        self.speed = speed              # ms entre deux frames
        self.index = 0
        self.finished = False
        self.last_update = pygame.time.get_ticks()
        self.frames = frames
        self.image = self.frames[self.index]

    def reset(self) -> None:
        self.index = 0
        self.finished = False
        self.image = self.frames[self.index]

    def update(self, now: int) -> None:
        """Avance l'animation si le délai `speed` est écoulé."""
        if now - self.last_update <= self.speed:
            return
        self.last_update = now
        if self.loop_type == "once":
            if self.index < len(self.frames) - 1:
                self.index += 1
            else:
                self.finished = True
        else:
            self.index = (self.index + 1) % len(self.frames)
        self.image = self.frames[self.index]

    def draw(self, surface: pygame.Surface, x: float, y: float) -> None:
        """Dessine la frame courante centrée sur (x, y)."""
        surface.blit(self.image, self.image.get_rect(center=(x, y)))


class StaticSprite:
    """Sprite fixe sans animation (fruits, pac-gommes)."""

    def __init__(self, col: int, row: int,
                 sheet: SpriteSheet, is_large: bool = True,
                 scale: float = 3,
                 macro_row: int = 0, palette_index: int = 0):
        if is_large:
            self.image = sheet.get_large_sprite(macro_row, palette_index, col, row, scale)
        else:
            self.image = sheet.get_small_sprite(macro_row, palette_index, col, row, scale)

    def draw(self, surface: pygame.Surface, x: float, y: float) -> None:
        surface.blit(self.image, self.image.get_rect(center=(x, y)))
