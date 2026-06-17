"""Scène du menu principal : navigation clavier entre les options."""

import math
import pygame

from .scene import Scene, AppProtocol, menu_mouse
from ..views.bitmap_font import BitmapFont
from ..views.settings import MANIFEST_WARNING

_GOOFY_COLORS = ("pink", "cyan", "yellow", "orange", "white", "red")

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
        self.font_warn = BitmapFont(app.sheet, "red", scale=max(1, small - 1))
        self._secret_activated_at: int = -1
        self._goofy_title_fonts = [
            BitmapFont(app.sheet, c, scale=big) for c in _GOOFY_COLORS
        ]
        self._goofy_item_fonts = [
            BitmapFont(app.sheet, c, scale=small) for c in _GOOFY_COLORS
        ]

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
                self._secret_activated_at = pygame.time.get_ticks()
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

    def _draw_goofy_title(self, screen: pygame.Surface, now: int,
                          w: int, top: int, title_h: int) -> None:
        """Titre 'FERMIS' : chaque lettre rebondit et change de couleur."""
        title = "FERMIS"
        nc = len(_GOOFY_COLORS)
        char_w = self._goofy_title_fonts[0].cell
        total_w = len(title) * char_w
        base_x = w // 2 - total_w // 2
        base_y = top + title_h // 2

        reveal_ms = 1000
        elapsed = now - self._secret_activated_at

        for i, ch in enumerate(title):
            cx = base_x + i * char_w + char_w // 2

            if elapsed < reveal_ms:
                t = elapsed / reveal_ms
                # Chaque lettre arrive d'une direction différente
                ox = int(((i * 137 + 73) % 500 - 250) * (1 - t) ** 2)
                oy = int(((i * 251 + 31) % 400 - 200) * (1 - t) ** 2)
                angle = ((i * 97 + 11) % 360) * (1 - t)
                cy = base_y + oy
                fi = i % nc
                surf = self._goofy_title_fonts[fi].render(ch)
                surf = pygame.transform.rotate(surf, angle)
                screen.blit(surf, surf.get_rect(center=(cx + ox, cy)))
            else:
                bounce = round(math.sin(now / 180.0 + i * 0.9) * 14)
                fi = (now // 120 + i * 2) % nc
                self._goofy_title_fonts[fi].draw(
                    screen, ch, center=(cx, base_y + bounce))

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

        secret = self.app.config.get("secret", False)
        if secret:
            self._draw_goofy_title(screen, now, w, top, title_h)
        else:
            self.title_font.draw(screen, "PAC-MAN",
                                 center=(w // 2, top + title_h // 2))

        start_y = top + title_h + group_gap + item_h // 2
        self._item_rects = []
        for i, option in enumerate(self.OPTIONS):
            font = self.font_sel if i == self.selected else self.font
            rect = font.draw(screen, option, center=(w // 2, start_y + i * gap))
            self._item_rects.append(rect.inflate(40, 16))

        if MANIFEST_WARNING:
            self.font_warn.draw(
                screen, "! MANIFEST INVALIDE - FALLBACK CHARGE !",
                center=(w // 2, h - self.font_warn.height),
            )
