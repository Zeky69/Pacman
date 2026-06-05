"""État global du jeu : agrège le labyrinthe et les entités."""

from .maze import Maze
from .pacman import Pacman
from .ghost import Blinky, Pinky, Inky, Clyde


class Game:
    """Conteneur de l'état de jeu (modèle racine)."""

    def __init__(self, config):
        self.config = config
        self.maze = Maze(cols=config["width"], rows=config["height"])
        self.pacman = Pacman()
        self.ghosts = [Blinky(), Pinky(), Inky(), Clyde()]
        self.score = 0

    def entities(self):
        """Toutes les entités animées (Pac-Man + fantômes)."""
        return [self.pacman, *self.ghosts]

    def update(self):
        """Fait avancer la logique d'une frame."""
        self.pacman.update(self.maze)
        for ghost in self.ghosts:
            ghost.update(self.maze, self.pacman)
