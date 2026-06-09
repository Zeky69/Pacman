"""Scène des instructions / contrôles du jeu."""

import pygame

from .scene import Scene

BACKGROUND = (0, 0, 0)
TITLE_COLOR = (255, 255, 0)
TEXT_COLOR = (255, 255, 255)

LINES = (
    "Move: Arrow keys or WASD",
    "Eat all the pacgums to clear a level",
    "Avoid the ghosts - they cost you a life",
    "Super-pacgum: ghosts become edible for a while",
    "ESC: back to menu",
)


class InstructionsScene(Scene):
    """Affiche les contrôles et règles. Échap/Entrée -> retour menu."""

    def __init__(self, app):
        super().__init__(app)
        h = app.screen.get_height()
        self.title_font = pygame.font.Font(None, max(40, h // 8))
        self.font = pygame.font.Font(None, max(24, h // 20))

    def handle_events(self, events, now):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key in (
                    pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                from .menu_scene import MenuScene
                self.app.change_scene(MenuScene(self.app))

    def draw(self, screen, now):
        screen.fill(BACKGROUND)
        w, h = screen.get_size()

        title = self.title_font.render("INSTRUCTIONS", True, TITLE_COLOR)
        screen.blit(title, title.get_rect(center=(w // 2, h // 6)))

        start_y = h // 3
        gap = self.font.get_height() + 16
        for i, line in enumerate(LINES):
            text = self.font.render(line, True, TEXT_COLOR)
            rect = text.get_rect(center=(w // 2, start_y + i * gap))
            screen.blit(text, rect)
