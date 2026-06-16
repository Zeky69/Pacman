PACMAN_ANIMATIONS = {
    'right': {
        'frame': [(6, 3), (6, 4), (6, 5)],
        'x_flip': False,
        'y_flip': False,
        'loop_type': 'pingpong',
        'rotation': 0,
    },
    'left': {
        'frame': [(6, 3), (6, 4), (6, 5)],
        'x_flip': True,
        'y_flip': False,
        'loop_type': 'pingpong',
        'rotation': 0,
    },
    'up': {
        'frame': [(7, 3), (7, 4), (6, 5)],
        'x_flip': False,
        'y_flip': True,
        'loop_type': 'pingpong',
        'rotation': 0,
    },
    'down': {
        'frame': [(7, 3), (7, 4), (6, 5)],
        'x_flip': False,
        'y_flip': False,
        'loop_type': 'pingpong',
        'rotation': 0,
    },
    'death_up': {
        'frame': [
            (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3),
            (0, 4), (1, 4), (2, 4), (3, 4), (4, 4), (5, 4),
        ],
        'x_flip': False,
        'y_flip': True,
        'loop_type': 'once',
        'rotation': 0,
    },
    'death_down': {
        'frame': [
            (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3),
            (0, 4), (1, 4), (2, 4), (3, 4), (4, 4), (5, 4),
        ],
        'x_flip': False,
        'y_flip': False,
        'loop_type': 'once',
        'rotation': 0,
    },
    'death_right': {
        'frame': [
            (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3),
            (0, 4), (1, 4), (2, 4), (3, 4), (4, 4), (5, 4),
        ],
        'x_flip': False,
        'y_flip': False,
        'loop_type': 'once',
        'rotation': -90,
    },
    'death_left': {
        'frame': [
            (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3),
            (0, 4), (1, 4), (2, 4), (3, 4), (4, 4), (5, 4),
        ],
        'x_flip': False,
        'y_flip': False,
        'loop_type': 'once',
        'rotation': 90,
    },
}

# Mode « secret » : textures dédiées chargées depuis des PNG individuels.
SECRET_SPRITES_DIR = "assets/sprites"

# Seule la frame « droite » existe : on dérive les autres directions par
# miroir / rotation (pygame : rotation positive = sens antihoraire).
# Chaque entrée donne les fichiers (un par frame) + la transformation à
# appliquer. Toute frame dont le fichier manque retombe sur la planche.
_PACMAN_RIGHT_FRAMES = ['pacman-right-1.png', 'pacman-right-2.png', 'pacman-right-3.png']

# La mort utilise les mêmes PNG pour toutes les directions, sans miroir ni
# rotation. L'animation par défaut compte 12 frames : on répète la dernière
# pour couvrir toutes les frames sans retomber sur la planche par défaut.
_PACMAN_DEATH_FRAMES = [
    'pacman-death-1.png', 'pacman-death-2.png', 'pacman-death-3.png',
    'pacman-death-4.png', 'pacman-death-5.png', 'pacman-death-6.png',
    'pacman-death-7.png', 'pacman-death-8.png',
    'pacman-death-8.png', 'pacman-death-8.png', 'pacman-death-8.png',
    'pacman-death-8.png',
]

PACMAN_SECRET_FRAMES = {
    'right': {'files': _PACMAN_RIGHT_FRAMES, 'x_flip': False, 'y_flip': False, 'rotation': 0},
    'left':  {'files': _PACMAN_RIGHT_FRAMES, 'x_flip': True,  'y_flip': False, 'rotation': 0},
    'up':    {'files': _PACMAN_RIGHT_FRAMES, 'x_flip': False, 'y_flip': False, 'rotation': 90},
    'down':  {'files': _PACMAN_RIGHT_FRAMES, 'x_flip': False, 'y_flip': False, 'rotation': -90},
    'death_up':    {'files': _PACMAN_DEATH_FRAMES, 'x_flip': False, 'y_flip': False, 'rotation': 0},
    'death_down':  {'files': _PACMAN_DEATH_FRAMES, 'x_flip': False, 'y_flip': False, 'rotation': 0},
    'death_right': {'files': _PACMAN_DEATH_FRAMES, 'x_flip': False, 'y_flip': False, 'rotation': 0},
    'death_left':  {'files': _PACMAN_DEATH_FRAMES, 'x_flip': False, 'y_flip': False, 'rotation': 0},
}

GHOST_ANIMATIONS = {
    'right': {
        'frame': [(0, 0), (1, 0)],
        'x_flip': False,
        'y_flip': False,
        'loop_type': 'pingpong',
        'rotation': 0,
    },
    'left': {
        'frame': [(4, 0), (5, 0)],
        'x_flip': False,
        'y_flip': False,
        'loop_type': 'pingpong',
        'rotation': 0,
    },
    'up': {
        'frame': [(6, 0), (7, 0)],
        'x_flip': False,
        'y_flip': False,
        'loop_type': 'pingpong',
        'rotation': 0,
    },
    'down': {
        'frame': [(2, 0), (3, 0)],
        'x_flip': False,
        'y_flip': False,
        'loop_type': 'pingpong',
        'rotation': 0,
    },
    'frightened': {
        'frame': [(0, 5), (1, 5)],
        'x_flip': False,
        'y_flip': False,
        'loop_type': 'pingpong',
        'rotation': 0,
    },
}


FOOD = {
    'cherry': {
        'frame': [(0, 2)],
        'x_flip': False,
        'y_flip': False,
        'default_color': 'white-2',
        'loop_type': 'none',
    },
    'strawberry': {
        'frame': [(1, 2)],
        'x_flip': False,
        'y_flip': False,
        'default_color': 'white-3',
        'loop_type': 'none',
    },
    'orange': {
        'frame': [(2, 2)],
        'x_flip': False,
        'y_flip': False,
        'default_color': 'orange-2',
        'loop_type': 'none',
    },
    'apple': {
        'frame': [(3, 2)],
        'x_flip': False,
        'y_flip': False,
        'default_color': 'white-3',
        'loop_type': 'none',
    },
    'grape': {
        'frame': [(4, 2)],
        'x_flip': False,
        'y_flip': False,
        'default_color': 'white-4',
        'loop_type': 'none',
    },
    'galaxian': {
        'frame': [(5, 2)],
        'x_flip': False,
        'y_flip': False,
        'default_color': 'yellow-2',
        'loop_type': 'none',
    },
}

COLORS = {
    'red': (0, 0),
    'pink': (1, 0),
    'cyan': (2, 0),
    'orange': (3, 0),
    'beige-2': (4, 0),
    'red-2': (0, 1),
    'black': (1, 1),
    'yellow': (2, 1),
    'blue': (3, 1),
    'white': (4, 1),
    'red-3': (0, 2),
    'beige': (1, 2),
    'white-2': (2, 2),
    'white-3': (3, 2),
    'orange-2': (4, 2),
    'white-4': (0, 3),
    'yellow-2': (1, 3),
    'white-5': (2, 3),
    'beige-3': (3, 3),
    'fatih': (4, 3),
}


GOMMES_TILES = {
    'small': (15, 1),
    'big': (15, 3),
}

MACRO_ROW_HEIGHT = 186
LARGE_BLOCK_Y_OFFSET = 82

SMALL_BLOCK = {
    'cell_w': 8, 'cell_h': 8, 'cell_margin': 1,
    'block_w': 199, 'block_margin': 1,
}

LARGE_BLOCK = {
    'cell_w': 16, 'cell_h': 16, 'cell_margin': 1,
    'block_w': 171, 'palette_w': 27, 'block_margin': 2,
}


MAZE_TILE = {
    "corner_outer_top_left": [16, 0],
    "corner_outer_top_right": [18, 0],
    "wall_horizontal_top": [17, 0],
    "corner_outer_bottom_left": [16, 2],
    "wall_vertical_left": [16, 1],
    "wall_fill": [17, 1],
    "corner_inner_top_left": [17, 4],
    "corner_outer_bottom_right": [18, 2],
    "wall_vertical_right": [18, 1],
    "corner_inner_top_right": [18, 4],
    "wall_horizontal_bottom": [17, 2],
    "corner_inner_bottom_left": [17, 5],
    "corner_inner_bottom_right": [18, 5],
    "border_corner_outer_top_left": [16, 3],
    "border_corner_outer_top_right": [19, 3],
    "border_wall_horizontal_top": [20, 0],
    "border_corner_outer_bottom_left": [16, 6],
    "border_wall_vertical_left": [19, 1],
    "border_corner_inner_top_left": [19, 6],
    "border_corner_outer_bottom_right": [17, 6],
    "border_wall_vertical_right": [21, 1],
    "border_corner_inner_top_right": [18, 6],
    "border_wall_horizontal_bottom": [20, 2],
    "border_corner_inner_bottom_left": [17, 3],
    "border_corner_inner_bottom_right": [18, 3],
    "border_corner_inner_top_right_bottom": [16, 4],
    "border_corner_inner_bottom_right_top": [16, 5],
    "border_corner_inner_bottom_left_top": [19, 5],
    "border_corner_inner_top_left_bottom": [19, 4],
}

BORDER_MAPS = {
    "TL": {14: "border_corner_outer_top_left", 15: "wall_fill"},
    "TR": {13: "border_corner_outer_top_right", 15: "wall_fill"},
    "BL": {11: "border_corner_outer_bottom_left", 15: "wall_fill"},
    "BR": {7: "border_corner_inner_top_left", 15: "wall_fill"},
    "T": {
        12: "border_wall_horizontal_bottom",
        13: "border_corner_inner_bottom_left",
        14: "border_corner_inner_bottom_right",
        15: "wall_fill",
    },
    "B": {
        3: "border_wall_horizontal_top",
        7: "border_corner_outer_bottom_right",
        11: "border_corner_inner_top_right",
        15: "wall_fill",
    },
    "L": {
        10: "border_wall_vertical_right",
        11: "border_corner_inner_top_right_bottom",
        14: "border_corner_inner_bottom_right_top",
        15: "wall_fill",
    },
    "R": {
        5: "border_wall_vertical_left",
        7: "border_corner_inner_top_left_bottom",
        13: "border_corner_inner_bottom_left_top",
        15: "wall_fill",
    },
}

CORNER_MAP = {
    0: None,
    1: "corner_outer_top_left",
    2: "corner_outer_top_right",
    3: "wall_horizontal_top",
    4: "corner_outer_bottom_left",
    5: "wall_vertical_left",
    6: "wall_fill",
    7: "corner_inner_top_left",
    8: "corner_outer_bottom_right",
    9: "wall_fill",
    10: "wall_vertical_right",
    11: "corner_inner_top_right",
    12: "wall_horizontal_bottom",
    13: "corner_inner_bottom_left",
    14: "corner_inner_bottom_right",
    15: "wall_fill",
}


ASCII_TILE = {
    '0': (0, 2),
    '1': (1, 2),
    '2': (2, 2),
    '3': (3, 2),
    '4': (4, 2),
    '5': (5, 2),
    '6': (6, 2),
    '7': (7, 2),
    '8': (8, 2),
    '9': (9, 2),
    'A': (0, 3),
    'B': (1, 3),
    'C': (2, 3),
    'D': (3, 3),
    'E': (4, 3),
    'F': (5, 3),
    'G': (6, 3),
    'H': (7, 3),
    'I': (8, 3),
    'J': (9, 3),
    'K': (10, 3),
    'L': (11, 3),
    'M': (12, 3),
    'N': (0, 4),
    'O': (1, 4),
    'P': (2, 4),
    'Q': (3, 4),
    'R': (4, 4),
    'S': (5, 4),
    'T': (6, 4),
    'U': (7, 4),
    'V': (8, 4),
    'W': (9, 4),
    'X': (10, 4),
    'Y': (11, 4),
    'Z': (12, 4),
    '!': (12, 2),
    '"': (10, 2),
    '/': (10, 1),
    '-': (11, 1),
    '.': (12, 1),
    '+': (9, 1),
}

SCORE_SPRITE = {
    '200': (2, 5),
    '400': (3, 5),
    '800': (4, 5),
    '1600': (5, 5),
}
