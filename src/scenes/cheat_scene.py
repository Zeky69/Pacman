"""Cheat menu : overlay sur le jeu gelé.

Ouvert avec la touche C pendant la partie (ou depuis le menu pause).
Fermeture : Échap ou sélection de RESUME.
"""

import pygame

from .scene import Scene
from ..views.bitmap_font import BitmapFont

OVERLAY_COLOR = (0, 0, 0, 210)

# (label affiché, type, attribut game pour les toggles)
_ITEMS = [
    ("GODMODE",     "toggle", "godmode"),
    ("FREEZE",      "toggle", "ghost_freeze"),
    ("SPEED BOOST", "toggle", "speed_boost"),
    ("PATHS",       "toggle", "show_paths"),
    ("TARGETS",     "toggle", "show_targets"),
    ("+1 LIFE",     "action", None),
    ("SKIP LEVEL",  "action", None),
    ("RESUME",      "back",   None),
]


class CheatScene(Scene):
    """Menu de triche superposé au jeu gelé."""

    def __init__(self, app, game_scene):
        super().__init__(app)
        self.game_scene = game_scene
        self.selected = 0

        self.snapshot = app.screen.copy()
        self.overlay = pygame.Surface(app.screen.get_size(), pygame.SRCALPHA)
        self.overlay.fill(OVERLAY_COLOR)

        h = app.screen.get_height()
        big   = max(2, h // 92)
        small = max(1, h // 200)
        self.title_font = BitmapFont(app.sheet, "yellow", scale=big)
        self.font       = BitmapFont(app.sheet, "white",  scale=small)
        self.font_sel   = BitmapFont(app.sheet, "yellow", scale=small)
        self.font_on    = BitmapFont(app.sheet, "yellow", scale=small)
        self.font_off   = BitmapFont(app.sheet, "red",    scale=small)

    # ── navigation ────────────────────────────────────────────────────────────

    def _resume(self):
        self.app.change_scene(self.game_scene)

    def handle_events(self, events, now):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(_ITEMS)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(_ITEMS)
            elif event.key in (pygame.K_ESCAPE, pygame.K_c):
                self._resume()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._activate()

    def _activate(self):
        game = self.game_scene.game
        label, kind, attr = _ITEMS[self.selected]

        if kind == "back":
            self._resume()
        elif kind == "toggle":
            if attr == "speed_boost":
                game.speed_boost = not game.speed_boost
                game.pacman.speed = game._pacman_speed * (2.5 if game.speed_boost else 1.0)
            else:
                setattr(game, attr, not getattr(game, attr))
        elif label == "+1 LIFE":
            game.lives += 1
        elif label == "SKIP LEVEL":
            game.skip_level()
            self._resume()

    # ── rendu ─────────────────────────────────────────────────────────────────

    def draw(self, screen, now):
        screen.blit(self.snapshot, (0, 0))
        screen.blit(self.overlay, (0, 0))
        w, h = screen.get_size()

        # Titre + items centrés verticalement comme un seul bloc.
        title_h = self.title_font.height
        item_h = self.font.height
        gap = item_h + 26
        items_h = (len(_ITEMS) - 1) * gap + item_h
        group_gap = title_h
        top = (h - (title_h + group_gap + items_h)) // 2

        self.title_font.draw(screen, "CHEAT MODE",
                             center=(w // 2, top + title_h // 2))

        start_y = top + title_h + group_gap + item_h // 2
        for i, (label, kind, attr) in enumerate(_ITEMS):
            y = start_y + i * gap
            font = self.font_sel if i == self.selected else self.font

            if kind == "toggle":
                val = bool(getattr(self.game_scene.game, attr))
                state_str = "- ON" if val else "- OFF"
                state_font = self.font_on if val else self.font_off
                # Aligne label + état centrés ensemble.
                lw = font.measure(label)
                sw = state_font.measure(state_str)
                space = font.cell
                total = lw + space + sw
                lx = w // 2 - total // 2
                sx = lx + lw + space
                font.draw(screen, label, midleft=(lx, y))
                state_font.draw(screen, state_str, midleft=(sx, y))
            else:
                font.draw(screen, label, center=(w // 2, y))
