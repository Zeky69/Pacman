import pygame
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

SCALE = 4
SPRITE_SIZE = 8 * SCALE  # 32px
COLS = 5
PADDING = 12
FONT_SIZE = 10
LABEL_H = 28
CELL_W = 160
CELL_H = SPRITE_SIZE + LABEL_H + PADDING

pygame.init()
WINDOW_W, WINDOW_H = 1100, 750
screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
pygame.display.set_caption("Maze Tiles Debug")
font = pygame.font.SysFont("consolas", FONT_SIZE)

from src.view.sprites import SpriteSheet
from src.view.settings import COLORS, MAZE_TILE

IMAGE_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets', 'default.png')
sheet = SpriteSheet(IMAGE_PATH)

tiles = list(MAZE_TILE.items())
n_rows = (len(tiles) + COLS - 1) // COLS
canvas_w = COLS * CELL_W + PADDING
canvas_h = n_rows * CELL_H + PADDING

canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill((25, 25, 35))

for i, (name, coords) in enumerate(tiles):
    ci = i % COLS
    ri = i // COLS
    x = PADDING + ci * CELL_W
    y = PADDING + ri * CELL_H

    sprite = sheet.get_small_sprite(macro_row=COLORS['blue'][1], palette_index=COLORS['blue'][0], col=coords[0], row=coords[1], scale=SCALE)
    canvas.blit(sprite, (x, y))

    label = font.render(name, True, (200, 200, 220))
    canvas.blit(label, (x, y + SPRITE_SIZE + 4))

zoom = 1.0
cam_x, cam_y = 20.0, 20.0
dragging = False
last_pos = (0, 0)

clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            dragging = True
            last_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            dragging = False
        elif event.type == pygame.MOUSEMOTION and dragging:
            dx = event.pos[0] - last_pos[0]
            dy = event.pos[1] - last_pos[1]
            cam_x += dx
            cam_y += dy
            last_pos = event.pos
        elif event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            cx = (mx - cam_x) / zoom
            cy = (my - cam_y) / zoom
            zoom = max(0.4, min(zoom + 0.15 * event.y, 8.0))
            cam_x = mx - cx * zoom
            cam_y = my - cy * zoom

    screen.fill((15, 15, 20))
    scaled = pygame.transform.scale(canvas, (int(canvas_w * zoom), int(canvas_h * zoom)))
    screen.blit(scaled, (int(cam_x), int(cam_y)))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
