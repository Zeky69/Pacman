import pygame
import sys

# --- CONFIGURATION ---
SMALL_BLOCK = {
    'cols': 22, 'rows': 9, 'cell_w': 8, 'cell_h': 8, 
    'cell_margin': 1, 'block_w': 199, 'block_margin': 1
}

LARGE_BLOCK = {
    'cols': 10, 'rows': 6, 'cell_w': 16, 'cell_h': 16, 
    'cell_margin': 1, 'block_w': 171, 'palette_w': 27, 'block_margin': 2
}
def draw_small_grid(surface, start_y):
    for table in range(5):
        start_x = table * (SMALL_BLOCK['block_w'] + SMALL_BLOCK['block_margin'])
        for row in range(SMALL_BLOCK['rows']):
            for col in range(SMALL_BLOCK['cols']):
                x = start_x + SMALL_BLOCK['cell_margin'] + col * (SMALL_BLOCK['cell_w'] + SMALL_BLOCK['cell_margin'])
                y = start_y + SMALL_BLOCK['cell_margin'] + row * (SMALL_BLOCK['cell_h'] + SMALL_BLOCK['cell_margin'])
                
                # MODIFICATION ICI : On englobe le sprite en dessinant sur la marge (-1, +2)
                rect = pygame.Rect(x - 1, y - 1, SMALL_BLOCK['cell_w'] + 2, SMALL_BLOCK['cell_h'] + 2)
                pygame.draw.rect(surface, (255, 0, 0), rect, 1)

def draw_large_grid(surface, start_y):
    for table in range(5):
        section_w = LARGE_BLOCK['block_w'] + LARGE_BLOCK['palette_w'] + LARGE_BLOCK['block_margin']
        start_x = table * section_w
        for row in range(LARGE_BLOCK['rows']):
            for col in range(LARGE_BLOCK['cols']):
                x = start_x + LARGE_BLOCK['cell_margin'] + col * (LARGE_BLOCK['cell_w'] + LARGE_BLOCK['cell_margin'])
                y = start_y + LARGE_BLOCK['cell_margin'] + row * (LARGE_BLOCK['cell_h'] + LARGE_BLOCK['cell_margin'])
                
                # MODIFICATION ICI : On englobe le sprite en dessinant sur la marge (-1, +2)
                rect = pygame.Rect(x - 1, y - 1, LARGE_BLOCK['cell_w'] + 2, LARGE_BLOCK['cell_h'] + 2)
                pygame.draw.rect(surface, (255, 0, 0), rect, 1)
# --- INITIALISATION ---
pygame.init()
IMAGE_PATH = "assets/default.png"

try:
    sprite_sheet = pygame.image.load(IMAGE_PATH)
except pygame.error:
    print(f"Erreur : Impossible de trouver {IMAGE_PATH}.")
    sys.exit()

# Taille de la fenêtre (fixe, pour pouvoir se déplacer à l'intérieur)
WINDOW_WIDTH, WINDOW_HEIGHT = 1024, 768
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Débogueur de Sprites - Molette: Zoom | Clic Gauche: Déplacer")

# OPTIMISATION : On dessine la grille UNE SEULE FOIS sur une copie de l'image
canvas = sprite_sheet.copy()
for y in range(4):
	draw_small_grid(canvas, start_y=0+(y *186))
	draw_large_grid(canvas, start_y=82+(y *186)) 
# Décommente et ajuste quand tu auras validé les premières lignes :
# draw_small_grid(canvas, start_y=187)

# --- VARIABLES DE CAMERA (Zoom & Pan) ---
zoom = 2.0   
cam_x = 0.0
cam_y = 0.0 
dragging = False
last_mouse_pos = (0, 0)

# --- BOUCLE PRINCIPALE ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # 1. GESTION DU DÉPLACEMENT (Clic & Glisse)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Clic gauche
                dragging = True
                last_mouse_pos = event.pos
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: # Relâchement du clic gauche
                dragging = False
                
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                mouse_x, mouse_y = event.pos
                dx = mouse_x - last_mouse_pos[0]
                dy = mouse_y - last_mouse_pos[1]
                cam_x += dx
                cam_y += dy
                last_mouse_pos = event.pos
                
        # 2. GESTION DU ZOOM (Molette souris)
        elif event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # On calcule où pointe la souris sur l'image AVANT le zoom
            canvas_mouse_x = (mouse_x - cam_x) / zoom
            canvas_mouse_y = (mouse_y - cam_y) / zoom

            # Changement du zoom
            if event.y > 0:
                zoom += 0.5  # Zoom avant
            elif event.y < 0:
                zoom -= 0.5  # Zoom arrière
                
            # Limites du zoom (pour ne pas crasher)
            zoom = max(0.5, min(zoom, 20.0))

            # On ajuste la caméra pour que le zoom se fasse vers le curseur de la souris
            cam_x = mouse_x - (canvas_mouse_x * zoom)
            cam_y = mouse_y - (canvas_mouse_y * zoom)

    # --- AFFICHAGE ---
    screen.fill((30, 30, 30)) # Fond gris foncé pour bien voir les bords

    # On redimensionne le canvas selon le zoom actuel
    new_w = int(canvas.get_width() * zoom)
    new_h = int(canvas.get_height() * zoom)
    scaled_canvas = pygame.transform.scale(canvas, (new_w, new_h))
    
    # On affiche le canvas redimensionné à la position de la caméra
    screen.blit(scaled_canvas, (cam_x, cam_y))
    
    pygame.display.flip()

pygame.quit()
sys.exit()