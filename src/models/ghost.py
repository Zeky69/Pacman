"""Modèle de fantôme : état pur, sans dépendance graphique.

La position est exprimée en CASE du labyrinthe (col, row), dans les
coordonnées des cellules d'origine (comme `maze.entry` / `maze.exit`).
La conversion case -> pixels est faite par la vue.
"""


class Ghost:
    def __init__(self, col=0, row=0, direction="right", color="red"):
        self.col = col              # case (colonne) dans le labyrinthe
        self.row = row              # case (ligne) dans le labyrinthe
        self.direction = direction
        self.color = color          # 'red' | 'pink' | 'cyan' | 'orange'
        self.frightened = False

    def update(self, maze, pacman):
        """À implémenter : déplacement / IA contre `maze` et `pacman`."""
        pass


class Blinky(Ghost):
    def __init__(self, col=0, row=0, direction="right"):
        super().__init__(col, row, direction, color="red")


class Pinky(Ghost):
    def __init__(self, col=0, row=0, direction="right"):
        super().__init__(col, row, direction, color="pink")


class Inky(Ghost):
    def __init__(self, col=0, row=0, direction="right"):
        super().__init__(col, row, direction, color="cyan")


class Clyde(Ghost):
    def __init__(self, col=0, row=0, direction="right"):
        super().__init__(col, row, direction, color="orange")
