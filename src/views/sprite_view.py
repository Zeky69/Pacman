"""Animation des sprites (Pac-Man, fantômes) à partir d'une sprite-sheet."""

from typing import Any
import pygame
from .sprites import SpriteSheet


class Animator:
    """Joue une animation (liste de frames) issue d'un dict d'animation.

    Le dict attendu suit le format de `settings.PACMAN_ANIMATIONS` /
    `GHOST_ANIMATIONS` :
        {"frame": [(col, row), ...], "x_flip", "y_flip", "loop_type", "rotation"}
    """

    def __init__(self, data: dict[str, Any], sheet: SpriteSheet,
                 palette_index: int = 0, macro_row: int = 0,
                 size: int = 32, speed: int = 100) -> None:
        self.loop_type = data.get("loop_type", "none")
        self.speed = speed              # ms entre deux frames
        self.index = 0
        self.finished = False
        self.last_update = pygame.time.get_ticks()
        self.frames = self._build_frames(data, sheet, palette_index, macro_row, size)
        self.image = self.frames[self.index]

    @staticmethod
    def _build_frames(data: dict[str, Any], sheet: SpriteSheet,
                      palette_index: int, macro_row: int,
                      size: int) -> list[pygame.Surface]:
        """Extrait, transforme (flip/rotation) et met à la taille `size` (px)."""
        frames = []
        for col, row in data["frame"]:
            img = sheet.get_large_sprite(macro_row, palette_index, col, row, 1)
            if data["x_flip"] or data["y_flip"]:
                img = pygame.transform.flip(img, data["x_flip"], data["y_flip"])
            if data["rotation"] != 0:
                img = pygame.transform.rotate(img, data["rotation"])
            # scale() = plus proche voisin -> pixels nets (pas de flou).
            frames.append(pygame.transform.scale(img, (size, size)))

        # En pingpong, on rejoue les frames intermédiaires à l'envers.
        if data["loop_type"] == "pingpong" and len(frames) > 2:
            frames += [frames[i] for i in range(len(frames) - 2, 0, -1)]
        return frames

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
