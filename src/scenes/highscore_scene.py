"""Scène d'affichage des meilleurs scores (top 10)."""

import pygame

from .scene import Scene, AppProtocol
from ..views.bitmap_font import BitmapFont
from ..highscores import load_highscores

BACKGROUND = (0, 0, 0)


class HighscoreScene(Scene):
    """Affiche le top 10 des scores. Échap/Entrée -> retour menu."""

    def __init__(self, app: AppProtocol) -> None:
        super().__init__(app)
        h = app.screen.get_height()
        self.title_font = BitmapFont(app.sheet, "yellow",
                                     scale=max(2, h // 104))
        self.font = BitmapFont(app.sheet, "white", scale=max(1, h // 220))
        path = app.config.get("highscore_filename", "scoreboard.json")
        self.scores = load_highscores(path)

    def handle_events(self, events: list[pygame.event.Event], now: int) -> None:
        for event in events:
            key_back = event.type == pygame.KEYDOWN and event.key in (
                pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE)
            click_back = (event.type == pygame.MOUSEBUTTONDOWN
                          and event.button == 1)
            if key_back or click_back:
                from .menu_scene import MenuScene
                self.app.change_scene(MenuScene(self.app))

    def draw(self, screen: pygame.Surface, now: int) -> None:
        screen.fill(BACKGROUND)
        w, h = screen.get_size()

        # Titre + classement centrés dans la zone au-dessus du hint du bas.
        title_h = self.title_font.height
        item_h = self.font.height
        gap = item_h + 14
        n = len(self.scores)
        list_h = ((n - 1) * gap + item_h) if n else item_h
        group_gap = title_h
        total = title_h + group_gap + list_h
        avail = h - h // 6  # réserve le bas pour "PRESS ESC TO GO BACK"
        top = (avail - total) // 2

        self.title_font.draw(screen, "HIGHSCORES",
                             center=(w // 2, top + title_h // 2))

        start_y = top + title_h + group_gap + item_h // 2
        if not self.scores:
            self.font.draw(screen, "NO HIGHSCORES YET",
                           center=(w // 2, start_y))
        else:
            for i, (name, score) in enumerate(self.scores):
                line = f"{i + 1}. {name} - {score} PTS"
                self.font.draw(screen, line,
                               center=(w // 2, start_y + i * gap))

        self.font.draw(screen, "PRESS ESC TO GO BACK",
                       center=(w // 2, h - h // 10))
