"""Scène du menu principal : navigation clavier entre les options."""

import pygame

from .scene import Scene

BACKGROUND = (0, 0, 0)
TITLE_COLOR = (255, 255, 0)
TEXT_COLOR = (255, 255, 255)
SELECTED_COLOR = (255, 255, 0)


class MenuScene(Scene):
    """Menu principal : flèches/WASD pour naviguer, Entrée pour valider."""

    OPTIONS = ("Start Game", "View Highscores", "Instructions", "Exit")

    def __init__(self, app):
        super().__init__(app)
        self.selected = 0
        h = app.screen.get_height()
        self.title_font = pygame.font.Font(None, max(48, h // 6))
        self.font = pygame.font.Font(None, max(28, h // 16))

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

        title = self.title_font.render("PAC-MAN", True, TITLE_COLOR)
        screen.blit(title, title.get_rect(center=(w // 2, h // 4)))

        start_y = h // 2
        gap = self.font.get_height() + 20
        for i, option in enumerate(self.OPTIONS):
            selected = (i == self.selected)
            color = SELECTED_COLOR if selected else TEXT_COLOR
            label = f"> {option} <" if selected else option
            text = self.font.render(label, True, color)
            rect = text.get_rect(center=(w // 2, start_y + i * gap))
            screen.blit(text, rect)
