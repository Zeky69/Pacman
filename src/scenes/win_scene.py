"""Scène de victoire : saisie du nom et sauvegarde du score.

Affichée quand le joueur a mangé toutes les gommes du labyrinthe. Le joueur
tape son nom (A-Z, 0-9), puis Entrée enregistre le score dans le fichier de
highscores et bascule sur l'écran des meilleurs scores. Échap permet de passer
sans enregistrer (retour au menu).
"""

import pygame

from .scene import Scene, AppProtocol
from ..views.bitmap_font import BitmapFont
from ..highscores import save_highscore

BACKGROUND = (0, 0, 0)
CURSOR_COLOR = (255, 221, 0)
MAX_NAME = 10
# Caractères saisissables (présents dans la police bitmap).
ALLOWED = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ")


class WinScene(Scene):
    """YOU WON! : saisie du nom puis enregistrement dans le scoreboard."""

    def __init__(self, app: AppProtocol, score: int) -> None:
        super().__init__(app)
        self.score = score
        self.name = ""
        self.saved = False
        # Zones cliquables des deux invites du bas (remplies à chaque draw).
        self._save_rect = pygame.Rect(0, 0, 0, 0)
        self._skip_rect = pygame.Rect(0, 0, 0, 0)
        self.path = app.config.get("highscore_filename", "scoreboard.json")
        h = app.screen.get_height()
        self.title_font = BitmapFont(app.sheet, "yellow",
                                     scale=max(2, h // 72))
        self.font = BitmapFont(app.sheet, "white", scale=max(1, h // 200))
        self.font_hi = BitmapFont(app.sheet, "yellow", scale=max(2, h // 120))

    def _submit(self) -> None:
        """Enregistre le score (une seule fois) puis va aux highscores."""
        if self.saved:
            return
        save_highscore(self.path, self.name, self.score)
        self.saved = True
        from .highscore_scene import HighscoreScene
        self.app.change_scene(HighscoreScene(self.app))

    def handle_events(self, events: list[pygame.event.Event], now: int) -> None:
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._save_rect.collidepoint(event.pos):
                    self._submit()
                elif self._skip_rect.collidepoint(event.pos):
                    from .menu_scene import MenuScene
                    self.app.change_scene(MenuScene(self.app))
                continue
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

    def draw(self, screen: pygame.Surface, now: int) -> None:
        screen.fill(BACKGROUND)
        w, h = screen.get_size()

        # Bloc principal (titre / score / invite / saisie) centré au-dessus
        # de la zone réservée aux deux hints du bas.
        title_h = self.title_font.height
        fh = self.font.height
        hh = self.font_hi.height
        g = fh
        total = title_h + g + fh + g + fh + g + hh
        top = (h - h // 5 - total) // 2

        y = top
        self.title_font.draw(screen, "YOU WON!",
                             center=(w // 2, y + title_h // 2))
        y += title_h + g
        self.font.draw(screen, f"SCORE {self.score}",
                       center=(w // 2, y + fh // 2))
        y += fh + g
        self.font.draw(screen, "ENTER YOUR NAME",
                       center=(w // 2, y + fh // 2))
        y += fh + g

        # Champ de saisie : nom centré + curseur clignotant à droite.
        text = self.name or " "
        rect = self.font_hi.draw(screen, text, center=(w // 2, y + hh // 2))
        if (now // 400) % 2 == 0 and len(self.name) < MAX_NAME:
            cw = self.font_hi.cell // 2
            cursor = pygame.Rect(0, 0, cw, self.font_hi.height)
            cursor.midleft = (rect.right + 6 if self.name else w // 2,
                              rect.centery)
            pygame.draw.rect(screen, CURSOR_COLOR, cursor)

        self._save_rect = self.font.draw(
            screen, "PRESS ENTER TO SAVE",
            center=(w // 2, h - h // 6)).inflate(40, 16)
        self._skip_rect = self.font.draw(
            screen, "ESC TO SKIP",
            center=(w // 2, h - h // 10)).inflate(40, 16)
