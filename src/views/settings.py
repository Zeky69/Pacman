"""Données graphiques, chargées depuis le manifeste `assets/manifest.json`.

Ce module lit le manifeste (source unique de vérité) et en dérive les
constantes typées attendues par les vues. Si le fichier est absent, un
manifeste de secours intégré en dur est utilisé à la place ; le rendu pygame
de `SpriteSheet` prend alors le relais si la planche PNG manque aussi.
"""

import json
from typing import Any, Optional

from ..paths import resource_path

_MANIFEST_PATH = resource_path("assets/manifest.json")

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

MANIFEST_WARNING: Optional[str] = None

_REQUIRED_KEYS = (
    "sheet", "palettes", "palette_rgb", "ghost_colors",
    "colors", "tiles", "maze", "food", "animations",
)

try:
    with open(_MANIFEST_PATH, encoding="utf-8") as _f:
        _candidate: dict[str, Any] = json.load(_f)
    _missing = [k for k in _REQUIRED_KEYS if k not in _candidate]
    if _missing:
        raise KeyError(f"clés manquantes : {', '.join(_missing)}")
    MANIFEST: dict[str, Any] = _candidate
except FileNotFoundError:
    MANIFEST_WARNING = (
        f"Manifeste introuvable « {_MANIFEST_PATH} » — fallback chargé."
    )
    MANIFEST = _FALLBACK_MANIFEST
except json.JSONDecodeError as _e:
    MANIFEST_WARNING = f"Manifeste invalide (JSON malformé : {_e}) — fallback chargé."
    MANIFEST = _FALLBACK_MANIFEST
except (OSError, KeyError, TypeError, ValueError) as _e:
    MANIFEST_WARNING = f"Manifeste invalide ({_e}) — fallback chargé."
    MANIFEST = _FALLBACK_MANIFEST

if MANIFEST_WARNING:
    print(f"Avertissement : {MANIFEST_WARNING}")


def _coords(table: dict[str, Any]) -> dict[str, tuple[int, int]]:
    """name -> (col, row) : convertit les listes JSON en couples."""
    return {k: (v[0], v[1]) for k, v in table.items()}


# Garde-fous numériques : au-delà de ces bornes, pygame plante (allocation de
# surface impossible, couleur invalide…). On préfère retomber sur le fallback.
_MAX_DIM = 4096        # côté de cellule / largeur de bloc raisonnable (pixels)
_MAX_OFFSET = 1_000_000  # décalage vertical dans la planche
_SMALL_BLOCK_KEYS = {"cell_w", "cell_h", "cell_margin", "block_w", "block_margin"}
_LARGE_BLOCK_KEYS = {"cell_w", "cell_h", "cell_margin",
                     "block_w", "palette_w", "block_margin"}
_REQUIRED_BORDER_EDGES = {"TL", "TR", "BL", "BR", "T", "B", "L", "R"}


def _checked_int(value: Any, name: str, lo: int, hi: int) -> int:
    """Convertit en int et vérifie l'appartenance à [lo, hi] (anti valeurs absurdes)."""
    n = int(value)
    if not lo <= n <= hi:
        raise ValueError(f"{name} = {n} hors limites [{lo}, {hi}]")
    return n


def _checked_rgb(table: Any, name: str) -> dict[str, tuple[int, int, int]]:
    """name -> (r, g, b), chaque composante bornée à [0, 255] (anti crash pygame)."""
    if not isinstance(table, dict):
        raise TypeError(f"'{name}' doit être un objet")
    out: dict[str, tuple[int, int, int]] = {}
    for k, v in table.items():
        if not isinstance(v, (list, tuple)) or len(v) != 3:
            raise ValueError(f"{name}.{k} doit être [r, g, b]")
        out[k] = (
            _checked_int(v[0], f"{name}.{k}", 0, 255),
            _checked_int(v[1], f"{name}.{k}", 0, 255),
            _checked_int(v[2], f"{name}.{k}", 0, 255),
        )
    return out


def _validate_block(block: Any, name: str, required: set[str]) -> dict[str, int]:
    """Valide un bloc de géométrie (small/large) : clés requises + ints bornés."""
    if not isinstance(block, dict):
        raise TypeError(f"sheet.{name} doit être un objet")
    missing = required - block.keys()
    if missing:
        raise KeyError(
            f"sheet.{name} : clé(s) manquante(s) : {', '.join(sorted(missing))}")
    out: dict[str, int] = {
        k: _checked_int(v, f"sheet.{name}.{k}", 0, _MAX_DIM)
        for k, v in block.items()
    }
    for dim in ("cell_w", "cell_h"):
        if out[dim] < 1:
            raise ValueError(f"sheet.{name}.{dim} doit être >= 1")
    return out


def _validate_maze(maze: Any) -> None:
    """Valide la section 'maze' : tuiles, corner_map et tous les bords requis.

    Un bord manquant dans 'border_maps' provoquerait sinon un KeyError au rendu
    (cf. MazeView._active_map).
    """
    if not isinstance(maze, dict):
        raise TypeError("'maze' doit être un objet")
    tiles = maze.get("tiles")
    if not isinstance(tiles, dict) or not tiles:
        raise TypeError("maze.tiles doit être un objet non vide")
    for tname, coords in tiles.items():
        if not isinstance(coords, (list, tuple)) or len(coords) != 2:
            raise ValueError(f"maze.tiles.{tname} doit être [col, row]")
        int(coords[0]); int(coords[1])  # noqa: E702

    corner_map = maze.get("corner_map")
    if not isinstance(corner_map, dict):
        raise TypeError("maze.corner_map doit être un objet")
    for code in corner_map:
        int(code)  # les clés sont des codes numériques

    border_maps = maze.get("border_maps")
    if not isinstance(border_maps, dict):
        raise TypeError("maze.border_maps doit être un objet")
    missing_edges = _REQUIRED_BORDER_EDGES - border_maps.keys()
    if missing_edges:
        raise KeyError(
            f"maze.border_maps : bord(s) manquant(s) : "
            f"{', '.join(sorted(missing_edges))}")
    for edge, mapping in border_maps.items():
        if not isinstance(mapping, dict):
            raise TypeError(f"maze.border_maps.{edge} doit être un objet")
        for code in mapping:
            int(code)


# Variantes requises par le code (game_view + _animator_for).
_REQUIRED_VARIANTS: dict[str, set[str]] = {
    "pacman": {"right", "left", "up", "down",
               "death_up", "death_down", "death_right", "death_left"},
    "gum":    {"small", "big"},
    "ghost":  {"right", "left", "up", "down", "frightened"},
}
_REQUIRED_GHOST_STATES = {"normal", "eaten", "frightened"}
_REQUIRED_GUM_TILES = {"small", "big"}
_REQUIRED_SCORE_TILES = {"200", "400", "800", "1600"}


def _validate_animations(animations: Any, known_colors: set[str]) -> None:
    """Valide la section 'animations' en entier."""
    if not isinstance(animations, dict):
        raise TypeError("'animations' doit être un objet")

    for anim_name, req_variants in _REQUIRED_VARIANTS.items():
        if anim_name not in animations:
            raise KeyError(f"animation '{anim_name}' manquante")
        adef = animations[anim_name]
        if not isinstance(adef, dict):
            raise TypeError(f"animations.{anim_name} doit être un objet")

        # palette optionnelle mais si présente doit être [int, int]
        if "palette" in adef:
            p = adef["palette"]
            if not (isinstance(p, (list, tuple)) and len(p) == 2):
                raise ValueError(
                    f"animations.{anim_name}.palette doit être [col, row]")
            int(p[0]); int(p[1])  # noqa: raises ValueError si non-numérique

        variants = adef.get("variants")
        if not isinstance(variants, dict):
            raise TypeError(f"animations.{anim_name}.variants doit être un objet")

        missing = req_variants - variants.keys()
        if missing:
            raise KeyError(
                f"animations.{anim_name}.variants : "
                f"variante(s) manquante(s) : {', '.join(sorted(missing))}")

        for vname, vdef in variants.items():
            if not isinstance(vdef, dict):
                raise TypeError(
                    f"animations.{anim_name}.variants.{vname} doit être un objet")
            if "from" in vdef:
                ref = vdef["from"]
                if ref not in variants:
                    raise KeyError(
                        f"animations.{anim_name}.variants.{vname}.from : "
                        f"référence '{ref}' inexistante")
            elif "frames" not in vdef:
                raise KeyError(
                    f"animations.{anim_name}.variants.{vname} : "
                    f"clé 'frames' ou 'from' manquante")
            else:
                frames = vdef["frames"]
                if not isinstance(frames, list) or not frames:
                    raise ValueError(
                        f"animations.{anim_name}.variants.{vname}.frames : "
                        f"doit être une liste non vide")
                for i, fr in enumerate(frames):
                    if not isinstance(fr, (list, tuple)) or len(fr) != 2:
                        raise ValueError(
                            f"animations.{anim_name}.variants.{vname}"
                            f".frames[{i}] doit être [col, row]")
                    int(fr[0])
                    int(fr[1])

    # --- Ghost states ---
    ghost_states = animations.get("ghost", {}).get("states")
    if not isinstance(ghost_states, dict):
        raise TypeError("animations.ghost.states doit être un objet")
    missing_states = _REQUIRED_GHOST_STATES - ghost_states.keys()
    if missing_states:
        raise KeyError(
            f"animations.ghost.states : états manquants : "
            f"{', '.join(sorted(missing_states))}")
    ghost_variants = animations["ghost"].get("variants", {})
    for sname, sdef in ghost_states.items():
        if not isinstance(sdef, dict):
            raise TypeError(f"animations.ghost.states.{sname} doit être un objet")
        if not sdef.get("use_direction") and "variant" not in sdef:
            raise KeyError(
                f"animations.ghost.states.{sname} : 'variant' requis "
                f"quand 'use_direction' est absent")
        if "variant" in sdef and sdef["variant"] not in ghost_variants:
            raise KeyError(
                f"animations.ghost.states.{sname}.variant : "
                f"'{sdef['variant']}' inexistant dans ghost.variants")
        if not sdef.get("color_from_entity") and "color" not in sdef:
            raise KeyError(
                f"animations.ghost.states.{sname} : 'color' requis "
                f"quand 'color_from_entity' est absent")
        if "color" in sdef and sdef["color"] not in known_colors:
            raise KeyError(
                f"animations.ghost.states.{sname}.color : "
                f"couleur '{sdef['color']}' absente de 'palettes'")
        if "blink_color" in sdef:
            if "blink_ms" not in sdef:
                raise KeyError(
                    f"animations.ghost.states.{sname} : "
                    f"'blink_ms' requis avec 'blink_color'")
            if sdef["blink_color"] not in known_colors:
                raise KeyError(
                    f"animations.ghost.states.{sname}.blink_color : "
                    f"couleur '{sdef['blink_color']}' absente de 'palettes'")


def _validate_food(food: Any, known_colors: set[str]) -> None:
    """Valide la section 'food' : frame [col,row] et default_color dans palettes."""
    if not isinstance(food, dict):
        raise TypeError("'food' doit être un objet")
    for fname, fdef in food.items():
        if not isinstance(fdef, dict):
            raise TypeError(f"food.{fname} doit être un objet")
        if "frame" not in fdef:
            raise KeyError(f"food.{fname} : clé 'frame' manquante")
        frames = fdef["frame"]
        if not isinstance(frames, list) or not frames:
            raise ValueError(f"food.{fname}.frame doit être une liste non vide")
        for i, fr in enumerate(frames):
            if not isinstance(fr, (list, tuple)) or len(fr) != 2:
                raise ValueError(f"food.{fname}.frame[{i}] doit être [col, row]")
            int(fr[0])
            int(fr[1])
        if "default_color" not in fdef:
            raise KeyError(f"food.{fname} : clé 'default_color' manquante")
        color = fdef["default_color"]
        if color not in known_colors:
            raise KeyError(
                f"food.{fname}.default_color : couleur '{color}' "
                f"absente de 'palettes'")


def _extract_constants(manifest: dict[str, Any]) -> dict[str, Any]:
    """Extrait et valide toutes les constantes typées du manifeste."""
    _sheet = manifest["sheet"]
    _tiles = manifest["tiles"]
    _maze = manifest["maze"]
    _wall = manifest["colors"]["wall"]
    if not isinstance(_wall, (list, tuple)) or len(_wall) != 3:
        raise ValueError("colors.wall doit être [r, g, b]")

    # Palettes : validation structurelle + collecte des noms connus.
    palettes = manifest["palettes"]
    if not isinstance(palettes, dict):
        raise TypeError("'palettes' doit être un objet")
    for pname, pval in palettes.items():
        if not isinstance(pval, (list, tuple)) or len(pval) != 2:
            raise ValueError(f"palettes.{pname} doit être [col, row]")
        int(pval[0])
        int(pval[1])
    known_colors: set[str] = set(palettes.keys())

    # Tiles requises.
    gommes = _tiles.get("gommes", {})
    missing_gum = _REQUIRED_GUM_TILES - gommes.keys()
    if missing_gum:
        raise KeyError(
            f"tiles.gommes : tuile(s) manquante(s) : {', '.join(sorted(missing_gum))}")
    score_tiles = _tiles.get("score", {})
    missing_score = _REQUIRED_SCORE_TILES - score_tiles.keys()
    if missing_score:
        raise KeyError(
            f"tiles.score : tuile(s) manquante(s) : {', '.join(sorted(missing_score))}")

    _validate_food(manifest["food"], known_colors)
    _validate_animations(manifest["animations"], known_colors)
    _validate_maze(_maze)

    return {
        # Chemin résolu vers la planche embarquée (compatible exécutable PyInstaller).
        "SHEET_PATH": resource_path(str(_sheet["path"])),
        "MACRO_ROW_HEIGHT": _checked_int(
            _sheet["macro_row_height"], "sheet.macro_row_height", 0, _MAX_OFFSET),
        "LARGE_BLOCK_Y_OFFSET": _checked_int(
            _sheet["large_block_y_offset"], "sheet.large_block_y_offset", 0, _MAX_OFFSET),
        "SMALL_BLOCK": _validate_block(_sheet["small_block"], "small_block", _SMALL_BLOCK_KEYS),
        "LARGE_BLOCK": _validate_block(_sheet["large_block"], "large_block", _LARGE_BLOCK_KEYS),
        "COLORS": _coords(palettes),
        "PALETTE_RGB": _checked_rgb(manifest["palette_rgb"], "palette_rgb"),
        "GHOST_COLORS": _checked_rgb(manifest["ghost_colors"], "ghost_colors"),
        "WALL_BLUE": (
            _checked_int(_wall[0], "colors.wall", 0, 255),
            _checked_int(_wall[1], "colors.wall", 0, 255),
            _checked_int(_wall[2], "colors.wall", 0, 255),
        ),
        "GOMMES_TILES": _coords(gommes),
        "SCORE_SPRITE": _coords(score_tiles),
        "ASCII_TILE": _coords(_tiles["ascii"]),
        "MAZE_TILE": dict(_maze["tiles"]),
        "CORNER_MAP": {int(c): n for c, n in _maze["corner_map"].items()},
        "BORDER_MAPS": {
            edge: {int(c): n for c, n in mapping.items()}
            for edge, mapping in _maze["border_maps"].items()
        },
        "FOOD": dict(manifest["food"]),
    }


try:
    _constants = _extract_constants(MANIFEST)
except Exception as _e:
    if MANIFEST_WARNING is None:
        MANIFEST_WARNING = (
            f"Manifeste invalide (valeurs incorrectes : {_e}) — fallback chargé."
        )
        print(f"Avertissement : {MANIFEST_WARNING}")
    MANIFEST = _FALLBACK_MANIFEST
    _constants = _extract_constants(MANIFEST)

# --- Géométrie de la planche assets/default.png ------------------------------
SHEET_PATH: str = _constants["SHEET_PATH"]
MACRO_ROW_HEIGHT: int = _constants["MACRO_ROW_HEIGHT"]
LARGE_BLOCK_Y_OFFSET: int = _constants["LARGE_BLOCK_Y_OFFSET"]
SMALL_BLOCK: dict[str, int] = _constants["SMALL_BLOCK"]
LARGE_BLOCK: dict[str, int] = _constants["LARGE_BLOCK"]

# --- Palettes (position dans la planche) + couleurs RGB des éléments ---------
COLORS: dict[str, tuple[int, int]] = _constants["COLORS"]
PALETTE_RGB: dict[str, tuple[int, int, int]] = _constants["PALETTE_RGB"]
GHOST_COLORS: dict[str, tuple[int, int, int]] = _constants["GHOST_COLORS"]
WALL_BLUE: tuple[int, int, int] = _constants["WALL_BLUE"]

# --- Tuiles statiques (gommes, scores, police bitmap) ------------------------
GOMMES_TILES: dict[str, tuple[int, int]] = _constants["GOMMES_TILES"]
SCORE_SPRITE: dict[str, tuple[int, int]] = _constants["SCORE_SPRITE"]
ASCII_TILE: dict[str, tuple[int, int]] = _constants["ASCII_TILE"]

# --- Labyrinthe (tuiles + tables de masques de murs) -------------------------
MAZE_TILE: dict[str, list[int]] = _constants["MAZE_TILE"]
CORNER_MAP: dict[int, Optional[str]] = _constants["CORNER_MAP"]
BORDER_MAPS: dict[str, dict[int, str]] = _constants["BORDER_MAPS"]

# --- Fruits bonus ------------------------------------------------------------
FOOD: dict[str, Any] = _constants["FOOD"]
