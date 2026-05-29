import pygame
import sys
import os

racine = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(racine)

from src.view.settings import PACMAN_ANIMATIONS, GHOST_ANIMATIONS, COLORS, FOOD, GOMMES_TILES
from src.view.sprites import SpriteSheet

# --- 3. CLASSES DE TEST ---
class AnimatorTester:
    """Gère les objets animés (Pac-Man, Fantômes)."""
    def __init__(self, name, data, sheet, palette_index=0, macro_row=0, scale=3):
        self.name = name
        self.frames = []
        self.loop_type = data['loop_type']
        self.index = 0
        self.last_update = pygame.time.get_ticks()
        self.speed = 100
        self.finished = False

        temp_frames = []
        for col, row in data['frame']:
            img = sheet.get_large_sprite(macro_row, palette_index, col, row, scale)
            if data['x_flip'] or data['y_flip']:
                img = pygame.transform.flip(img, data['x_flip'], data['y_flip'])
            if data['rotation'] != 0:
                img = pygame.transform.rotate(img, data['rotation'])
            temp_frames.append(img)

        if self.loop_type == 'pingpong' and len(temp_frames) > 2:
            for i in range(len(temp_frames) - 2, 0, -1):
                temp_frames.append(temp_frames[i])
                
        self.frames = temp_frames
        self.image = self.frames[self.index]

    def update(self, now):
        if now - self.last_update > self.speed:
            self.last_update = now
            if self.loop_type == 'once':
                if self.index < len(self.frames) - 1:
                    self.index += 1
                else:
                    self.finished = True
            else:
                self.index = (self.index + 1) % len(self.frames)
            self.image = self.frames[self.index]

    def draw(self, surface, x, y, font):
        rect = self.image.get_rect(center=(x, y))
        surface.blit(self.image, rect)
        text = font.render(self.name, True, (255, 255, 255))
        surface.blit(text, text.get_rect(center=(x, y + 40)))

class StaticTester:
    """Gère les objets fixes (Fruits, Pac-gommes)."""
    def __init__(self, name, col, row, sheet, is_large=True, scale=3):
        self.name = name
        if is_large:
            self.image = sheet.get_large_sprite(0, 0, col, row, scale)
        else:
            self.image = sheet.get_small_sprite(0, 0, col, row, scale)

    def update(self, now):
        pass # Pas d'animation nécessaire

    def draw(self, surface, x, y, font):
        rect = self.image.get_rect(center=(x, y))
        surface.blit(self.image, rect)
        text = font.render(self.name, True, (200, 200, 255))
        surface.blit(text, text.get_rect(center=(x, y + 40)))

# --- 4. INITIALISATION ---
pygame.init()
screen = pygame.display.set_mode((1200, 900)) # Écran plus grand !
pygame.display.set_caption("Galerie Complète des Sprites Pac-Man")
font = pygame.font.SysFont("Arial", 14, bold=True)
clock = pygame.time.Clock()

try:
    sheet = SpriteSheet("assets/default.png")
except:
    print("Erreur : l'image 'assets/default.png' est introuvable.")
    sys.exit()

testers = []

# 1. Ajouter toutes les animations de Pac-Man
for name, data in PACMAN_ANIMATIONS.items():
    testers.append(AnimatorTester(f"Pac: {name}", data, sheet, palette_index=2, macro_row=1))

# 2. Ajouter toutes les directions d'un fantôme de base
for name, data in GHOST_ANIMATIONS.items():
    testers.append(AnimatorTester(f"Ghost Dir: {name}", data, sheet))

# 3. TEST DES COULEURS (Palettes) : On affiche le fantôme 'right' pour chaque couleur
for color_name, (pal_idx, mac_row) in COLORS.items():
    testers.append(AnimatorTester(f"Color: {color_name}", GHOST_ANIMATIONS['right'], sheet, palette_index=pal_idx, macro_row=mac_row))

# 4. Ajouter la nourriture (Fruits) -> Grands sprites (16x16)
for name, coords in FOOD.items():
    testers.append(StaticTester(f"Food: {name}", coords[0], coords[1], sheet, is_large=True))

# 5. Ajouter les Pac-gommes -> Petits sprites (8x8)
for name, coords in GOMMES_TILES.items():
    testers.append(StaticTester(f"Dot: {name}", coords[0], coords[1], sheet, is_large=False))

# --- 5. BOUCLE PRINCIPALE ---
running = True
while running:
    now = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            for t in testers:
                if hasattr(t, 'loop_type') and t.loop_type == 'once':
                    t.index = 0
                    t.finished = False

    screen.fill((20, 20, 30))

    # Grille d'affichage dynamique
    start_x, start_y = 80, 80
    spacing_x, spacing_y = 130, 110
    current_x, current_y = start_x, start_y

    for tester in testers:
        tester.update(now)
        tester.draw(screen, current_x, current_y, font)
        
        current_x += spacing_x
        if current_x > screen.get_width() - 80:
            current_x = start_x
            current_y += spacing_y

    info_text = font.render("ESPACE = Relancer les morts | Voici TOUT ton univers Pac-Man !", True, (255, 255, 0))
    screen.blit(info_text, (20, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()