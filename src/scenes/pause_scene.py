"""Scène de pause : superposée au jeu gelé.

La partie en cours n'est pas recréée : on garde la référence vers la
`GameScene` d'origine, donc « Resume » reprend exactement le même état.
Le fond est une capture figée du jeu (le modèle n'est plus mis à jour).
"""

import pygame

from .scene import Scene
from ..views.bitmap_font import BitmapFont

OVERLAY_COLOR = (0, 0, 0, 180)


class PauseScene(Scene):
    """Menu de pause : Resume / Return to Main Menu."""

    OPTIONS = ("Resume", "Cheat Mode", "Return to Main Menu")

    def __init__(self, app, game_scene):
        super().__init__(app)
        self.game_scene = game_scene
        self.selected = 0
        # Capture figée du dernier rendu du jeu (affiché en fond).
        self.snapshot = app.screen.copy()
        self.overlay = pygame.Surface(app.screen.get_size(), pygame.SRCALPHA)
        self.overlay.fill(OVERLAY_COLOR)
        h = app.screen.get_height()
        big = max(2, h // 72)
        small = max(1, h // 160)
        self.title_font = BitmapFont(app.sheet, "yellow", scale=big)
        self.font = BitmapFont(app.sheet, "white", scale=small)
        self.font_sel = BitmapFont(app.sheet, "yellow", scale=small)

    def _resume(self):
        """Reprend la partie en cours (même instance de GameScene)."""
        self.app.change_scene(self.game_scene)

    def handle_events(self, events, now):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.OPTIONS)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.OPTIONS)
            elif event.key == pygame.K_ESCAPE:
                self._resume()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._activate()

    def _activate(self):
        """Déclenche l'option sélectionnée."""
        choice = self.OPTIONS[self.selected]
        if choice == "Resume":
            self._resume()
        elif choice == "Cheat Mode":
            from .cheat_scene import CheatScene
            self.app.change_scene(CheatScene(self.app, self.game_scene))
        else:
            from .menu_scene import MenuScene
            self.app.change_scene(MenuScene(self.app))

    def draw(self, screen, now):
        screen.blit(self.snapshot, (0, 0))
        screen.blit(self.overlay, (0, 0))
        w, h = screen.get_size()

        self.title_font.draw(screen, "PAUSE", center=(w // 2, h // 4))

        start_y = h // 2
        gap = self.font.height + 28
        for i, option in enumerate(self.OPTIONS):
            font = self.font_sel if i == self.selected else self.font
            font.draw(screen, option, center=(w // 2, start_y + i * gap))
