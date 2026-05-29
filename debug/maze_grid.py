import pygame
import sys
import os

# --- GESTION DES CHEMINS ---
racine = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(racine)

# --- DICTIONNAIRE DES TUILES ---
MAZE_TILE = {
    "corner_top_left": (16, 0),
    "corner_top_right": (18, 0),
    "corner_down_left": (16, 2),
    "corner_down_right": (18, 2),
    "horizontal_up": (17, 0),
    "horizontal_down": (17, 2),
    "vertical_left": (16, 1),
    "vertical_right": (18, 1),
 
    "border_corner_top_left": (16, 3),
    "border_corner_top_right": (19, 3),
    "border_corner_down_left": (16, 6),
    "border_corner_down_right": (19, 6),
    "border_horizontal_up": (20, 2),
    "border_horizontal_down": (20, 0),
    "border_vertical_left": (21, 1),
    "border_vertical_right": (19, 1),
 
    "border_horizontal_top_left_inner": (17, 3),
    "border_horizontal_top_right_inner": (18, 3),
    "border_horizontal_down_left_inner": (17, 6),
    "border_horizontal_down_right_inner": (18, 6),
 
    "border_vertical_left_down_inner": (16, 4),
    "border_vertical_left_up_inner": (16, 5),
    "border_vertical_right_down_inner": (19, 4),
    "border_vertical_right_up_inner": (19, 5),
 
    "cross_left_top": (17, 4),
    "cross_left_down": (17, 5),
    "cross_right_top": (18, 4),
    "cross_right_down": (18, 5),
}

# --- 1. LE MODÈLE (Logique et Auto-tiling) ---
class MazeModel:
    def __init__(self, raw_data):
        # Transformation du texte Hexadécimal en une grille d'entiers
        self.grid = []
        for line in raw_data.strip().split('\n'):
            row = [int(char, 16) for char in line.strip()]
            self.grid.append(row)
            
        self.rows = len(self.grid)
        self.cols = len(self.grid[0]) if self.rows > 0 else 0

    def get_cell_value(self, r, c):
        """Retourne la valeur binaire du mur de la cellule, ou 0 si hors limites."""
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return self.grid[r][c]
        return 0

    def determine_tile_name(self, r, c):
        """Détermine le nom exact de la tuile en analysant la cellule et ses voisins."""
        val = self.grid[r][c]
        
        # Si la case est vide
        if val == 0:
            return None 

        # Correspondance de base selon le Bitmask (1=N, 2=E, 4=S, 8=W)
        base_tiles = {
            1: "horizontal_up",
            2: "vertical_right",
            4: "horizontal_down",
            8: "vertical_left",
            3: "corner_top_right",
            6: "corner_down_right",
            9: "corner_top_left",
            12: "corner_down_left"
        }
        
        tile_name = base_tiles.get(val, "unknown")
        if tile_name == "unknown":
            return None # Ignore les formes non définies pour ce test

        # Est-on sur le bord de la carte ?
        is_border = (r == 0 or r == self.rows - 1 or c == 0 or c == self.cols - 1)

        # Récupération des murs voisins pour l'Auto-tiling
        neighbor_north = self.get_cell_value(r - 1, c)
        neighbor_south = self.get_cell_value(r + 1, c)
        neighbor_east  = self.get_cell_value(r, c + 1)
        neighbor_west  = self.get_cell_value(r, c - 1)

        # --- Logique Contextuelle ---
        # Exemple 1 : Transformation des coins (9, 3) en croix si connectés
        if val == 9: # Coin Haut-Gauche
            if neighbor_north & 4: # Le voisin du haut a un mur vers le bas
                tile_name = "cross_left_top"
        elif val == 3: # Coin Haut-Droite
            if neighbor_north & 4: 
                tile_name = "cross_right_top"
        elif val == 12: # Coin Bas-Gauche
            if neighbor_south & 1: # Le voisin du bas a un mur vers le haut
                tile_name = "cross_left_down"
        elif val == 6: # Coin Bas-Droite
            if neighbor_south & 1: 
                tile_name = "cross_right_down"

        # Exemple 2 : Gestion des Bords (Borders et Inner-borders)
        if is_border and "cross" not in tile_name:
            if tile_name == "horizontal_up" and (neighbor_south & 1):
                tile_name = "border_horizontal_top_left_inner"
            elif tile_name == "horizontal_down" and (neighbor_north & 4):
                tile_name = "border_horizontal_down_left_inner"
            else:
                # Ajout du préfixe classique pour les bords normaux
                tile_name = f"border_{tile_name}"

        return tile_name


# --- 2. LA VUE (Affichage Pygame) ---
class MazeView:
    def __init__(self, tiles_images, scale=4):
        self.tiles_images = tiles_images
        self.tile_size = 8 * scale

    def draw(self, screen, model, offset_x=0, offset_y=0):
        for r in range(model.rows):
            for c in range(model.cols):
                
                # On demande au modèle la tuile précise (avec l'auto-tiling)
                tile_name = model.determine_tile_name(r, c)
                
                if not tile_name:
                    continue # On ignore le vide

                pos_x = offset_x + c * self.tile_size
                pos_y = offset_y + r * self.tile_size

                # Affichage de l'image si elle existe, sinon rectangle coloré
                if tile_name in self.tiles_images:
                    screen.blit(self.tiles_images[tile_name], (pos_x, pos_y))
                else:
                    color = (255, 100, 100) if "cross" in tile_name else (255, 0, 255)
                    pygame.draw.rect(screen, color, (pos_x, pos_y, self.tile_size, self.tile_size), 2)


# --- 3. INITIALISATION ET BOUCLE PRINCIPALE ---
pygame.init()
SCALE = 4
screen = pygame.display.set_mode((1000, 800))
pygame.display.set_caption("Labyrinthe Contextuel Complet")

# 3.1 Chargement des Assets
tiles_images = {}
try:
    from src.view.settings import COLORS
    from src.view.sprites import SpriteSheet
    
    sheet = SpriteSheet("assets/default.png")
    for name, (col, row) in MAZE_TILE.items():
        tiles_images[name] = sheet.get_small_sprite(
            macro_row=COLORS['blue'][1], 
            palette_index=COLORS['blue'][0], 
            col=col, 
            row=row, 
            scale=SCALE
        )
    print("Sprites chargés avec succès.")
except Exception as e:
    print(f"Mode Fallback activé (Erreur d'import : {e})")
    # Génération procédurale de tuiles pour tester sans les images
    for name in MAZE_TILE.keys():
        surf = pygame.Surface((8 * SCALE, 8 * SCALE), pygame.SRCALPHA)
        color = (30, 80, 200) if "border" in name else (100, 150, 255)
        color = (255, 200, 0) if "cross" in name or "inner" in name else color
        
        pygame.draw.rect(surf, color, (0, 0, 8 * SCALE, 8 * SCALE), 3)
        if "corner" in name or "cross" in name:
            pygame.draw.rect(surf, (255, 255, 255), (4, 4, 8 * SCALE - 8, 8 * SCALE - 8))
            
        tiles_images[name] = surf

# 3.2 Création des données du labyrinthe


donnees_brutes = """91113
80002
80002
80002
C4446"""

model = MazeModel(donnees_brutes)
view = MazeView(tiles_images, scale=SCALE)

# 3.3 Boucle de jeu
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((20, 20, 30))

    # Dessin avec un décalage pour centrer
    view.draw(screen, model, offset_x=150, offset_y=150)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()