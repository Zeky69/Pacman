"""Scène d'affichage des meilleurs scores (top 10)."""

import pygame

from .scene import Scene
from ..highscores import load_highscores

BACKGROUND = (0, 0, 0)
TITLE_COLOR = (255, 255, 0)
TEXT_COLOR = (255, 255, 255)


class HighscoreScene(Scene):
    """Affiche le top 10 des scores. Échap/Entrée -> retour menu."""

    def __init__(self, app):
        super().__init__(app)
        h = app.screen.get_height()
        self.title_font = pygame.font.Font(None, max(40, h // 8))
        self.font = pygame.font.Font(None, max(24, h // 18))
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

        title = self.title_font.render("HIGHSCORES", True, TITLE_COLOR)
        screen.blit(title, title.get_rect(center=(w // 2, h // 6)))

        if not self.scores:
            msg = self.font.render("No highscores yet", True, TEXT_COLOR)
            screen.blit(msg, msg.get_rect(center=(w // 2, h // 2)))
        else:
            start_y = h // 3
            gap = self.font.get_height() + 12
            for i, (name, score) in enumerate(self.scores):
                line = f"{i + 1}. {name} - {score} pts"
                text = self.font.render(line, True, TEXT_COLOR)
                rect = text.get_rect(center=(w // 2, start_y + i * gap))
                screen.blit(text, rect)

        hint = self.font.render("Press ESC to go back", True, TEXT_COLOR)
        screen.blit(hint, hint.get_rect(center=(w // 2, h - h // 10)))
