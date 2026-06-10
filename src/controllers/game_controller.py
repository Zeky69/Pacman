"""Application : boucle principale et gestion des scènes.

Le contrôleur ne joue plus une partie en dur : il tient la *scène* courante
(menu, jeu, highscores...) et lui délègue entrées, mise à jour et rendu.
La transition entre écrans se fait via `change_scene`.
"""

import sys
from typing import Any
import pygame

FPS = 60


class GameController:
    """Tient la scène courante et fait tourner la boucle principale."""

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        pygame.init()
        # Plein écran "sans bordure" : fenêtre à la taille du bureau, sans
        # changement de mode vidéo (évite le flash fenêtré -> plein écran).
        width, height = pygame.display.get_desktop_sizes()[0]
        self.screen = pygame.display.set_mode(
            (width, height), pygame.FULLSCREEN | pygame.NOFRAME)
        pygame.display.set_caption("Pac-Man")
        self.clock = pygame.time.Clock()
        self.running = True

        # Planche de sprites partagée (police bitmap des scènes, icônes...).
        from ..views.sprites import SpriteSheet
        from ..views.game_view import ASSET_PATH
        self.sheet = SpriteSheet(ASSET_PATH)

        # Scène de départ : le menu principal.
        from ..scenes.menu_scene import MenuScene
        self.scene = MenuScene(self)

    def change_scene(self, scene: Any) -> None:
        """Remplace la scène courante et appelle son `on_enter`."""
        self.scene = scene
        scene.on_enter()

    def quit(self) -> None:
        """Demande l'arrêt de la boucle principale."""
        self.running = False

    def run(self) -> None:
        """Boucle principale : events -> update -> draw -> flip."""
        while self.running:
            now = pygame.time.get_ticks()
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
            self.scene.handle_events(events, now)
            self.scene.update(now)
            self.scene.draw(self.screen, now)
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
