"""Vue principale : assemble le rendu du labyrinthe et des entités."""

import pygame

from ..models.pacman import Pacman
from ..models.ghost import Inky, Blinky, Clyde
from ..models.game import HALF
from .sprites import SpriteSheet
from .maze_view import MazeView
from .sprite_view import Animator
from .bitmap_font import BitmapFont
from .settings import PACMAN_ANIMATIONS, GHOST_ANIMATIONS, COLORS, GOMMES_TILES, SCORE_SPRITE

ASSET_PATH = "assets/default.png"
BACKGROUND = (0, 0, 0)

DEBUG_SHOW_PATHS   = False   # chemins BFS de chaque fantôme
DEBUG_SHOW_TARGETS = False   # visualisations des cibles (Inky line, Clyde radius)

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

        # Bandes réservées au HUD (haut = score/level/time, bas = vies).
        # Le labyrinthe est ajusté pour tenir entre les deux.
        self.hud_top = max(40, screen_h // 12)
        self.hud_bottom = max(40, screen_h // 12)
        avail_h = screen_h - self.hud_top - self.hud_bottom

        # 1. Échelle entière (tuiles nettes) pour pré-rendre le labyrinthe.
        self.scale = max(1, min(
            screen_w // (maze.width * BASE_CELL),
            avail_h // (maze.height * BASE_CELL),
        ))
        self.maze_view = MazeView(self.sheet, scale=self.scale)

        # 2-3. Ratio d'ajustement (les dimensions du labyrinthe sont constantes
        # d'un niveau à l'autre) puis pré-rendu du labyrinthe. Le pré-rendu est
        # isolé dans _rebuild_maze_surface : il doit être refait à chaque
        # changement de niveau, car la disposition des murs change.
        tile = self.maze_view.tile_size
        maze_w, maze_h = maze.width * tile, maze.height * tile
        self.fit = min(screen_w / maze_w, avail_h / maze_h)
        self._maze = None
        self._rebuild_maze_surface(maze)

        # 4. Centrage : horizontal sur l'écran, vertical entre les bandes HUD.
        self.offset_x = (screen_w - self.maze_surface.get_width()) // 2
        self.offset_y = self.hud_top + (
            avail_h - self.maze_surface.get_height()) // 2

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
        b_size = max(4, round(self.cell_pitch * 0.6))
        self._gom_img  = pygame.transform.scale(raw_small, (s_size, s_size))
        self._sgom_img = pygame.transform.scale(raw_big,   (b_size, b_size))

        self._animators = {}  # cache : (id(entity), direction) -> Animator

        # Sprites de score (mangé un fantôme) pré-scalés à la taille d'une case.
        score_size = max(8, self.tile_px)
        self._score_imgs = {}
        for label, (sc, sr) in SCORE_SPRITE.items():
            raw = self.sheet.get_large_sprite(0, 0, sc, sr, 1)
            self._score_imgs[label] = pygame.transform.scale(raw, (score_size, score_size))

        # Ressources HUD : police sprite Pac-Man (3 couleurs) + icône de vie.
        hud_s = max(2, self.hud_top // 20)
        self.hud_font = BitmapFont(self.sheet, "white", scale=hud_s)
        self.hud_font_yellow = BitmapFont(self.sheet, "yellow", scale=hud_s)
        self.hud_font_red = BitmapFont(self.sheet, "red", scale=hud_s)
        # Police réduite pour les popups de score en mode ASCII (valeur non-standard).
        self.popup_font = BitmapFont(self.sheet, "yellow", scale=max(1, hud_s - 2))
        pac_palette, pac_macro = PACMAN_PALETTE
        life_raw = self.sheet.get_large_sprite(pac_macro, pac_palette, 6, 3, 1)
        life_size = max(12, int(self.hud_bottom * 0.7))
        self._life_icon = pygame.transform.scale(
            life_raw, (life_size, life_size))

    def _rebuild_maze_surface(self, maze):
        """(Re)génère le fond pré-rendu du labyrinthe pour `maze`.

        Appelée à l'init et à chaque changement de niveau : comme la
        disposition des murs change, le fond statique doit être redessiné,
        sinon on continue de voir l'ancien tableau (et on « traverse » les
        nouveaux murs). On garde une référence sur `maze` pour détecter le
        changement par identité d'objet.
        """
        tile = self.maze_view.tile_size
        maze_w, maze_h = maze.width * tile, maze.height * tile
        base_surface = pygame.Surface((maze_w, maze_h))
        self.maze_view.draw(base_surface, maze, 0, 0)
        self.maze_surface = pygame.transform.scale(
            base_surface, (round(maze_w * self.fit), round(maze_h * self.fit))
        )
        self._maze = maze

    def _animator_for(self, entity, now=0):
        """Renvoie (en le créant au besoin) l'animateur courant de l'entité."""
        if isinstance(entity, Pacman):
            if entity.dead:
                # dead_until est unique à chaque mort → animateur remis à zéro automatiquement
                key = (id(entity), "dead", entity.direction, entity.dead_until)
                if key not in self._animators:
                    data = PACMAN_ANIMATIONS[f"death_{entity.direction}"]
                    palette_index, macro_row = PACMAN_PALETTE
                    self._animators[key] = Animator(
                        data, self.sheet, palette_index, macro_row, size=self.tile_px
                    )
                return self._animators[key]
            key = (id(entity), entity.direction)
            if key not in self._animators:
                data = PACMAN_ANIMATIONS[entity.direction]
                palette_index, macro_row = PACMAN_PALETTE
                self._animators[key] = Animator(
                    data, self.sheet, palette_index, macro_row, size=self.tile_px
                )
            return self._animators[key]

        # Ghost mangé : retour au spawn en noir
        if entity.eaten:
            key = (id(entity), "eaten", entity.direction)
            if key not in self._animators:
                data = GHOST_ANIMATIONS[entity.direction]
                palette_index, macro_row = COLORS["black"]
                self._animators[key] = Animator(
                    data, self.sheet, palette_index, macro_row, size=self.tile_px
                )
            return self._animators[key]

        # Ghost effrayé → animation frightened + couleur propre (ou red-2 si clignotement)
        if entity.frightened:
            if entity.is_blinking(now) and (now // 250) % 2 == 0:
                color = "red-2"
            else:
                color = entity.color
            key = (id(entity), "frightened", color)
            if key not in self._animators:
                data = GHOST_ANIMATIONS["frightened"]
                palette_index, macro_row = COLORS[color]
                self._animators[key] = Animator(
                    data, self.sheet, palette_index, macro_row, size=self.tile_px
                )
            return self._animators[key]

        key = (id(entity), entity.direction)
        if key not in self._animators:
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

    def _entity_screen_pos(self, entity):
        """Position écran (centre) d'une entité depuis ses coordonnées modèle."""
        x = self.offset_x + round(entity.x * self.model_scale)
        y = self.offset_y + round(entity.y * self.model_scale)
        return x, y

    def _draw_inky_line(self, game):
        """Droite Blinky–Pac-Man étendue jusqu'à la cible d'Inky."""
        blinky = next((g for g in game.ghosts if isinstance(g, Blinky)), None)
        inky   = next((g for g in game.ghosts if isinstance(g, Inky)),   None)
        if blinky is None or inky is None:
            return

        bx, by = self._entity_screen_pos(blinky)
        px, py = self._entity_screen_pos(game.pacman)
        # Cible d'Inky = symétrique de Blinky par rapport à Pac-Man
        tc, tr = inky._target(game.pacman)
        tx, ty = self._tile_screen_pos(tc, tr)

        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        pygame.draw.line(overlay, (0, 255, 255, 180), (bx, by), (tx, ty), 3)
        pygame.draw.circle(overlay, (255, 0,   0,   220), (bx, by), 6)   # Blinky
        pygame.draw.circle(overlay, (255, 255, 0,   220), (px, py), 6)   # Pac-Man (milieu)
        pygame.draw.circle(overlay, (0,   255, 255, 220), (tx, ty), 6)   # cible Inky
        self.screen.blit(overlay, (0, 0))

    def _draw_ghost_targets(self, game):
        """Petit carré coloré sur la case cible de chaque fantôme."""
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        sq = max(4, round(self.cell_pitch * 0.4))
        for ghost in game.ghosts:
            tc, tr = ghost._clamp_target(*ghost._target(game.pacman), game.maze)
            tx, ty = self._tile_screen_pos(tc, tr)
            rgb = _PATH_COLORS.get(ghost.color, (255, 255, 255))
            rect = pygame.Rect(tx - sq // 2, ty - sq // 2, sq, sq)
            pygame.draw.rect(overlay, (*rgb, 220), rect)
        self.screen.blit(overlay, (0, 0))

    def _draw_clyde_radius(self, game):
        """Cercle de rayon FLEE_RADIUS cases autour de Clyde (orange)."""
        clyde = next((g for g in game.ghosts if isinstance(g, Clyde)), None)
        if clyde is None:
            return
        px, py = self._entity_screen_pos(game.pacman)
        radius_px = round(Clyde.FLEE_RADIUS * self.cell_pitch * 2)
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        pygame.draw.circle(overlay, (255, 184, 81, 180), (px, py), radius_px, 2)
        self.screen.blit(overlay, (0, 0))

    def _draw_score_popups(self, game):
        """Affiche les popups de score au-dessus de l'endroit où le fantôme a été mangé."""
        for popup in game.score_popups:
            label = str(popup['value'])
            x = self.offset_x + round(popup['x'] * self.model_scale)
            y = self.offset_y + round(popup['y'] * self.model_scale)
            if label in self._score_imgs:
                img = self._score_imgs[label]
                self.screen.blit(img, img.get_rect(center=(x, y)))
            else:
                self.popup_font.draw(self.screen, label, center=(x, y))

    def _draw_hud(self, game):
        """Barre du haut (score / level / time) + vies en bas (icônes)."""
        w, h = self.screen.get_size()
        top_cy = self.hud_top // 2

        # Barre du haut (police sprite Pac-Man).
        self.hud_font.draw(self.screen, f"SCORE {game.score}",
                           midleft=(24, top_cy))
        self.hud_font_yellow.draw(self.screen, f"LEVEL {game.level}",
                                  center=(w // 2, top_cy))

        secs = game.time_remaining
        font = self.hud_font_red if secs <= 10 else self.hud_font
        font.draw(self.screen, f"TIME {secs}", midright=(w - 24, top_cy))

        # Barre du bas : jusqu'à 5 icônes Pac-Man, puis "+N" si vies > 5.
        MAX_ICONS = 5
        icon_w = self._life_icon.get_width()
        y = h - self.hud_bottom // 2
        displayed = min(max(0, game.lives), MAX_ICONS)
        for i in range(displayed):
            x = 24 + i * (icon_w + 10)
            rect = self._life_icon.get_rect(midleft=(x, y))
            self.screen.blit(self._life_icon, rect)
        if game.lives > MAX_ICONS:
            extra = game.lives - MAX_ICONS
            ex = 24 + displayed * (icon_w + 10)
            self.hud_font_yellow.draw(self.screen, f"+{extra}", midleft=(ex, y))

        # Indicateurs de cheats actifs (coin bas-droit).
        cheat_labels = []
        if game.invincible:
            cheat_labels.append(("INVINCIBLE", self.hud_font_yellow))
        if game.ghost_freeze:
            cheat_labels.append(("FREEZE", self.hud_font_red))
        if game.speed_boost:
            cheat_labels.append(("SPEED", self.hud_font))
        if game.show_paths:
            cheat_labels.append(("PATHS", self.hud_font))
        if game.show_targets:
            cheat_labels.append(("TARGETS", self.hud_font))
        cx = w - 16
        for label, font in reversed(cheat_labels):
            font.draw(self.screen, label, midright=(cx, y))
            cx -= font.measure(label) + 16


    def render(self, game, now):
        """Dessine une frame complète à partir de l'état du jeu."""
        # Changement de niveau (nouveau labyrinthe) : re-rendre le fond et
        # purger le cache d'animateurs. Les entités ont été recréées et leurs
        # id() peuvent être réutilisés : sans purge, un fantôme pourrait hériter
        # de l'animateur Pac-Man d'un id recyclé (-> « second Pac-Man »).
        if game.maze is not self._maze:
            self._rebuild_maze_surface(game.maze)
            self._animators.clear()

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

        any_frightened = any(g.frightened for g in game.ghosts)
        if (DEBUG_SHOW_PATHS or game.show_paths) and not any_frightened:
            self._draw_ghost_paths(game)
        if (DEBUG_SHOW_TARGETS or game.show_targets) and not any_frightened:
            self._draw_ghost_targets(game)
            self._draw_inky_line(game)
            self._draw_clyde_radius(game)

        for entity in game.entities():
            animator = self._animator_for(entity, now)
            if isinstance(entity, Pacman) and not entity.dead and not entity.moved:
                animator.index = 1
                animator.image = animator.frames[1]
            else:
                animator.update(now)
            x = self.offset_x + round(entity.x * self.model_scale)
            y = self.offset_y + round(entity.y * self.model_scale)
            if isinstance(entity, Pacman) and game.invincible:
                img = animator.image.copy()
                img.set_alpha(130)
                self.screen.blit(img, img.get_rect(center=(x, y)))
            else:
                animator.draw(self.screen, x, y)

        self._draw_score_popups(game)
        self._draw_hud(game)

        if game.ready:
            cx = self.offset_x + self.maze_surface.get_width() // 2
            cy = self.offset_y + self.maze_surface.get_height() // 2
            self.hud_font_yellow.draw(self.screen, "READY!", center=(cx, cy))
