"""État global du jeu : agrège le labyrinthe et les entités."""

from .maze import Maze
from .pacman import Pacman
from .ghost import Blinky, Pinky, Inky, Clyde


class Game:
    """Conteneur de l'état de jeu (modèle racine)."""

    def __init__(self, config):
        self.config = config
        self.maze = Maze(cols=config["width"], rows=config["height"])

        # Placement par case (col, row) du labyrinthe.
        # Si la largeur est paire, on décale d'une case à gauche pour rester centré.
        pac_col = config["width"] // 2 - (1 if config["width"] % 2 == 0 else 0)
        self.pacman = Pacman(pac_col, config["height"] // 2)

        cx, cy = config["width"] - 1, config["height"] - 1
        self.ghosts = [
            Blinky(cx, cy),
            Pinky(0, cy),
            Inky(cx, 0),
            Clyde(0, 0),
        ]
        self.score = 0

    def entities(self):
        """Toutes les entités animées (Pac-Man + fantômes)."""
        return [self.pacman, *self.ghosts]

    def update(self):
        """Fait avancer la logique d'une frame."""
        self.pacman.update(self.maze)
        for ghost in self.ghosts:
            ghost.update(self.maze, self.pacman)
