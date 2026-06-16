import math
from typing import Any, Optional
import pygame

from .settings import (
    SMALL_BLOCK, LARGE_BLOCK,
    MACRO_ROW_HEIGHT, LARGE_BLOCK_Y_OFFSET,
    COLORS, MAZE_TILE, GOMMES_TILES,
    PALETTE_RGB, WALL_BLUE,
)

_PALETTE_TO_NAME = {v: k for k, v in COLORS.items()}
_WALL_BLUE = WALL_BLUE


def _palette_rgb(palette_index: int, macro_row: int) -> tuple[int, int, int]:
    name = _PALETTE_TO_NAME.get((palette_index, macro_row))
    return PALETTE_RGB.get(name, (128, 128, 128)) if name else (128, 128, 128)


_MAZE_COORDS_TO_NAME = {(v[0], v[1]): k for k, v in MAZE_TILE.items()}
_DOT_SMALL = tuple(GOMMES_TILES["small"])
_DOT_BIG = tuple(GOMMES_TILES["big"])

FALLBACK_CORNER_MAP = {
    0: None,
    1: "corner_outer_top_left",
    2: "corner_outer_top_right",
    3: "wall_horizontal_top",
    4: "corner_outer_bottom_left",
    5: "border_wall_vertical_left",
    6: "wall_fill",
    7: "border_corner_outer_bottom_right",
    8: "corner_outer_bottom_right",
    9: "wall_fill",
    10: "wall_vertical_right",
    11: "border_corner_outer_bottom_left",
    12: "wall_horizontal_bottom",
    13: "border_corner_outer_top_right",
    14: "corner_outer_top_left",
    15: "wall_fill",
}

FALLBACK_BORDER_MAPS = {
    "TL": {14: "border_corner_inner_top_left", 15: "wall_fill"},
    "TR": {13: "border_corner_inner_top_right", 15: "wall_fill"},
    "BL": {11: "border_corner_inner_bottom_left", 15: "wall_fill"},
    "BR": {7: "border_corner_inner_bottom_right", 15: "wall_fill"},
    "T": {
        12: "border_wall_horizontal_bottom",
        13: "border_corner_outer_top_right",
        14: "corner_outer_top_left",
        15: "wall_fill",
    },
    "B": {
        3: "border_wall_horizontal_top",
        7: "border_corner_outer_bottom_right",
        11: "corner_outer_bottom_left",
        15: "wall_fill",
    },
    "L": {
        10: "border_wall_vertical_right",
        11: "corner_outer_bottom_left",
        14: "border_corner_outer_top_left",
        15: "wall_fill",
    },
    "R": {
        5: "border_wall_vertical_left",
        7: "corner_outer_bottom_right",
        13: "corner_outer_top_right",
        15: "wall_fill",
    },
}


def _thick_arc(surf: pygame.Surface,
               color: tuple[int, int, int],
               cx: float,
               cy: float,
               r_out: float,
               thickness: float,
               start_deg: int,
               end_deg: int) -> None:
    r_in = max(0, r_out - thickness)
    outer, inner = [], []
    step = max(1, (end_deg - start_deg) // 20)
    for deg in range(start_deg, end_deg + 1, step):
        rad = math.radians(deg)
        cos_r, sin_r = math.cos(rad), math.sin(rad)
        outer.append((cx + r_out * cos_r, cy + r_out * sin_r))
        inner.append((cx + r_in * cos_r,  cy + r_in * sin_r))
    poly = outer + inner[::-1]
    if len(poly) >= 3:
        pygame.draw.polygon(surf, color, poly)


def _draw_pacman(col: int, row: int, scale: float) -> pygame.Surface:
    side = LARGE_BLOCK["cell_w"] * scale
    surf = pygame.Surface((side, side), pygame.SRCALPHA)
    cx, cy, r = side // 2, side // 2, side // 2 - 1

    gap = {3: 38, 4: 18}.get(row, 0)

    pygame.draw.circle(surf, (255, 220, 0), (cx, cy), r)

    if gap > 0:
        pts = [(cx, cy)]
        for deg in range(-gap, gap + 1, 3):
            rad = math.radians(deg)
            pts.append((cx + r * math.cos(rad), cy + r * math.sin(rad)))
        if len(pts) >= 3:
            pygame.draw.polygon(surf, (0, 0, 0, 0), pts)

    return surf


def _draw_ghost(color: tuple[int, int, int], scale: float) -> pygame.Surface:
    side = LARGE_BLOCK["cell_w"] * scale
    surf = pygame.Surface((side, side), pygame.SRCALPHA)

    pygame.draw.ellipse(surf, color, (0, 0, side, side * 2 // 3 + 2))
    pygame.draw.rect(surf, color, (0, side // 3, side, side * 2 // 3))
    bw = side // 3
    for i in range(3):
        pygame.draw.circle(surf, (0, 0, 0, 0), (i * bw + bw // 2, side), bw // 2 + 1)

    er = max(2, side // 7)
    for ex in (side // 3, side * 2 // 3):
        ey = side * 5 // 14
        pygame.draw.circle(surf, (255, 255, 255), (ex, ey), er)
        pygame.draw.circle(surf, (0, 0, 180), (ex + er // 3, ey), max(1, er // 2))

    return surf


def _draw_frightened_ghost(scale: float, blinking: bool = False) -> pygame.Surface:
    color = (255, 255, 255) if blinking else (33, 33, 200)
    side = LARGE_BLOCK["cell_w"] * scale
    surf = _draw_ghost(color, scale)
    my = side * 6 // 11
    pts = [(side // 5 + i * (side // 8),
            my + (side // 14 if i % 2 == 0 else -side // 14))
           for i in range(5)]
    if len(pts) > 1:
        pygame.draw.lines(surf, (255, 255, 255), False, pts, max(1, round(scale)))
    return surf


def _draw_eyes_only(scale: float) -> pygame.Surface:
    side = LARGE_BLOCK["cell_w"] * scale
    surf = pygame.Surface((side, side), pygame.SRCALPHA)
    er = max(2, side // 5)
    for ex in (side // 3, side * 2 // 3):
        ey = side // 2
        pygame.draw.circle(surf, (255, 255, 255), (ex, ey), er)
        pygame.draw.circle(surf, (0, 0, 180), (ex + er // 3, ey), max(1, er // 2))
    return surf


def _draw_large_fallback(macro_row: int, palette_index: int,
                         col: int, row: int, scale: float) -> pygame.Surface:
    if macro_row == 1 and palette_index == 2:
        return _draw_pacman(col, row, scale)
    if macro_row == 1 and palette_index == 1:
        return _draw_eyes_only(scale)
    if macro_row == 1 and palette_index == 3:
        return _draw_frightened_ghost(scale, blinking=False)
    if macro_row == 1 and palette_index == 0:
        return _draw_frightened_ghost(scale, blinking=True)
    if macro_row == 0 and row == 5:
        return _draw_frightened_ghost(scale, blinking=False)
    if macro_row == 0 and palette_index <= 4:
        return _draw_ghost(_palette_rgb(palette_index, macro_row), scale)
    side = LARGE_BLOCK["cell_w"] * scale
    surf = pygame.Surface((side, side), pygame.SRCALPHA)
    surf.fill(_palette_rgb(palette_index, macro_row))
    return surf


def _draw_maze_tile(col: int, row: int, scale: float) -> pygame.Surface:
    side = SMALL_BLOCK["cell_w"] * scale
    surf = pygame.Surface((side, side), pygame.SRCALPHA)
    name = _MAZE_COORDS_TO_NAME.get((col, row), "")
    color = _WALL_BLUE
    t = max(2, side // 7)
    half = side // 2

    if not name or "fill" in name:
        surf.fill(color)
        return surf

    if "horizontal" in name:
        pygame.draw.rect(surf, color, (0, half - t // 2, side, t))
        return surf
    if "vertical" in name:
        pygame.draw.rect(surf, color, (half - t // 2, 0, t, side))
        return surf

    if "corner" in name:
        if "outer" in name:
            r = half + t // 2
            outer_arcs = {
                "top_left": (side, side, 180, 270),
                "top_right": (0, side, 270, 360),
                "bottom_left": (side, 0, 90, 180),
                "bottom_right": (0, 0, 0, 90),
            }
            for key, (cx, cy, s, e) in outer_arcs.items():
                if key in name:
                    _thick_arc(surf, color, cx, cy, r, t, s, e)
                    return surf

        if "inner" in name:
            segments = {
                "top_left": (
                    (half - t // 2, half - t // 2, side - half + t // 2, t),
                    (half - t // 2, half - t // 2, t, side - half + t // 2),
                ),
                "top_right": (
                    (0, half - t // 2, half + t // 2, t),
                    (half - t // 2, half - t // 2, t, side - half + t // 2),
                ),
                "bottom_left": (
                    (half - t // 2, half - t // 2, side - half + t // 2, t),
                    (half - t // 2, 0, t, half + t // 2),
                ),
                "bottom_right": (
                    (0, half - t // 2, half + t // 2, t),
                    (half - t // 2, 0, t, half + t // 2),
                ),
            }
            for key, (r1, r2) in segments.items():
                if key in name:
                    pygame.draw.rect(surf, color, r1)
                    pygame.draw.rect(surf, color, r2)
                    return surf

        surf.fill(color)

    return surf


def _draw_small_fallback(macro_row: int, palette_index: int,
                         col: int, row: int, scale: float) -> pygame.Surface:
    if (col, row) == _DOT_SMALL:
        side = SMALL_BLOCK["cell_w"] * scale
        surf = pygame.Surface((side, side), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 255, 255), (side // 2, side // 2), max(1, side // 4))
        return surf

    if (col, row) == _DOT_BIG:
        side = SMALL_BLOCK["cell_w"] * scale
        surf = pygame.Surface((side, side), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 255, 255), (side // 2, side // 2), max(2, side // 2 - 1))
        return surf

    if macro_row == 1 and palette_index == 3:
        return _draw_maze_tile(col, row, scale)

    side = SMALL_BLOCK["cell_w"] * scale
    surf = pygame.Surface((side, side), pygame.SRCALPHA)
    surf.fill(_palette_rgb(palette_index, macro_row))
    return surf


class SpriteSheet:

    def __init__(self, filename: str) -> None:
        self._fallback = False
        self.sheet: Optional[pygame.Surface] = None
        try:
            self.sheet = pygame.image.load(filename).convert()
        except (pygame.error, FileNotFoundError, OSError):
            print(f"Avertissement : asset introuvable « {filename} » — rendu de secours activé.")
            self._fallback = True
        self._cache: dict[Any, pygame.Surface] = {}

    def _extract(self, x: float, y: float, width: int, height: int,
                 scale: float) -> pygame.Surface:
        assert self.sheet is not None
        image = pygame.Surface((width, height)).convert()
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        image.set_colorkey((0, 0, 0))
        if scale != 1:
            image = pygame.transform.scale(image, (width * scale, height * scale))
        return image

    @staticmethod
    def _cell_position(start_x: float, start_y: float,
                       col: int, row: int, cfg: dict[str, Any]) -> tuple[float, float]:
        x = start_x + cfg["cell_margin"] + col * (cfg["cell_w"] + cfg["cell_margin"])
        y = start_y + cfg["cell_margin"] + row * (cfg["cell_h"] + cfg["cell_margin"])
        return x, y

    def get_small_sprite(self, macro_row: int, palette_index: int,
                         col: int, row: int, scale: float = 1.0) -> pygame.Surface:
        key = ("small", macro_row, palette_index, col, row, scale)
        if key not in self._cache:
            if self._fallback:
                self._cache[key] = _draw_small_fallback(macro_row, palette_index, col, row, scale)
            else:
                start_y = macro_row * MACRO_ROW_HEIGHT
                start_x = palette_index * (SMALL_BLOCK["block_w"] + SMALL_BLOCK["block_margin"])
                x, y = self._cell_position(start_x, start_y, col, row, SMALL_BLOCK)
                self._cache[key] = self._extract(
                    x, y, SMALL_BLOCK["cell_w"], SMALL_BLOCK["cell_h"], scale
                )
        return self._cache[key]

    def get_large_sprite(self, macro_row: int, palette_index: int,
                         col: int, row: int, scale: float = 1.0) -> pygame.Surface:
        key = ("large", macro_row, palette_index, col, row, scale)
        if key not in self._cache:
            if self._fallback:
                self._cache[key] = _draw_large_fallback(macro_row, palette_index, col, row, scale)
            else:
                start_y = LARGE_BLOCK_Y_OFFSET + macro_row * MACRO_ROW_HEIGHT
                section_w = (LARGE_BLOCK["block_w"] + LARGE_BLOCK["palette_w"]
                             + LARGE_BLOCK["block_margin"])
                start_x = palette_index * section_w
                x, y = self._cell_position(start_x, start_y, col, row, LARGE_BLOCK)
                self._cache[key] = self._extract(
                    x, y, LARGE_BLOCK["cell_w"], LARGE_BLOCK["cell_h"], scale
                )
        return self._cache[key]
