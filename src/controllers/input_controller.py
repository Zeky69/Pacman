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
            if event.key == pygame.K_c:
                return "cheat"
            if event.key == pygame.K_g:
                game.invincible = not game.invincible
                continue
            if event.key == pygame.K_f:
                game.ghost_freeze = not game.ghost_freeze
                continue
            if event.key == pygame.K_l:
                game.lives += 1
                continue
            if event.key == pygame.K_v:
                game.speed_boost = not game.speed_boost
                boost = 2.5 if game.speed_boost else 1.0
                game.pacman.speed = game._pacman_speed * boost
                continue
            direction = KEY_TO_DIRECTION.get(event.key)
            if direction:
                game.pacman.queued_direction = direction
        return None
