"""Scène du menu principal : navigation clavier entre les options."""

import pygame

from .scene import Scene, AppProtocol, menu_mouse
from ..views.bitmap_font import BitmapFont

BACKGROUND = (0, 0, 0)

# Cheat-code : taper « fermis » dans l'ordre active le mode secret. Le titre
# devient alors « FERMIS » en rose.
_SECRET_KEYS = (
    pygame.K_f, pygame.K_e, pygame.K_r, pygame.K_m, pygame.K_i, pygame.K_s)


class MenuScene(Scene):
    """Menu principal : flèches/WASD pour naviguer, Entrée pour valider."""

    OPTIONS = ("Start Game", "View Highscores", "Instructions", "Exit")

    def __init__(self, app: AppProtocol) -> None:
        super().__init__(app)
        self.selected = 0
        # Zones cliquables des options (remplies à chaque draw).
        self._item_rects: list[pygame.Rect] = []
        # Progression dans la séquence du cheat-code « fermis ».
        self._secret_progress = 0
        h = app.screen.get_height()
        big = max(2, h // 84)
        small = max(1, h // 176)
        self.title_font = BitmapFont(app.sheet, "yellow", scale=big)
        self.title_font_secret = BitmapFont(app.sheet, "pink", scale=big)
        self.font = BitmapFont(app.sheet, "white", scale=small)
        self.font_sel = BitmapFont(app.sheet, "yellow", scale=small)

    def handle_events(self, events: list[pygame.event.Event], now: int) -> None:
        self.selected, clicked = menu_mouse(events, self._item_rects, self.selected)
        if clicked:
            self._activate()
            return
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            self._check_secret(event.key)
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.OPTIONS)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.OPTIONS)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._activate()
            elif event.key == pygame.K_ESCAPE:
                self.app.quit()

    def _check_secret(self, key: int) -> None:
        """Avance dans la séquence « fermis » ; à la fin, active le mode secret."""
        if key == _SECRET_KEYS[self._secret_progress]:
            self._secret_progress += 1
            if self._secret_progress == len(_SECRET_KEYS):
                self.app.config["secret"] = True
                self._secret_progress = 0
        else:
            # Touche inattendue : on repart de zéro (ou de 1 si c'est le « f »).
            self._secret_progress = 1 if key == _SECRET_KEYS[0] else 0

    def _activate(self) -> None:
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

    def draw(self, screen: pygame.Surface, now: int) -> None:
        screen.fill(BACKGROUND)
        w, h = screen.get_size()

        # Titre + options centrés verticalement comme un seul bloc.
        title_h = self.title_font.height
        item_h = self.font.height
        gap = item_h + 28
        items_h = (len(self.OPTIONS) - 1) * gap + item_h
        group_gap = title_h
        top = (h - (title_h + group_gap + items_h)) // 2

        # Mode secret activé (cheat « fermis ») : titre « FERMIS » en rose.
        if self.app.config.get("secret"):
            self.title_font_secret.draw(screen, "FERMIS",
                                        center=(w // 2, top + title_h // 2))
        else:
            self.title_font.draw(screen, "PAC-MAN",
                                 center=(w // 2, top + title_h // 2))

        start_y = top + title_h + group_gap + item_h // 2
        self._item_rects = []
        for i, option in enumerate(self.OPTIONS):
            font = self.font_sel if i == self.selected else self.font
            rect = font.draw(screen, option, center=(w // 2, start_y + i * gap))
            self._item_rects.append(rect.inflate(40, 16))
