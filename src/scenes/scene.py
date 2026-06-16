"""Classe de base d'une scène (écran) du jeu.

Une scène encapsule un écran autonome (menu, jeu, game over...). L'« app »
(GameController) tient la scène courante, lui transmet les événements de la
frame, l'update et le rendu, et offre `change_scene` / `quit` pour les
transitions. Une scène ne fait jamais `pygame.display.flip()` : c'est l'app
qui flippe une seule fois par frame (permet d'empiler des overlays).
"""

from __future__ import annotations
from typing import Any, Protocol

import pygame


class AppProtocol(Protocol):
    config: dict[str, Any]
    screen: pygame.Surface
    sheet: Any

    def change_scene(self, scene: Any) -> None: ...
    def quit(self) -> None: ...


def menu_mouse(
    events: list[pygame.event.Event],
    rects: list[pygame.Rect],
    selected: int,
) -> tuple[int, bool]:
    """Gère la souris pour un menu à options.

    `rects` sont les zones cliquables des options (dans l'ordre), telles que
    rendues à la frame précédente. Le survol (déplacement souris) met à jour
    l'option sélectionnée ; un clic gauche sur une option la sélectionne et
    déclenche son activation.

    Renvoie ``(index_sélectionné, cliqué)`` : `cliqué` est vrai si une option
    vient d'être cliquée (l'appelant doit alors l'activer).
    """
    for event in events:
        if event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(rects):
                if rect.collidepoint(event.pos):
                    selected = i
                    break
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(rects):
                if rect.collidepoint(event.pos):
                    return i, True
    return selected, False


class Scene:
    """Écran autonome : gère ses entrées, sa logique et son rendu."""

    def __init__(self, app: AppProtocol) -> None:
        self.app = app

    def on_enter(self) -> None:
        """Appelée une fois quand la scène devient active (optionnel)."""

    def handle_events(self, events: list[pygame.event.Event], now: int) -> None:
        """Traite les événements pygame de la frame (liste)."""

    def update(self, now: int) -> None:
        """Fait avancer la logique de la scène."""

    def draw(self, screen: pygame.Surface, now: int) -> None:
        """Dessine la scène sur `screen` (sans flip : l'app s'en charge)."""
