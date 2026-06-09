"""Scène de pause : superposée au jeu gelé.

La partie en cours n'est pas recréée : on garde la référence vers la
`GameScene` d'origine, donc « Resume » reprend exactement le même état.
Le fond est une capture figée du jeu (le modèle n'est plus mis à jour).
"""

import pygame

from .scene import Scene

TITLE_COLOR = (255, 255, 0)
TEXT_COLOR = (255, 255, 255)
SELECTED_COLOR = (255, 255, 0)
OVERLAY_COLOR = (0, 0, 0, 180)


class PauseScene(Scene):
    """Menu de pause : Resume / Return to Main Menu."""

    OPTIONS = ("Resume", "Return to Main Menu")

    def __init__(self, app, game_scene):
        super().__init__(app)
        self.game_scene = game_scene
        self.selected = 0
        # Capture figée du dernier rendu du jeu (affiché en fond).
        self.snapshot = app.screen.copy()
        self.overlay = pygame.Surface(app.screen.get_size(), pygame.SRCALPHA)
        self.overlay.fill(OVERLAY_COLOR)
        h = app.screen.get_height()
        self.title_font = pygame.font.Font(None, max(48, h // 8))
        self.font = pygame.font.Font(None, max(28, h // 16))

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
        if self.OPTIONS[self.selected] == "Resume":
            self._resume()
        else:
            from .menu_scene import MenuScene
            self.app.change_scene(MenuScene(self.app))

    def draw(self, screen, now):
        screen.blit(self.snapshot, (0, 0))
        screen.blit(self.overlay, (0, 0))
        w, h = screen.get_size()

        title = self.title_font.render("PAUSE", True, TITLE_COLOR)
        screen.blit(title, title.get_rect(center=(w // 2, h // 4)))

        start_y = h // 2
        gap = self.font.get_height() + 20
        for i, option in enumerate(self.OPTIONS):
            selected = (i == self.selected)
            color = SELECTED_COLOR if selected else TEXT_COLOR
            label = f"> {option} <" if selected else option
            text = self.font.render(label, True, color)
            rect = text.get_rect(center=(w // 2, start_y + i * gap))
            screen.blit(text, rect)
