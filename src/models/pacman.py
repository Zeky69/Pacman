"""Modèle de Pac-Man : état pur, sans dépendance graphique.

Le dossier `debug/` ne contenait pas de logique de déplacement/collision :
cette classe ne porte donc que l'état. La logique de mouvement (déplacement
case par case, collisions avec `Maze`) reste à implémenter dans `update()`.
"""


class Pacman:
    def __init__(self, x=0, y=0, direction="right"):
        self.x = x                  # position en pixels à l'écran
        self.y = y
        self.direction = direction  # 'right' | 'left' | 'up' | 'down'
        self.alive = True

    def update(self, maze):
        """À implémenter : déplacement et collisions contre `maze`."""
        pass
