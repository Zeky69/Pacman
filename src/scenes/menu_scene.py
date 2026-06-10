"""Scène du menu principal : navigation clavier entre les options."""

import pygame

from .scene import Scene
from ..views.bitmap_font import BitmapFont

BACKGROUND = (0, 0, 0)


class MenuScene(Scene):
    """Menu principal : flèches/WASD pour naviguer, Entrée pour valider."""

    OPTIONS = ("Start Game", "View Highscores", "Instructions", "Exit")

    def __init__(self, app):
        super().__init__(app)
        self.selected = 0
        h = app.screen.get_height()
        big = max(2, h // 84)
        small = max(1, h // 176)
        self.title_font = BitmapFont(app.sheet, "yellow", scale=big)
        self.font = BitmapFont(app.sheet, "white", scale=small)
        self.font_sel = BitmapFont(app.sheet, "yellow", scale=small)

    def handle_events(self, events, now):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.OPTIONS)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.OPTIONS)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._activate()
            elif event.key == pygame.K_ESCAPE:
                self.app.quit()

    def _activate(self):
        """Déclenche l'action de l'option sélectionnée."""
        choice = self.OPTIONS[self.selected]
        if choice == "Start Game":
            from .game_scene import GameScene
            self.app.change_scene(GameScene(self.app))
        elif choice == "View Highscores":
            from .highscore_scene import HighscoreScene
            self.app.change_scene(HighscoreScene(self.app))
        elif choice == "Instructions":
            from .instructions_scene import InstructionsScene
            self.app.change_scene(InstructionsScene(self.app))
        elif choice == "Exit":
            self.app.quit()

    def draw(self, screen, now):
        screen.fill(BACKGROUND)
        w, h = screen.get_size()

        # Titre + options centrés verticalement comme un seul bloc.
        title_h = self.title_font.height
        item_h = self.font.height
        gap = item_h + 28
        items_h = (len(self.OPTIONS) - 1) * gap + item_h
        group_gap = title_h
        top = (h - (title_h + group_gap + items_h)) // 2

        self.title_font.draw(screen, "PAC-MAN",
                             center=(w // 2, top + title_h // 2))

        start_y = top + title_h + group_gap + item_h // 2
        for i, option in enumerate(self.OPTIONS):
            font = self.font_sel if i == self.selected else self.font
            font.draw(screen, option, center=(w // 2, start_y + i * gap))
