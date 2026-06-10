"""Scène de victoire : saisie du nom et sauvegarde du score.

Affichée quand le joueur a mangé toutes les gommes du labyrinthe. Le joueur
tape son nom (A-Z, 0-9), puis Entrée enregistre le score dans le fichier de
highscores et bascule sur l'écran des meilleurs scores. Échap permet de passer
sans enregistrer (retour au menu).
"""

import pygame

from .scene import Scene
from ..views.bitmap_font import BitmapFont
from ..highscores import save_highscore

BACKGROUND = (0, 0, 0)
CURSOR_COLOR = (255, 221, 0)
MAX_NAME = 12
# Caractères saisissables (présents dans la police bitmap).
ALLOWED = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")


class WinScene(Scene):
    """YOU WON! : saisie du nom puis enregistrement dans le scoreboard."""

    def __init__(self, app, score):
        super().__init__(app)
        self.score = score
        self.name = ""
        self.saved = False
        self.path = app.config.get("highscore_filename", "scoreboard.json")
        h = app.screen.get_height()
        self.title_font = BitmapFont(app.sheet, "yellow",
                                     scale=max(2, h // 56))
        self.font = BitmapFont(app.sheet, "white", scale=max(1, h // 160))
        self.font_hi = BitmapFont(app.sheet, "yellow", scale=max(2, h // 96))

    def _submit(self):
        """Enregistre le score (une seule fois) puis va aux highscores."""
        if self.saved:
            return
        save_highscore(self.path, self.name, self.score)
        self.saved = True
        from .highscore_scene import HighscoreScene
        self.app.change_scene(HighscoreScene(self.app))

    def handle_events(self, events, now):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_RETURN:
                self._submit()
            elif event.key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]
            elif event.key == pygame.K_ESCAPE:
                from .menu_scene import MenuScene
                self.app.change_scene(MenuScene(self.app))
            else:
                ch = event.unicode.upper()
                if ch in ALLOWED and len(self.name) < MAX_NAME:
                    self.name += ch

    def draw(self, screen, now):
        screen.fill(BACKGROUND)
        w, h = screen.get_size()

        self.title_font.draw(screen, "YOU WON!", center=(w // 2, h // 5))
        self.font.draw(screen, f"SCORE {self.score}",
                       center=(w // 2, h // 3))
        self.font.draw(screen, "ENTER YOUR NAME",
                       center=(w // 2, h // 2 - self.font.height))

        # Champ de saisie : nom centré + curseur clignotant à droite.
        field_y = h // 2 + self.font_hi.height
        text = self.name or " "
        rect = self.font_hi.draw(screen, text, center=(w // 2, field_y))
        if (now // 400) % 2 == 0 and len(self.name) < MAX_NAME:
            cw = self.font_hi.cell // 2
            cursor = pygame.Rect(0, 0, cw, self.font_hi.height)
            cursor.midleft = (rect.right + 6 if self.name else w // 2,
                              rect.centery)
            pygame.draw.rect(screen, CURSOR_COLOR, cursor)

        self.font.draw(screen, "PRESS ENTER TO SAVE",
                       center=(w // 2, h - h // 6))
        self.font.draw(screen, "ESC TO SKIP",
                       center=(w // 2, h - h // 10))
