"""Gestion des entrées clavier."""

import pygame

KEY_TO_DIRECTION = {
    pygame.K_RIGHT: "right",
    pygame.K_LEFT: "left",
    pygame.K_UP: "up",
    pygame.K_DOWN: "down",
    # WASD (claviers QWERTY) en plus des flèches.
    pygame.K_d: "right",
    pygame.K_a: "left",
    pygame.K_w: "up",
    pygame.K_s: "down",
}


class InputController:
    """Traduit les événements clavier en actions sur le jeu."""

    def apply(self, events, game):
        """Applique les entrées de mouvement de la frame.

        Renvoie l'action de scène demandée (``"pause"`` sur Échap) ou ``None``.
        """
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_ESCAPE:
                return "pause"
            direction = KEY_TO_DIRECTION.get(event.key)
            if direction:
                game.pacman.queued_direction = direction
        return None
