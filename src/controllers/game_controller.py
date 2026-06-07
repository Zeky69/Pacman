"""Contrôleur principal : boucle de jeu reliant modèle, vue et entrées."""

import sys
import pygame

from ..models.game import Game
from ..views.game_view import GameView
from .input_controller import InputController

FPS = 60


class GameController:
    """Orchestre la boucle de jeu (entrées -> update -> rendu)."""

    def __init__(self, config):
        self.config = config
        pygame.init()
        # Plein écran "sans bordure" : fenêtre à la taille du bureau, sans
        # changement de mode vidéo (évite le flash fenêtré -> plein écran).
        width, height = pygame.display.get_desktop_sizes()[0]
        self.screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN | pygame.NOFRAME)
        pygame.display.set_caption("Pac-Man")
        self.clock = pygame.time.Clock()

        self.game = Game(config)
        self.view = GameView(self.screen, self.game.maze)
        self.input = InputController()

    def run(self):
        running = True
        while running:
            now = pygame.time.get_ticks()
            running = self.input.handle_events(self.game)
            self.game.update()
            self.view.render(self.game, now)
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
