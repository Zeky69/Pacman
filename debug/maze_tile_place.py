import sys
from pathlib import Path
import pygame

# --- 1. Configuration des chemins et imports ---
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Imports spécifiques à ton projet
from src.view.sprites import SpriteSheet
from src.view.settings import MAZE_TILE, COLORS

# --- 2. Constantes ---
NORTH = 1
EAST  = 2
SOUTH = 4
WEST  = 8

SCALE = 4
TILE_SIZE = 8 * SCALE  # 32 px
GAP = 20
LABEL_H = 20
STATUS_H = 24

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
    "C545545456C54555545444556"
]

# --- 3. Dictionnaires de Mapping ---
CORNER_MAP =  {
     0: None, 1: 'corner_outer_top_left', 2: 'corner_outer_top_right', 3: 'wall_horizontal_top',
     4: 'corner_outer_bottom_left', 5: 'wall_vertical_left', 6: 'wall_fill', 7: 'corner_inner_top_left',
     8: 'corner_outer_bottom_right', 9: 'wall_fill', 10: 'wall_vertical_right', 11: 'corner_inner_top_right',
     12: 'wall_horizontal_bottom', 13: 'corner_inner_bottom_left', 14: 'corner_inner_bottom_right', 15: 'wall_fill',
}

BORDER_MAPS = {
    'TL': {14: 'border_corner_outer_top_left', 15: 'wall_fill'},
    'TR': {13: 'border_corner_outer_top_right', 15: 'wall_fill'},
    'BL': {11: 'border_corner_outer_bottom_left', 15: 'wall_fill'},
    'BR': { 7: 'border_corner_inner_top_left', 15: 'wall_fill'},
    'T':  {12: 'border_wall_horizontal_bottom', 13: 'border_corner_inner_bottom_left', 14: 'border_corner_inner_bottom_right', 15: 'wall_fill'},
    'B':  { 3: 'border_wall_horizontal_top', 7: 'border_corner_outer_bottom_right', 11: 'border_corner_inner_top_right', 15: 'wall_fill'},
    'L':  {10: 'border_wall_vertical_right', 11: 'border_corner_inner_top_right_bottom', 14: 'border_corner_inner_bottom_right_top', 15: 'wall_fill'},
    'R':  { 5: 'border_wall_vertical_left', 7: 'border_corner_inner_top_left_bottom', 13: 'border_corner_inner_bottom_left_top', 15: 'wall_fill'},
}

# --- 4. Classe Principale ---
class MazeDebugger:
    def __init__(self):
        pygame.init()
        self.window_w, self.window_h = 1200, 900
        self.screen = pygame.display.set_mode((self.window_w, self.window_h))
        pygame.display.set_caption("Maze Tile Placer Debug - POO Version")

        # Polices
        self.font_debug  = pygame.font.SysFont("consolas", 8)
        self.font_label  = pygame.font.SysFont("consolas", 14)
        self.font_status = pygame.font.SysFont("consolas", 13)

        # État et Options
        self.debug_mask = True
        self.dirty = True
        self.zoom = 2.0
        self.cam_x = 20.0
        self.cam_y = float(LABEL_H)
        self.dragging = False
        self.last_pos = (0, 0)
        self.hover_cx = None
        self.hover_cy = None

        # Chargement des ressources
        self.load_sprites()
        
        # Données de la carte
        self.grid = self.build_wall_grid(MAZE_HEX)
        self.grid_h = len(self.grid)
        self.grid_w = len(self.grid[0])
        self.maze_w = self.grid_w * TILE_SIZE
        self.maze_h = self.grid_h * TILE_SIZE

        # Surfaces
        self.left_surf = pygame.Surface((self.maze_w, self.maze_h))
        self.right_surf = pygame.Surface((self.maze_w, self.maze_h))
        self.build_reference_view()

    def load_sprites(self):
        image_path = BASE_DIR / 'assets' / 'default.png'
        sheet = SpriteSheet(str(image_path))
        
        macro_row = COLORS['pink'][1]
        palette_idx = COLORS['pink'][0]

        self.tile_sprites = {
            name: sheet.get_small_sprite(macro_row, palette_idx, coords[0], coords[1], scale=SCALE)
            for name, coords in MAZE_TILE.items()
        }
        self.tile_cycle = [None] + list(self.tile_sprites.keys())

    def build_wall_grid(self, maze_hex):
        h = len(maze_hex)
        w = len(maze_hex[0])
        h_ext = h * 2 + 1
        w_ext = w * 2 + 1
        grid = [[1] * w_ext for _ in range(h_ext)]

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

    def is_wall(self, gx, gy):
        return 0 <= gx < self.grid_w and 0 <= gy < self.grid_h and self.grid[gy][gx] == 1

    def get_corner_mask(self, cx, cy):
        nw = self.is_wall(cx - 1, cy - 1)
        ne = self.is_wall(cx,     cy - 1)
        sw = self.is_wall(cx - 1, cy    )
        se = self.is_wall(cx,     cy    )
        return (nw << 3) | (ne << 2) | (sw << 1) | se

    def get_border_type(self, cx, cy):
        on_t = cy == 1
        on_b = cy == self.grid_h - 1
        on_l = cx == 1
        on_r = cx == self.grid_w - 1
        
        if on_t and on_l: return 'TL'
        if on_t and on_r: return 'TR'
        if on_b and on_l: return 'BL'
        if on_b and on_r: return 'BR'
        if on_t: return 'T'
        if on_b: return 'B'
        if on_l: return 'L'
        if on_r: return 'R'
        return None

    def get_active_map(self, cx, cy):
        if cx == 0 or cx == self.grid_w or cy == 0 or cy == self.grid_h:
            return None, None
            
        bt = self.get_border_type(cx, cy)
        if bt is not None:
            return BORDER_MAPS[bt], bt
        return CORNER_MAP, ''

    def screen_to_grid(self, mx, my):
        px = (mx - self.cam_x) / self.zoom
        py = (my - self.cam_y) / self.zoom - LABEL_H
        cx = round(px / TILE_SIZE)
        cy = round(py / TILE_SIZE)
        
        if 0 <= cx <= self.grid_w and 0 <= cy <= self.grid_h:
            return cx, cy
        return None, None

    def cycle_tile(self, cx, cy, direction):
        target, tlabel = self.get_active_map(cx, cy)
        if target is None:
            return
            
        mask = self.get_corner_mask(cx, cy)
        label = f"BORDER_{tlabel}_MAP" if tlabel else "CORNER_MAP"
        current = target.get(mask)
        
        idx = self.tile_cycle.index(current) if current in self.tile_cycle else 0
        idx = (idx + direction) % len(self.tile_cycle)
        target[mask] = self.tile_cycle[idx]
        self.dirty = True
        
        print(f"[{label}] mask {mask:2d} ({mask:04b}) → {self.tile_cycle[idx]}")

    def build_reference_view(self):
        self.right_surf.fill((0, 0, 0))
        for gy in range(self.grid_h):
            for gx in range(self.grid_w):
                if self.grid[gy][gx] == 1:
                    pygame.draw.rect(self.right_surf, (33, 33, 222),
                                     (gx * TILE_SIZE, gy * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    def render_editor_view(self):
        self.left_surf.fill((0, 0, 0))
        half = TILE_SIZE // 2
        
        for cy in range(self.grid_h + 1):
            for cx in range(self.grid_w + 1):
                amap, alabel = self.get_active_map(cx, cy)
                if amap is None: continue
                
                mask = self.get_corner_mask(cx, cy)
                name = amap.get(mask)
                px = cx * TILE_SIZE - half
                py = cy * TILE_SIZE - half

                if name and name in self.tile_sprites:
                    self.left_surf.blit(self.tile_sprites[name], (px, py))

                if self.debug_mask and mask > 0:
                    color = (255, 160, 0) if alabel else (255, 255, 0)
                    lbl = self.font_debug.render(f"{alabel}{mask}" if alabel else str(mask), True, color)
                    self.left_surf.blit(lbl, (px + 1, py + 1))

        # Highlight du survol
        if self.hover_cx is not None and self.hover_cy is not None:
            hx = self.hover_cx * TILE_SIZE - half
            hy = self.hover_cy * TILE_SIZE - half
            pygame.draw.rect(self.left_surf, (255, 80, 0), (hx, hy, TILE_SIZE, TILE_SIZE), 2)

    def draw_status_bar(self):
        pygame.draw.rect(self.screen, (30, 30, 40), (0, self.window_h - STATUS_H, self.window_w, STATUS_H))
        
        if self.hover_cx is not None:
            target, tlabel = self.get_active_map(self.hover_cx, self.hover_cy)
            if target is None:
                info = f"  [skip] corner ({self.hover_cx},{self.hover_cy})"
                color = (120, 120, 120)
            else:
                mask = self.get_corner_mask(self.hover_cx, self.hover_cy)
                tile = target.get(mask)
                idx = self.tile_cycle.index(tile) if tile in self.tile_cycle else 0
                kind = f"border {tlabel}" if tlabel else "inner"
                color = (255, 200, 120) if tlabel else (200, 220, 255)
                info = f"  [{kind}] corner ({self.hover_cx},{self.hover_cy})  mask={mask} ({mask:04b})  [{idx}/{len(self.tile_cycle)-1}]  tile: {tile}"
            
            self.screen.blit(self.font_status.render(info, True, color), (6, self.window_h - STATUS_H + 4))

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
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                cx, cy = self.screen_to_grid(*event.pos)
                if event.button == 1: # Clic gauche
                    if cx is not None: self.cycle_tile(cx, cy, +1)
                    else: self.dragging, self.last_pos = True, event.pos
                elif event.button == 3: # Clic droit
                    if cx is not None: self.cycle_tile(cx, cy, -1)
                    else: self.dragging, self.last_pos = True, event.pos
                elif event.button == 2: # Molette (Drag)
                    self.dragging, self.last_pos = True, event.pos
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging = False
                
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    dx, dy = event.pos[0] - self.last_pos[0], event.pos[1] - self.last_pos[1]
                    self.cam_x += dx
                    self.cam_y += dy
                    self.last_pos = event.pos
                    
                cx, cy = self.screen_to_grid(*event.pos)
                if (cx, cy) != (self.hover_cx, self.hover_cy):
                    self.hover_cx, self.hover_cy = cx, cy
                    self.dirty = True
                    
            elif event.type == pygame.MOUSEWHEEL:
                mx, my = pygame.mouse.get_pos()
                world_x = (mx - self.cam_x) / self.zoom
                world_y = (my - self.cam_y) / self.zoom
                self.zoom = max(0.5, min(self.zoom + 0.2 * event.y, 10.0))
                self.cam_x = mx - world_x * self.zoom
                self.cam_y = my - world_y * self.zoom

        return True

    def update(self):
        if self.dirty:
            self.render_editor_view()
            self.dirty = False

    def draw(self):
        # 1. Préparation du canvas composite
        canvas_w = self.maze_w * 2 + GAP
        canvas_h = self.maze_h + LABEL_H
        canvas = pygame.Surface((canvas_w, canvas_h))
        canvas.fill((10, 10, 15))
        
        # 2. Blit des sous-surfaces
        canvas.blit(self.left_surf, (0, LABEL_H))
        canvas.blit(self.right_surf, (self.maze_w + GAP, LABEL_H))
        canvas.blit(self.font_label.render("Sprites [clic=cycler]", True, (200, 200, 200)), (4, 2))
        canvas.blit(self.font_label.render("Référence", True, (200, 200, 200)), (self.maze_w + GAP + 4, 2))

        # 3. Rendu final à l'écran avec zoom et caméra
        self.screen.fill((10, 10, 15))
        scaled = pygame.transform.scale(canvas, (int(canvas_w * self.zoom), int(canvas_h * self.zoom)))
        self.screen.blit(scaled, (int(self.cam_x), int(self.cam_y)))

        # 4. Interface statique (Barre d'état)
        self.draw_status_bar()
        
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            clock.tick(60)
            
        pygame.quit()
        sys.exit()

# --- 5. Lancement ---
if __name__ == "__main__":
    app = MazeDebugger()
    app.run()