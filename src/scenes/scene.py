"""Classe de base d'une scène (écran) du jeu.

Une scène encapsule un écran autonome (menu, jeu, game over...). L'« app »
(GameController) tient la scène courante, lui transmet les événements de la
frame, l'update et le rendu, et offre `change_scene` / `quit` pour les
transitions. Une scène ne fait jamais `pygame.display.flip()` : c'est l'app
qui flippe une seule fois par frame (permet d'empiler des overlays).
"""


class Scene:
    """Écran autonome : gère ses entrées, sa logique et son rendu."""

    def __init__(self, app):
        self.app = app

    def on_enter(self):
        """Appelée une fois quand la scène devient active (optionnel)."""

    def handle_events(self, events, now):
        """Traite les événements pygame de la frame (liste)."""

    def update(self, now):
        """Fait avancer la logique de la scène."""

    def draw(self, screen, now):
        """Dessine la scène sur `screen` (sans flip : l'app s'en charge)."""
