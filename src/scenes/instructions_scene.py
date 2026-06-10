"""Scène des instructions / contrôles du jeu."""

import pygame

from .scene import Scene, AppProtocol
from ..views.bitmap_font import BitmapFont

BACKGROUND = (0, 0, 0)

# Uniquement des caractères gérés par la police sprite (A-Z, 0-9, - . ! " /).
LINES = (
    "MOVE - ARROW KEYS OR WASD",
    "EAT ALL PACGUMS TO CLEAR A LEVEL",
    "AVOID GHOSTS - THEY COST A LIFE",
    "SUPER-PACGUM MAKES GHOSTS EDIBLE",
    "ESC - PAUSE THE GAME",
)


class InstructionsScene(Scene):
    """Affiche les contrôles et règles. Échap/Entrée -> retour menu."""

    def __init__(self, app: AppProtocol) -> None:
        super().__init__(app)
        h = app.screen.get_height()
        self.title_font = BitmapFont(app.sheet, "yellow",
                                     scale=max(2, h // 104))
        self.font = BitmapFont(app.sheet, "white", scale=max(1, h // 240))

    def handle_events(self, events: list[pygame.event.Event], now: int) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key in (
                    pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                from .menu_scene import MenuScene
                self.app.change_scene(MenuScene(self.app))

    def draw(self, screen: pygame.Surface, now: int) -> None:
        screen.fill(BACKGROUND)
        w, h = screen.get_size()

        # Titre + lignes centrés verticalement comme un seul bloc.
        title_h = self.title_font.height
        item_h = self.font.height
        gap = item_h + 22
        lines_h = (len(LINES) - 1) * gap + item_h
        group_gap = title_h
        top = (h - (title_h + group_gap + lines_h)) // 2

        self.title_font.draw(screen, "INSTRUCTIONS",
                             center=(w // 2, top + title_h // 2))

        start_y = top + title_h + group_gap + item_h // 2
        for i, line in enumerate(LINES):
            self.font.draw(screen, line, center=(w // 2, start_y + i * gap))
