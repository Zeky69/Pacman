"""
Debug visuel des tuiles de labyrinthe en mode FALLBACK (sans asset).

Lance : uv run debug/maze_tile_place_fallback.py

Contrôles :
  Clic gauche    : cycler la tuile au coin survolé (+1)
  Clic droit     : cycler la tuile au coin survolé (-1)
  D              : afficher/masquer les masques de coin
  Entrée         : print rapport dans le terminal
  Scroll         : zoom
  Clic milieu    : panoramique
  Échap          : quitter
"""

import sys
from pathlib import Path
import pygame

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.views.sprites import SpriteSheet
from src.views.settings import MAZE_TILE, COLORS

# ── Constantes ────────────────────────────────────────────────────────────────

NORTH = 1
EAST  = 2
SOUTH = 4
WEST  = 8

SCALE     = 4
TILE_SIZE = 8 * SCALE   # 32 px
GAP       = 20
LABEL_H   = 20
STATUS_H  = 24

MAZE_HEX = [
    "9515391539551795151151153",
    "EBABAE812853C1412BA812812",
    "96A8416A84545412AC4282C2A",
    "C3A83816A9395384453A82D02",
    "96842A852AC07AAD13A8283C2",
    "C1296C43AAB83AA92AA8686BA",
    "92E853968428444682AC12902",
    "AC3814452FA83FFF82C52C42A",
    "85684117AFC6857FAC1383D06",
    "C53AD043AFFFAFFF856AA8143",
    "91441294297FAFD501142C6BA",
    "AA912AC3843FAFFF82856D52A",
    "842A8692A92B8517C4451552A",
    "816AC384468285293917A9542",
    "C416928513C443A828456C3BA",
    "91416AA92C393A82801553AAA",
    "A81292AA814682C6A8693C6AA",
    "A8442C6C2C1168552C16A9542",
    "86956951692C1455416928552",
    "C545545456C54555545444556",
]

CORNER_MAP_DEFAULT = {
     0: None,
     1: "corner_outer_top_left",
     2: "corner_outer_top_right",
     3: "wall_horizontal_top",
     4: "corner_outer_bottom_left",
     5: "border_wall_vertical_left",
     6: "wall_fill",
     7: "border_corner_outer_bottom_right",
     8: "corner_outer_bottom_right",
     9: "wall_fill",
    10: "wall_vertical_right",
    11: "border_corner_outer_bottom_left",
    12: "wall_horizontal_bottom",
    13: "border_corner_outer_top_right",
    14: "corner_outer_top_left",
    15: "wall_fill",
}

BORDER_MAPS_DEFAULT = {
    "TL": {14: "border_corner_inner_top_left",    15: "wall_fill"},
    "TR": {13: "border_corner_inner_top_right",   15: "wall_fill"},
    "BL": {11: "border_corner_inner_bottom_left", 15: "wall_fill"},
    "BR": { 7: "border_corner_inner_bottom_right", 15: "wall_fill"},
    "T":  {12: "border_wall_horizontal_bottom",
           13: "border_corner_outer_top_right",
           14: "corner_outer_top_left",            15: "wall_fill"},
    "B":  { 3: "border_wall_horizontal_top",
            7: "border_corner_outer_bottom_right",
           11: "corner_outer_bottom_left",         15: "wall_fill"},
    "L":  {10: "border_wall_vertical_right",
           11: "corner_outer_bottom_left",
           14: "border_corner_outer_top_left",     15: "wall_fill"},
    "R":  { 5: "border_wall_vertical_left",
            7: "corner_outer_bottom_right",
           13: "corner_outer_top_right",           15: "wall_fill"},
}


def _deep_copy_maps():
    corner = dict(CORNER_MAP_DEFAULT)
    border = {k: dict(v) for k, v in BORDER_MAPS_DEFAULT.items()}
    return corner, border


# ── Classe principale ─────────────────────────────────────────────────────────

class MazeDebuggerFallback:
    def __init__(self):
        pygame.init()
        self.window_w, self.window_h = 1200, 900
        self.screen = pygame.display.set_mode((self.window_w, self.window_h))
        pygame.display.set_caption("Maze Tile Placer — MODE FALLBACK   [Entrée = rapport]")

        self.font_debug  = pygame.font.SysFont("consolas", 8)
        self.font_label  = pygame.font.SysFont("consolas", 14)
        self.font_status = pygame.font.SysFont("consolas", 13)

        self.debug_mask = True
        self.dirty      = True
        self.zoom       = 2.0
        self.cam_x      = 20.0
        self.cam_y      = float(LABEL_H)
        self.dragging   = False
        self.last_pos   = (0, 0)
        self.hover_cx   = None
        self.hover_cy   = None

        self.corner_map, self.border_maps = _deep_copy_maps()

        self._load_sprites()

        self.grid   = self._build_wall_grid(MAZE_HEX)
        self.grid_h = len(self.grid)
        self.grid_w = len(self.grid[0])
        self.maze_w = self.grid_w * TILE_SIZE
        self.maze_h = self.grid_h * TILE_SIZE

        self.left_surf  = pygame.Surface((self.maze_w, self.maze_h))
        self.right_surf = pygame.Surface((self.maze_w, self.maze_h))
        self._build_reference_view()

    # ── Chargement sprites fallback ───────────────────────────────────────────

    def _load_sprites(self):
        sheet = SpriteSheet("__MISSING_ASSET__.png")   # force _fallback=True
        assert sheet._fallback, "Fallback non actif — vérifier SpriteSheet.__init__"
        print("✓ SpriteSheet en mode FALLBACK (asset absent intentionnellement)")

        macro_row   = COLORS["blue"][1]
        palette_idx = COLORS["blue"][0]

        self.tile_sprites = {
            name: sheet.get_small_sprite(macro_row, palette_idx, c, r, scale=SCALE)
            for name, (c, r) in MAZE_TILE.items()
        }
        self.tile_cycle = [None] + list(self.tile_sprites.keys())

    # ── Construction de la grille ─────────────────────────────────────────────

    def _build_wall_grid(self, maze_hex):
        h, w = len(maze_hex), len(maze_hex[0])
        grid = [[1] * (w * 2 + 1) for _ in range(h * 2 + 1)]
        for y in range(h):
            for x in range(w):
                cell = int(maze_hex[y][x], 16)
                gx, gy = x * 2 + 1, y * 2 + 1
                grid[gy][gx] = 0
                if not (cell & NORTH) and y > 0:     grid[gy - 1][gx] = 0
                if not (cell & EAST)  and x < w - 1: grid[gy][gx + 1] = 0
                if not (cell & SOUTH) and y < h - 1: grid[gy + 1][gx] = 0
                if not (cell & WEST)  and x > 0:     grid[gy][gx - 1] = 0
        return grid

    def _is_wall(self, gx, gy):
        return 0 <= gx < self.grid_w and 0 <= gy < self.grid_h and self.grid[gy][gx] == 1

    def _corner_mask(self, cx, cy):
        nw = self._is_wall(cx - 1, cy - 1)
        ne = self._is_wall(cx,     cy - 1)
        sw = self._is_wall(cx - 1, cy    )
        se = self._is_wall(cx,     cy    )
        return (nw << 3) | (ne << 2) | (sw << 1) | se

    def _border_type(self, cx, cy):
        t = cy == 1;             b = cy == self.grid_h - 1
        l = cx == 1;             r = cx == self.grid_w - 1
        if t and l: return "TL"
        if t and r: return "TR"
        if b and l: return "BL"
        if b and r: return "BR"
        if t: return "T"
        if b: return "B"
        if l: return "L"
        if r: return "R"
        return None

    def _active_map(self, cx, cy):
        if cx == 0 or cx == self.grid_w or cy == 0 or cy == self.grid_h:
            return None, None
        bt = self._border_type(cx, cy)
        if bt:
            return self.border_maps[bt], bt
        return self.corner_map, ""

    def _screen_to_grid(self, mx, my):
        px = (mx - self.cam_x) / self.zoom
        py = (my - self.cam_y) / self.zoom - LABEL_H
        cx = round(px / TILE_SIZE)
        cy = round(py / TILE_SIZE)
        if 0 <= cx <= self.grid_w and 0 <= cy <= self.grid_h:
            return cx, cy
        return None, None

    # ── Cyclage de tuile ──────────────────────────────────────────────────────

    def _cycle_tile(self, cx, cy, direction):
        amap, alabel = self._active_map(cx, cy)
        if amap is None:
            return
        mask = self._corner_mask(cx, cy)
        label = f"BORDER_{alabel}_MAP" if alabel else "CORNER_MAP"
        current = amap.get(mask)
        idx = self.tile_cycle.index(current) if current in self.tile_cycle else 0
        idx = (idx + direction) % len(self.tile_cycle)
        amap[mask] = self.tile_cycle[idx]
        self.dirty = True
        print(f"[{label}] mask {mask:2d} ({mask:04b}) → {self.tile_cycle[idx]}")

    # ── Rendu ─────────────────────────────────────────────────────────────────

    def _build_reference_view(self):
        self.right_surf.fill((0, 0, 0))
        for gy in range(self.grid_h):
            for gx in range(self.grid_w):
                if self.grid[gy][gx] == 1:
                    pygame.draw.rect(self.right_surf, (33, 33, 200),
                                     (gx * TILE_SIZE, gy * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    def _render_editor_view(self):
        self.left_surf.fill((0, 0, 0))
        half = TILE_SIZE // 2

        for cy in range(self.grid_h + 1):
            for cx in range(self.grid_w + 1):
                amap, alabel = self._active_map(cx, cy)
                if amap is None:
                    continue
                mask = self._corner_mask(cx, cy)
                name = amap.get(mask)
                px = cx * TILE_SIZE - half
                py = cy * TILE_SIZE - half

                if name and name in self.tile_sprites:
                    self.left_surf.blit(self.tile_sprites[name], (px, py))

                if self.debug_mask and mask > 0:
                    color = (255, 160, 0) if alabel else (255, 255, 0)
                    lbl = self.font_debug.render(
                        f"{alabel}{mask}" if alabel else str(mask), True, color
                    )
                    self.left_surf.blit(lbl, (px + 1, py + 1))

        if self.hover_cx is not None:
            hx = self.hover_cx * TILE_SIZE - half
            hy = self.hover_cy * TILE_SIZE - half
            pygame.draw.rect(self.left_surf, (255, 80, 0), (hx, hy, TILE_SIZE, TILE_SIZE), 2)

    def _draw_status_bar(self):
        pygame.draw.rect(self.screen, (30, 30, 40),
                         (0, self.window_h - STATUS_H, self.window_w, STATUS_H))
        if self.hover_cx is None:
            return
        amap, alabel = self._active_map(self.hover_cx, self.hover_cy)
        if amap is None:
            info  = f"  [skip] coin ({self.hover_cx},{self.hover_cy})"
            color = (120, 120, 120)
        else:
            mask  = self._corner_mask(self.hover_cx, self.hover_cy)
            tile  = amap.get(mask)
            idx   = self.tile_cycle.index(tile) if tile in self.tile_cycle else 0
            kind  = f"border {alabel}" if alabel else "inner"
            color = (255, 200, 120) if alabel else (200, 220, 255)
            info  = (f"  [{kind}] coin ({self.hover_cx},{self.hover_cy})"
                     f"  mask={mask} ({mask:04b})  [{idx}/{len(self.tile_cycle)-1}]"
                     f"  tile: {tile}")
        self.screen.blit(self.font_status.render(info, True, color),
                         (6, self.window_h - STATUS_H + 4))

    # ── Rapport terminal ──────────────────────────────────────────────────────

    def _print_report(self):
        SEP = "─" * 72
        print(f"\n{SEP}")
        print("  RAPPORT FALLBACK — CORNER_MAP")
        print(SEP)
        for mask in range(16):
            default = CORNER_MAP_DEFAULT.get(mask)
            current = self.corner_map.get(mask)
            changed = "  ← MODIFIÉ" if current != default else ""
            print(f"  mask {mask:2d} ({mask:04b})  {str(current):<40}{changed}")

        print(f"\n{SEP}")
        print("  RAPPORT FALLBACK — BORDER_MAPS")
        print(SEP)
        for zone, bmap in self.border_maps.items():
            default_bmap = BORDER_MAPS_DEFAULT[zone]
            for mask, tile in bmap.items():
                changed = "  ← MODIFIÉ" if tile != default_bmap.get(mask) else ""
                print(f"  [{zone}] mask {mask:2d} ({mask:04b})  {str(tile):<40}{changed}")

        if self.hover_cx is not None:
            print(f"\n{SEP}")
            print(f"  COIN SURVOLÉ : ({self.hover_cx}, {self.hover_cy})")
            amap, alabel = self._active_map(self.hover_cx, self.hover_cy)
            if amap is None:
                print("  → hors grille (ignoré par le renderer)")
            else:
                mask = self._corner_mask(self.hover_cx, self.hover_cy)
                tile = amap.get(mask)
                kind = f"border {alabel}" if alabel else "corner intérieur"
                print(f"  type     : {kind}")
                print(f"  mask     : {mask} ({mask:04b})")
                print(f"  tuile    : {tile}")
                if tile and tile in self.tile_sprites:
                    surf = self.tile_sprites[tile]
                    cx_px = surf.get_width() // 2
                    cy_px = surf.get_height() // 2
                    print(f"  pixel centre RGBA : {surf.get_at((cx_px, cy_px))}")
        print(f"{SEP}\n")

    # ── Boucle événements ─────────────────────────────────────────────────────

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_d:
                    self.debug_mask = not self.debug_mask
                    self.dirty = True
                elif event.key == pygame.K_RETURN:
                    self._print_report()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                cx, cy = self._screen_to_grid(*event.pos)
                if event.button == 1:
                    if cx is not None: self._cycle_tile(cx, cy, +1)
                    else: self.dragging, self.last_pos = True, event.pos
                elif event.button == 3:
                    if cx is not None: self._cycle_tile(cx, cy, -1)
                    else: self.dragging, self.last_pos = True, event.pos
                elif event.button == 2:
                    self.dragging, self.last_pos = True, event.pos

            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    dx = event.pos[0] - self.last_pos[0]
                    dy = event.pos[1] - self.last_pos[1]
                    self.cam_x += dx
                    self.cam_y += dy
                    self.last_pos = event.pos
                cx, cy = self._screen_to_grid(*event.pos)
                if (cx, cy) != (self.hover_cx, self.hover_cy):
                    self.hover_cx, self.hover_cy = cx, cy
                    self.dirty = True

            elif event.type == pygame.MOUSEWHEEL:
                mx, my = pygame.mouse.get_pos()
                wx = (mx - self.cam_x) / self.zoom
                wy = (my - self.cam_y) / self.zoom
                self.zoom = max(0.5, min(self.zoom + 0.2 * event.y, 10.0))
                self.cam_x = mx - wx * self.zoom
                self.cam_y = my - wy * self.zoom

        return True

    def update(self):
        if self.dirty:
            self._render_editor_view()
            self.dirty = False

    def draw(self):
        canvas_w = self.maze_w * 2 + GAP
        canvas_h = self.maze_h + LABEL_H
        canvas   = pygame.Surface((canvas_w, canvas_h))
        canvas.fill((10, 10, 15))

        canvas.blit(self.left_surf,  (0, LABEL_H))
        canvas.blit(self.right_surf, (self.maze_w + GAP, LABEL_H))
        canvas.blit(self.font_label.render("Fallback sprites [clic=cycler]", True, (200, 200, 200)), (4, 2))
        canvas.blit(self.font_label.render("Référence (solide)", True, (200, 200, 200)), (self.maze_w + GAP + 4, 2))

        self.screen.fill((10, 10, 15))
        scaled = pygame.transform.scale(
            canvas, (int(canvas_w * self.zoom), int(canvas_h * self.zoom))
        )
        self.screen.blit(scaled, (int(self.cam_x), int(self.cam_y)))
        self._draw_status_bar()
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        print("Prêt — Entrée: rapport terminal   D: masques   Échap: quitter")
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            clock.tick(60)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    MazeDebuggerFallback().run()
