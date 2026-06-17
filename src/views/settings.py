"""Données graphiques, chargées depuis le manifeste `assets/manifest.json`.

Ce module lit le manifeste (source unique de vérité) et en dérive les
constantes typées attendues par les vues. Si le fichier est absent, un
manifeste de secours intégré en dur est utilisé à la place ; le rendu pygame
de `SpriteSheet` prend alors le relais si la planche PNG manque aussi.
"""

import json
import os
from typing import Any, Optional

_MANIFEST_PATH = os.path.join("assets", "manifest.json")

_FALLBACK_MANIFEST: dict[str, Any] = {
    "sheet": {
        "path": "assets/default.png",
        "macro_row_height": 186,
        "large_block_y_offset": 82,
        "small_block": {
            "cell_w": 8, "cell_h": 8, "cell_margin": 1,
            "block_w": 199, "block_margin": 1,
        },
        "large_block": {
            "cell_w": 16, "cell_h": 16, "cell_margin": 1,
            "block_w": 171, "palette_w": 27, "block_margin": 2,
        },
    },
    "palettes": {
        "red": [0, 0], "pink": [1, 0], "cyan": [2, 0], "orange": [3, 0], "beige-2": [4, 0],
        "red-2": [0, 1], "black": [1, 1], "yellow": [2, 1], "blue": [3, 1], "white": [4, 1],
        "red-3": [0, 2], "beige": [1, 2], "white-2": [2, 2], "white-3": [3, 2], "orange-2": [4, 2],
        "white-4": [0, 3], "yellow-2": [1, 3], "white-5": [2, 3],
        "beige-3": [3, 3], "fatih": [4, 3],
    },
    "palette_rgb": {
        "red": [220, 50, 50], "pink": [255, 184, 255], "cyan": [0, 220, 220],
        "orange": [255, 184, 81], "beige-2": [222, 184, 135], "red-2": [255, 100, 100],
        "black": [20, 20, 20], "yellow": [255, 220, 0], "blue": [50, 50, 220],
        "white": [255, 255, 255], "red-3": [200, 80, 80], "beige": [210, 180, 140],
        "white-2": [230, 230, 230], "white-3": [210, 210, 210], "orange-2": [255, 165, 0],
        "white-4": [200, 200, 200], "yellow-2": [255, 200, 0], "white-5": [190, 190, 190],
        "beige-3": [195, 170, 120], "fatih": [150, 100, 200],
    },
    "ghost_colors": {
        "red": [255, 0, 0], "pink": [255, 184, 255],
        "cyan": [0, 255, 255], "orange": [255, 184, 81],
    },
    "colors": {"wall": [33, 33, 200]},
    "tiles": {
        "gommes": {"small": [15, 1], "big": [15, 3]},
        "score": {"200": [2, 5], "400": [3, 5], "800": [4, 5], "1600": [5, 5]},
        "ascii": {
            "0": [0, 2], "1": [1, 2], "2": [2, 2], "3": [3, 2], "4": [4, 2],
            "5": [5, 2], "6": [6, 2], "7": [7, 2], "8": [8, 2], "9": [9, 2],
            "A": [0, 3], "B": [1, 3], "C": [2, 3], "D": [3, 3], "E": [4, 3],
            "F": [5, 3], "G": [6, 3], "H": [7, 3], "I": [8, 3], "J": [9, 3],
            "K": [10, 3], "L": [11, 3], "M": [12, 3], "N": [0, 4], "O": [1, 4],
            "P": [2, 4], "Q": [3, 4], "R": [4, 4], "S": [5, 4], "T": [6, 4],
            "U": [7, 4], "V": [8, 4], "W": [9, 4], "X": [10, 4], "Y": [11, 4],
            "Z": [12, 4], "!": [12, 2], "\"": [10, 2], "/": [10, 1],
            "-": [11, 1], ".": [12, 1], "+": [9, 1],
        },
    },
    "maze": {
        "tiles": {
            "corner_outer_top_left": [16, 0], "corner_outer_top_right": [18, 0],
            "wall_horizontal_top": [17, 0], "corner_outer_bottom_left": [16, 2],
            "wall_vertical_left": [16, 1], "wall_fill": [17, 1],
            "corner_inner_top_left": [17, 4], "corner_outer_bottom_right": [18, 2],
            "wall_vertical_right": [18, 1], "corner_inner_top_right": [18, 4],
            "wall_horizontal_bottom": [17, 2], "corner_inner_bottom_left": [17, 5],
            "corner_inner_bottom_right": [18, 5],
            "border_corner_outer_top_left": [16, 3], "border_corner_outer_top_right": [19, 3],
            "border_wall_horizontal_top": [20, 0], "border_corner_outer_bottom_left": [16, 6],
            "border_wall_vertical_left": [19, 1], "border_corner_inner_top_left": [19, 6],
            "border_corner_outer_bottom_right": [17, 6], "border_wall_vertical_right": [21, 1],
            "border_corner_inner_top_right": [18, 6], "border_wall_horizontal_bottom": [20, 2],
            "border_corner_inner_bottom_left": [17, 3],
            "border_corner_inner_bottom_right": [18, 3],
            "border_corner_inner_top_right_bottom": [16, 4],
            "border_corner_inner_bottom_right_top": [16, 5],
            "border_corner_inner_bottom_left_top": [19, 5],
            "border_corner_inner_top_left_bottom": [19, 4],
        },
        "corner_map": {
            "0": None, "1": "corner_outer_top_left", "2": "corner_outer_top_right",
            "3": "wall_horizontal_top", "4": "corner_outer_bottom_left",
            "5": "wall_vertical_left", "6": "wall_fill", "7": "corner_inner_top_left",
            "8": "corner_outer_bottom_right", "9": "wall_fill", "10": "wall_vertical_right",
            "11": "corner_inner_top_right", "12": "wall_horizontal_bottom",
            "13": "corner_inner_bottom_left", "14": "corner_inner_bottom_right",
            "15": "wall_fill",
        },
        "border_maps": {
            "TL": {"14": "border_corner_outer_top_left", "15": "wall_fill"},
            "TR": {"13": "border_corner_outer_top_right", "15": "wall_fill"},
            "BL": {"11": "border_corner_outer_bottom_left", "15": "wall_fill"},
            "BR": {"7": "border_corner_inner_top_left", "15": "wall_fill"},
            "T": {"12": "border_wall_horizontal_bottom", "13": "border_corner_inner_bottom_left",
                  "14": "border_corner_inner_bottom_right", "15": "wall_fill"},
            "B": {"3": "border_wall_horizontal_top", "7": "border_corner_outer_bottom_right",
                  "11": "border_corner_inner_top_right", "15": "wall_fill"},
            "L": {"10": "border_wall_vertical_right", "11": "border_corner_inner_top_right_bottom",
                  "14": "border_corner_inner_bottom_right_top", "15": "wall_fill"},
            "R": {"5": "border_wall_vertical_left", "7": "border_corner_inner_top_left_bottom",
                  "13": "border_corner_inner_bottom_left_top", "15": "wall_fill"},
        },
    },
    "food": {
        "cherry":     {"frame": [[0, 2]], "default_color": "white-2",  "loop": "none"},
        "strawberry": {"frame": [[1, 2]], "default_color": "white-3",  "loop": "none"},
        "orange":     {"frame": [[2, 2]], "default_color": "orange-2", "loop": "none"},
        "apple":      {"frame": [[3, 2]], "default_color": "white-3",  "loop": "none"},
        "grape":      {"frame": [[4, 2]], "default_color": "white-4",  "loop": "none"},
        "galaxian":   {"frame": [[5, 2]], "default_color": "yellow-2", "loop": "none"},
    },
    "animations": {
        "pacman": {
            "palette": [2, 1],
            "size": "large",
            "variants": {
                "right": {"frames": [[6, 3], [6, 4], [6, 5]], "loop": "pingpong"},
                "left":  {"from": "right", "x_flip": True},
                "up":    {"frames": [[7, 3], [7, 4], [6, 5]], "loop": "pingpong", "y_flip": True},
                "down":  {"from": "up", "y_flip": False},
                "death_up": {
                    "frames": [[0, 3], [1, 3], [2, 3], [3, 3], [4, 3], [5, 3],
                               [0, 4], [1, 4], [2, 4], [3, 4], [4, 4], [5, 4]],
                    "loop": "once", "y_flip": True,
                },
                "death_down":  {"from": "death_up", "y_flip": False},
                "death_right": {"from": "death_down", "rotation": -90},
                "death_left":  {"from": "death_down", "rotation": 90},
            },
        },
        "gum": {
            "palette": [0, 0],
            "size": "small",
            "variants": {
                "small": {"frames": [[15, 1]], "loop": "none"},
                "big":   {"frames": [[15, 3]], "loop": "none"},
            },
        },
        "ghost": {
            "size": "large",
            "variants": {
                "right":      {"frames": [[0, 0], [1, 0]], "loop": "pingpong"},
                "left":       {"frames": [[4, 0], [5, 0]], "loop": "pingpong"},
                "up":         {"frames": [[6, 0], [7, 0]], "loop": "pingpong"},
                "down":       {"frames": [[2, 0], [3, 0]], "loop": "pingpong"},
                "frightened": {"frames": [[0, 5], [1, 5]], "loop": "pingpong"},
            },
            "states": {
                "normal":     {"use_direction": True, "color_from_entity": True},
                "eaten":      {"use_direction": True, "color": "black"},
                "frightened": {"variant": "frightened", "color_from_entity": True,
                               "blink_color": "red-2", "blink_ms": 250},
            },
        },
    },
    "skins": {"default": {}, "secret": {"dir": "assets/sprites", "overrides": {}}},
}

try:
    with open(_MANIFEST_PATH, encoding="utf-8") as _f:
        MANIFEST: dict[str, Any] = json.load(_f)
except (FileNotFoundError, OSError, json.JSONDecodeError):
    print(
        f"Avertissement : manifeste introuvable « {_MANIFEST_PATH} »"
        " — données de secours utilisées."
    )
    MANIFEST = _FALLBACK_MANIFEST


def _coords(table: dict[str, Any]) -> dict[str, tuple[int, int]]:
    """name -> (col, row) : convertit les listes JSON en couples."""
    return {k: (v[0], v[1]) for k, v in table.items()}


def _rgb(table: dict[str, Any]) -> dict[str, tuple[int, int, int]]:
    """name -> (r, g, b)."""
    return {k: (v[0], v[1], v[2]) for k, v in table.items()}


# --- Géométrie de la planche assets/default.png ------------------------------
_SHEET = MANIFEST["sheet"]
SHEET_PATH: str = _SHEET["path"]
MACRO_ROW_HEIGHT: int = _SHEET["macro_row_height"]
LARGE_BLOCK_Y_OFFSET: int = _SHEET["large_block_y_offset"]
SMALL_BLOCK: dict[str, int] = _SHEET["small_block"]
LARGE_BLOCK: dict[str, int] = _SHEET["large_block"]

# --- Palettes (position dans la planche) + couleurs RGB des éléments ---------
COLORS: dict[str, tuple[int, int]] = _coords(MANIFEST["palettes"])
PALETTE_RGB: dict[str, tuple[int, int, int]] = _rgb(MANIFEST["palette_rgb"])
GHOST_COLORS: dict[str, tuple[int, int, int]] = _rgb(MANIFEST["ghost_colors"])
_wall = MANIFEST["colors"]["wall"]
WALL_BLUE: tuple[int, int, int] = (_wall[0], _wall[1], _wall[2])

# --- Tuiles statiques (gommes, scores, police bitmap) ------------------------
_TILES = MANIFEST["tiles"]
GOMMES_TILES: dict[str, tuple[int, int]] = _coords(_TILES["gommes"])
SCORE_SPRITE: dict[str, tuple[int, int]] = _coords(_TILES["score"])
ASCII_TILE: dict[str, tuple[int, int]] = _coords(_TILES["ascii"])

# --- Labyrinthe (tuiles + tables de masques de murs) -------------------------
_MAZE = MANIFEST["maze"]
MAZE_TILE: dict[str, list[int]] = _MAZE["tiles"]
CORNER_MAP: dict[int, Optional[str]] = {
    int(code): name for code, name in _MAZE["corner_map"].items()}
BORDER_MAPS: dict[str, dict[int, str]] = {
    edge: {int(code): name for code, name in mapping.items()}
    for edge, mapping in _MAZE["border_maps"].items()
}

# --- Fruits bonus ------------------------------------------------------------
FOOD: dict[str, Any] = MANIFEST["food"]
