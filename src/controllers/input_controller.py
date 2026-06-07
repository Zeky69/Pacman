"""Gestion des entrées clavier."""

import pygame

KEY_TO_DIRECTION = {
    pygame.K_RIGHT: "right",
    pygame.K_LEFT: "left",
    pygame.K_UP: "up",
    pygame.K_DOWN: "down",
}


class InputController:
    """Traduit les événements pygame en actions sur le jeu."""

    def handle_events(self, game):
        """Traite la file d'événements. Renvoie False pour quitter."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                direction = KEY_TO_DIRECTION.get(event.key)
                if direction:
                    game.pacman.queued_direction = direction
        return True
