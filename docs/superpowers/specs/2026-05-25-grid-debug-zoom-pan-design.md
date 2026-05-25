# Design : Zoom & Pan dans le débogueur de grille Pac-Man

**Date :** 2026-05-25  
**Fichier cible :** `debug/grid.py`

## Objectif

Permettre à l'utilisateur de zoomer et de se déplacer dans le viewer pygame de sprite sheet pour débugger précisément la grille de sprites.

## Contrôles

| Action | Contrôle |
|--------|----------|
| Zoom avant/arrière | Molette souris (centré sur la position du curseur) |
| Déplacement (pan) | Clic gauche maintenu + glisser |

## État de la caméra

Deux variables dans la boucle principale :

- `zoom : float` — facteur d'agrandissement, départ `1.0`, min `0.5`, max `16.0`
- `offset : [float, float]` — décalage en pixels à l'écran, départ `[0.0, 0.0]`
- `panning : bool` — indique si le clic gauche est maintenu
- `pan_start : [int, int]` — position souris au début du drag

## Zoom centré sur la souris

Lors d'un événement `MOUSEWHEEL` :

```
mouse_x, mouse_y = position souris à l'écran
world_x = (mouse_x - offset[0]) / zoom
world_y = (mouse_y - offset[1]) / zoom
zoom *= 1.1  (ou 0.9 pour dézoomer)
zoom = clamp(zoom, 0.5, 16.0)
offset[0] = mouse_x - world_x * zoom
offset[1] = mouse_y - world_y * zoom
```

Cela garantit que le point du monde sous la souris reste au même endroit à l'écran.

## Pan par clic + drag

- `MOUSEBUTTONDOWN` (bouton 1) → `panning = True`, mémoriser `pan_start`
- `MOUSEMOTION` si `panning` → `offset += delta souris`
- `MOUSEBUTTONUP` (bouton 1) → `panning = False`

## Dessin transformé

### Sprite sheet

Calculer la taille affichée : `(int(width * zoom), int(height * zoom))`.  
Utiliser `pygame.transform.scale(sprite_sheet, scaled_size)` puis blitter à `(int(offset[0]), int(offset[1]))`.

### Grilles

Les fonctions `draw_small_grid` et `draw_large_grid` reçoivent `zoom` et `offset` comme paramètres supplémentaires.  
Toute coordonnée monde `(wx, wy)` est transformée en coordonnée écran : `sx = wx * zoom + offset[0]`, `sy = wy * zoom + offset[1]`.  
La taille de chaque cellule est également multipliée par `zoom` : `cell_w_s = int(cell_w * zoom)`.  
Les rectangles de moins de 1px de large/haut sont ignorés (pas visibles).

## Fenêtre

La fenêtre reste à taille fixe (dimensions originales de l'image). Le contenu peut sortir des bords lors du pan/zoom — comportement attendu pour un outil de navigation.

## Fichiers modifiés

- `debug/grid.py` — seul fichier à modifier

## Ce qui ne change pas

- La configuration `SMALL_BLOCK` et `LARGE_BLOCK`
- La logique de calcul des positions de la grille (inchangée, seulement la transformation finale)
- Le chargement de l'image
