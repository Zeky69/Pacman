import pygame
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

NORTH = 1
EAST  = 2
SOUTH = 4
WEST  = 8

MAZE_HEX = [
    "955517B",
    "8153816",
    "A838687",
    "AAA8387",
    "A846AAB",
    "C011406",
    "D6EC7C7",
]

def build_wall_grid(maze_hex):
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

            if not (cell & NORTH) and y > 0:        grid[gy - 1][gx] = 0
            if not (cell & EAST)  and x < w - 1:    grid[gy][gx + 1] = 0
            if not (cell & SOUTH) and y < h - 1:    grid[gy + 1][gx] = 0
            if not (cell & WEST)  and x > 0:        grid[gy][gx - 1] = 0

    return grid


SCALE = 4
TILE_SIZE = 8 * SCALE  # 32 px
DEBUG_MASK = True

pygame.init()
WINDOW_W, WINDOW_H = 1200, 900
screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
pygame.display.set_caption("Maze Tile Placer Debug")

font_debug  = pygame.font.SysFont("consolas", 8)
font_label  = pygame.font.SysFont("consolas", 14)
font_status = pygame.font.SysFont("consolas", 13)

from src.view.sprites import SpriteSheet
from src.view.settings import MAZE_TILE, COLORS

IMAGE_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets', 'default.png')
sheet = SpriteSheet(IMAGE_PATH)

macro_row   = COLORS['red'][1]
palette_idx = COLORS['red'][0]

tile_sprites = {
    name: sheet.get_small_sprite(macro_row, palette_idx, coords[0], coords[1], scale=SCALE)
    for name, coords in MAZE_TILE.items()
}

# Ordered list for cycling (None = empty slot)
TILE_CYCLE = [None] + list(tile_sprites.keys())

grid   = build_wall_grid(MAZE_HEX)
GRID_H = len(grid)
GRID_W = len(grid[0])

MAZE_W = GRID_W * TILE_SIZE
MAZE_H = GRID_H * TILE_SIZE
GAP    = 20
HALF   = TILE_SIZE // 2

# NW=8, NE=4, SW=2, SE=1
CORNER_MAP =  {
     0: None,
     1: 'corner_outer_top_left',
     2: 'corner_outer_top_right',
     3: 'wall_horizontal_top',
     4: 'corner_outer_bottom_left',
     5: 'wall_vertical_left',
     6: 'wall_fill',
     7: 'corner_inner_top_left',
     8: 'corner_outer_bottom_right',
     9: 'wall_fill',
    10: 'wall_vertical_right',
    11: 'corner_inner_top_right',
    12: 'wall_horizontal_bottom',
    13: 'corner_inner_bottom_left',
    14: 'corner_inner_bottom_right',
    15: 'wall_fill',
}

def is_wall(gx, gy):
    return 0 <= gx < GRID_W and 0 <= gy < GRID_H and grid[gy][gx] == 1

def corner_mask(cx, cy):
    nw = is_wall(cx - 1, cy - 1)
    ne = is_wall(cx,     cy - 1)
    sw = is_wall(cx - 1, cy    )
    se = is_wall(cx,     cy    )
    return (nw << 3) | (ne << 2) | (sw << 1) | se

def render_left(left, highlight_cx=None, highlight_cy=None):
    left.fill((0, 0, 0))
    for cy in range(GRID_H + 1):
        for cx in range(GRID_W + 1):
            mask = corner_mask(cx, cy)
            name = CORNER_MAP.get(mask)
            px = cx * TILE_SIZE - HALF
            py = cy * TILE_SIZE - HALF

            if name and name in tile_sprites:
                left.blit(tile_sprites[name], (px, py))

            if DEBUG_MASK and mask > 0:
                lbl = font_debug.render(str(mask), True, (255, 255, 0))
                left.blit(lbl, (px + 1, py + 1))

    if highlight_cx is not None and highlight_cy is not None:
        hx = highlight_cx * TILE_SIZE - HALF
        hy = highlight_cy * TILE_SIZE - HALF
        pygame.draw.rect(left, (255, 80, 0), (hx, hy, TILE_SIZE, TILE_SIZE), 2)

# --- Canvas droit : référence ---
right = pygame.Surface((MAZE_W, MAZE_H))
right.fill((0, 0, 0))
for gy in range(GRID_H):
    for gx in range(GRID_W):
        if grid[gy][gx] == 1:
            pygame.draw.rect(right, (33, 33, 222),
                             (gx * TILE_SIZE, gy * TILE_SIZE, TILE_SIZE, TILE_SIZE))

LABEL_H  = 20
STATUS_H = 24

left_surf = pygame.Surface((MAZE_W, MAZE_H))
render_left(left_surf)

zoom    = 2.0
cam_x   = 20.0
cam_y   = float(LABEL_H)
dragging  = False
last_pos  = (0, 0)
hover_cx  = None
hover_cy  = None
dirty     = False
clock     = pygame.time.Clock()

def screen_to_left_corner(mx, my):
    """Convertit une position écran en coin (cx, cy) dans le panneau gauche."""
    px = (mx - cam_x) / zoom
    py = (my - cam_y) / zoom - LABEL_H
    cx = round(px / TILE_SIZE)
    cy = round(py / TILE_SIZE)
    if 0 <= cx <= GRID_W and 0 <= cy <= GRID_H:
        return cx, cy
    return None, None

def cycle_tile(cx, cy, direction):
    global dirty
    mask = corner_mask(cx, cy)
    current = CORNER_MAP.get(mask)
    idx = TILE_CYCLE.index(current) if current in TILE_CYCLE else 0
    idx = (idx + direction) % len(TILE_CYCLE)
    CORNER_MAP[mask] = TILE_CYCLE[idx]
    dirty = True
    print(f"mask {mask:2d} ({mask:04b}) → {TILE_CYCLE[idx]}")
    print("CORNER_MAP = {")
    for k in sorted(CORNER_MAP):
        print(f"    {k:2d}: {repr(CORNER_MAP[k])},")
    print("}")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_d:
                DEBUG_MASK = not DEBUG_MASK
                dirty = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                cx, cy = screen_to_left_corner(*event.pos)
                if cx is not None:
                    cycle_tile(cx, cy, +1)
                else:
                    dragging = True
                    last_pos = event.pos
            elif event.button == 3:
                cx, cy = screen_to_left_corner(*event.pos)
                if cx is not None:
                    cycle_tile(cx, cy, -1)
                else:
                    dragging = True
                    last_pos = event.pos
            elif event.button == 2:
                dragging = True
                last_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                dx = event.pos[0] - last_pos[0]
                dy = event.pos[1] - last_pos[1]
                cam_x += dx
                cam_y += dy
                last_pos = event.pos
            cx, cy = screen_to_left_corner(*event.pos)
            if (cx, cy) != (hover_cx, hover_cy):
                hover_cx, hover_cy = cx, cy
                dirty = True
        elif event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            world_x = (mx - cam_x) / zoom
            world_y = (my - cam_y) / zoom
            zoom = max(0.5, min(zoom + 0.2 * event.y, 10.0))
            cam_x = mx - world_x * zoom
            cam_y = my - world_y * zoom

    if dirty:
        render_left(left_surf, hover_cx, hover_cy)
        dirty = False

    # Assemble canvas
    canvas_w = MAZE_W * 2 + GAP
    canvas_h = MAZE_H + LABEL_H
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((10, 10, 15))
    canvas.blit(left_surf, (0, LABEL_H))
    canvas.blit(right,     (MAZE_W + GAP, LABEL_H))
    canvas.blit(font_label.render("Sprites [clic=cycler]", True, (200, 200, 200)), (4, 2))
    canvas.blit(font_label.render("Référence",             True, (200, 200, 200)), (MAZE_W + GAP + 4, 2))

    screen.fill((10, 10, 15))
    scaled = pygame.transform.scale(canvas, (int(canvas_w * zoom), int(canvas_h * zoom)))
    screen.blit(scaled, (int(cam_x), int(cam_y)))

    # Barre de statut (hors zoom)
    if hover_cx is not None:
        mask = corner_mask(hover_cx, hover_cy)
        tile = CORNER_MAP.get(mask)
        idx  = TILE_CYCLE.index(tile) if tile in TILE_CYCLE else 0
        info = f"  corner ({hover_cx},{hover_cy})  mask={mask} ({mask:04b})  [{idx}/{len(TILE_CYCLE)-1}]  tile: {tile}"
        pygame.draw.rect(screen, (30, 30, 40), (0, WINDOW_H - STATUS_H, WINDOW_W, STATUS_H))
        screen.blit(font_status.render(info, True, (200, 220, 255)), (6, WINDOW_H - STATUS_H + 4))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
