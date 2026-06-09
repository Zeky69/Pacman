"""Scène d'affichage des meilleurs scores (top 10)."""

import pygame

from .scene import Scene
from ..views.bitmap_font import BitmapFont
from ..highscores import load_highscores

BACKGROUND = (0, 0, 0)


class HighscoreScene(Scene):
    """Affiche le top 10 des scores. Échap/Entrée -> retour menu."""

    def __init__(self, app):
        super().__init__(app)
        h = app.screen.get_height()
        self.title_font = BitmapFont(app.sheet, "yellow",
                                     scale=max(2, h // 80))
        self.font = BitmapFont(app.sheet, "white", scale=max(1, h // 180))
        path = app.config.get("highscore_filename", "scoreboard.json")
        self.scores = load_highscores(path)

    def handle_events(self, events, now):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key in (
                    pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                from .menu_scene import MenuScene
                self.app.change_scene(MenuScene(self.app))

    def draw(self, screen, now):
        screen.fill(BACKGROUND)
        w, h = screen.get_size()

        self.title_font.draw(screen, "HIGHSCORES", center=(w // 2, h // 6))

        if not self.scores:
            self.font.draw(screen, "NO HIGHSCORES YET",
                           center=(w // 2, h // 2))
        else:
            start_y = h // 3
            gap = self.font.height + 14
            for i, (name, score) in enumerate(self.scores):
                line = f"{i + 1}. {name} - {score} PTS"
                self.font.draw(screen, line,
                               center=(w // 2, start_y + i * gap))

        self.font.draw(screen, "PRESS ESC TO GO BACK",
                       center=(w // 2, h - h // 10))
