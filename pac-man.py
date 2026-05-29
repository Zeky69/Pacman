import pygame
import sys

from src.view.sprites import SpriteSheet 

pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Test d'affichage des Sprites")

IMAGE_PATH = "assets/default.png"
sheet = SpriteSheet(IMAGE_PATH)

pacman_image = sheet.get_large_sprite(macro_row=0, palette_index=0, col=2, row=0, scale=4)

ghost_blue = sheet.get_large_sprite(macro_row=0, palette_index=1, col=6, row=0, scale=4)

letter_o = sheet.get_small_sprite(macro_row=0, palette_index=0, col=0, row=2, scale=4)


# --- BOUCLE PRINCIPALE ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((20, 10, 30))

    screen.blit(pacman_image, (150, 150))
    screen.blit(ghost_blue, (250, 150))
    screen.blit(letter_o, (350, 166))
    pygame.display.flip()

pygame.quit()
sys.exit()