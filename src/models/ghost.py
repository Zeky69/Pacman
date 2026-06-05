"""Modèle de fantôme : état pur, sans dépendance graphique.

La logique d'IA (poursuite, dispersion, mode effrayé) reste à implémenter :
le dossier `debug/` ne fournissait que les animations.
"""


class Ghost:
    def __init__(self, x=0, y=0, direction="right", color="red"):
        self.x = x
        self.y = y
        self.direction = direction
        self.color = color          # 'red' | 'pink' | 'cyan' | 'orange'
        self.frightened = False

    def update(self, maze, pacman):
        """À implémenter : déplacement / IA contre `maze` et `pacman`."""
        pass


class Blinky(Ghost):
    def __init__(self, x=0, y=0, direction="right"):
        super().__init__(x, y, direction, color="red")


class Pinky(Ghost):
    def __init__(self, x=0, y=0, direction="right"):
        super().__init__(x, y, direction, color="pink")


class Inky(Ghost):
    def __init__(self, x=0, y=0, direction="right"):
        super().__init__(x, y, direction, color="cyan")


class Clyde(Ghost):
    def __init__(self, x=0, y=0, direction="right"):
        super().__init__(x, y, direction, color="orange")
