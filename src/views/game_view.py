"""Vue principale : assemble le rendu du labyrinthe et des entités."""

import pygame

from ..models.pacman import Pacman
from .sprites import SpriteSheet
from .maze_view import MazeView
from .sprite_view import Animator
from .settings import PACMAN_ANIMATIONS, GHOST_ANIMATIONS, COLORS

ASSET_PATH = "assets/default.png"
BACKGROUND = (0, 0, 0)

# Côté d'une cellule de base (avant mise à l'échelle), en pixels.
BASE_CELL = 8

# Palette de Pac-Man dans la planche (palette_index, macro_row).
PACMAN_PALETTE = (2, 1)


class GameView:
    """Charge les ressources graphiques et dessine l'état du jeu."""

    def __init__(self, screen, maze):
        self.screen = screen
        self.sheet = SpriteSheet(ASSET_PATH)
        screen_w, screen_h = screen.get_size()

        # 1. Échelle entière (tuiles nettes) pour pré-rendre le labyrinthe.
        self.scale = max(1, min(
            screen_w // (maze.width * BASE_CELL),
            screen_h // (maze.height * BASE_CELL),
        ))
        self.maze_view = MazeView(self.sheet, scale=self.scale)

        # 2. Pré-rendu du labyrinthe (statique) sur sa propre surface.
        tile = self.maze_view.tile_size
        maze_w, maze_h = maze.width * tile, maze.height * tile
        base_surface = pygame.Surface((maze_w, maze_h))
        self.maze_view.draw(base_surface, maze, 0, 0)

        # 3. Redimensionnement flottant pour remplir l'écran au mieux (ratio conservé).
        self.fit = min(screen_w / maze_w, screen_h / maze_h)
        self.maze_surface = pygame.transform.scale(
            base_surface, (round(maze_w * self.fit), round(maze_h * self.fit))
        )

        # 4. Centrage de la surface finale.
        self.offset_x = (screen_w - self.maze_surface.get_width()) // 2
        self.offset_y = (screen_h - self.maze_surface.get_height()) // 2

        # Pas exact (flottant) entre deux cases -> positionnement sans dérive.
        self.cell_pitch = tile * self.fit
        # Taille d'une tuile affichée : les entités sont dimensionnées à cette taille.
        self.tile_px = round(self.cell_pitch)

        self._animators = {}  # cache : (id(entity), direction) -> Animator

    def _animator_for(self, entity):
        """Renvoie (en le créant au besoin) l'animateur courant de l'entité."""
        key = (id(entity), entity.direction)
        if key not in self._animators:
            if isinstance(entity, Pacman):
                data = PACMAN_ANIMATIONS[entity.direction]
                palette_index, macro_row = PACMAN_PALETTE
            else:  # Ghost
                data = GHOST_ANIMATIONS[entity.direction]
                palette_index, macro_row = COLORS[entity.color]
            self._animators[key] = Animator(
                data, self.sheet, palette_index, macro_row, size=self.tile_px
            )
        return self._animators[key]

    def render(self, game, now):
        """Dessine une frame complète à partir de l'état du jeu."""
        self.screen.fill(BACKGROUND)
        self.screen.blit(self.maze_surface, (self.offset_x, self.offset_y))

        for entity in game.entities():
            animator = self._animator_for(entity)
            animator.update(now)
            # Case (col, row) -> centre de la tuile correspondante à l'écran.
            gx, gy = game.maze.cell_to_grid(entity.col, entity.row)
            x = self.offset_x + round((gx + 0.5) * self.cell_pitch)
            y = self.offset_y + round((gy + 0.5) * self.cell_pitch)
            animator.draw(self.screen, x, y)

        pygame.display.flip()
