"""Données graphiques, chargées depuis le manifeste `assets/manifest.json`.

Ce module ne contient plus aucune table en dur : il lit le manifeste (source
unique de vérité) et en dérive les constantes typées attendues par les vues —
géométrie de la planche, palettes, couleurs RGB des éléments, tuiles de
labyrinthe, police ASCII, fruits. Les animations et les skins sont, eux,
consommés directement par `views.assets` via `MANIFEST`.
"""

import json
import os
from typing import Any, Optional

_MANIFEST_PATH = os.path.join("assets", "manifest.json")

with open(_MANIFEST_PATH, encoding="utf-8") as _f:
    MANIFEST: dict[str, Any] = json.load(_f)


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
