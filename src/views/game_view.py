"""Vue principale : assemble le rendu du labyrinthe et des entités."""

import pygame

from ..models.pacman import Pacman
from ..models.game import HALF
from .sprites import SpriteSheet
from .maze_view import MazeView
from .sprite_view import Animator
from .settings import PACMAN_ANIMATIONS, GHOST_ANIMATIONS, COLORS, GOMMES_TILES

ASSET_PATH = "assets/default.png"
BACKGROUND = (0, 0, 0)

# Côté d'une cellule de base (avant mise à l'échelle), en pixels.
BASE_CELL = 8

# Palette de Pac-Man dans la planche (palette_index, macro_row).
PACMAN_PALETTE = (2, 1)

# Couleurs RGB des chemins de chaque fantôme.
_PATH_COLORS = {
    "red":    (255, 0,   0),
    "pink":   (255, 184, 255),
    "cyan":   (0,   255, 255),
    "orange": (255, 184, 81),
}


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
        # Facteur pixel-modèle → pixel-écran (1 pixel-modèle = cell_pitch / HALF px écran).
        self.model_scale = self.cell_pitch / HALF

        # Sprites des gommes pré-scalés.
        sc, sr = GOMMES_TILES["small"]
        bc, br = GOMMES_TILES["big"]
        raw_small = self.sheet.get_small_sprite(0, 0, sc, sr, 1)
        raw_big   = self.sheet.get_small_sprite(0, 0, bc, br, 1)
        s_size = max(2, round(self.cell_pitch * 0.5))
        b_size = max(4, round(self.cell_pitch * 0.85))
        self._gom_img  = pygame.transform.scale(raw_small, (s_size, s_size))
        self._sgom_img = pygame.transform.scale(raw_big,   (b_size, b_size))

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

    def _tile_screen_pos(self, col, row):
        """Convertit une case originale (col, row) en coordonnées écran."""
        x = self.offset_x + round((col * 2 + 1.5) * self.cell_pitch)
        y = self.offset_y + round((row * 2 + 1.5) * self.cell_pitch)
        return x, y

    def _draw_ghost_paths(self, game):
        """Dessine le chemin prévu de chaque fantôme avec sa couleur."""
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        for ghost in game.ghosts:
            path = ghost.compute_path(game.maze, game.pacman)
            if len(path) < 2:
                continue
            rgb = _PATH_COLORS.get(ghost.color, (255, 255, 255))
            points = [self._tile_screen_pos(c, r) for c, r in path]
            pygame.draw.lines(overlay, (*rgb, 160), False, points, 4)
        self.screen.blit(overlay, (0, 0))

    def render(self, game, now):
        """Dessine une frame complète à partir de l'état du jeu."""
        self.screen.fill(BACKGROUND)
        self.screen.blit(self.maze_surface, (self.offset_x, self.offset_y))

        # Gommes
        for gx, gy in game.maze.pacgums:
            sx = self.offset_x + round((gx + 0.5) * self.cell_pitch)
            sy = self.offset_y + round((gy + 0.5) * self.cell_pitch)
            self.screen.blit(self._gom_img, self._gom_img.get_rect(center=(sx, sy)))

        # Super-gommes (clignotement toutes les 300 ms)
        if now % 600 < 300:
            for gx, gy in game.maze.super_pacgums:
                sx = self.offset_x + round((gx + 0.5) * self.cell_pitch)
                sy = self.offset_y + round((gy + 0.5) * self.cell_pitch)
                self.screen.blit(self._sgom_img, self._sgom_img.get_rect(center=(sx, sy)))

        self._draw_ghost_paths(game)

        for entity in game.entities():
            animator = self._animator_for(entity)
            animator.update(now)
            # Pixel-modèle -> pixel-écran (mouvement continu, sub-case).
            x = self.offset_x + round(entity.x * self.model_scale)
            y = self.offset_y + round(entity.y * self.model_scale)
            animator.draw(self.screen, x, y)

        pygame.display.flip()
