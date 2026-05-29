
PACMAN_ANIMATIONS = {
    'right': {'frame': [(6, 3), (6, 4), (6, 5)],
              'x_flip': False, 
              'y_flip': False,
              'loop_type': 'pingpong',
              'rotation': 0
              },

    'left':  {'frame': [(6, 3), (6, 4), (6, 5)],
              'x_flip': True, 
              'y_flip': False,
              'loop_type': 'pingpong',
              'rotation': 0
              },

    'up':    {'frame': [(7, 3), (7, 4), (6, 5)],
              'x_flip': False, 
              'y_flip': True,
			  'loop_type': 'pingpong',
			  'rotation': 0
              },

    'down':  {'frame':  [(7, 3), (7, 4), (6, 5)],
              'x_flip': False, 
              'y_flip': False,
			  'loop_type': 'pingpong',
			  'rotation': 0
              },
    'death_up': {'frame': [(0, 3), (1, 3),(2, 3),(3, 3),(4, 3),(5, 3),
                        (0, 4), (1, 4),(2, 4),(3, 4),(4, 4),(5, 4)],
              'x_flip': False,
              'y_flip': False,
              'loop_type': 'once',
              'rotation': 0
              },
    'death_down': {'frame': [(0, 3), (1, 3),(2, 3),(3, 3),(4, 3),(5, 3),
                        (0, 4), (1, 4),(2, 4),(3, 4),(4, 4),(5, 4)],
                  'x_flip': False,
                  'y_flip': True,
                  'loop_type': 'once',
                  'rotation': 0
                  },
    'death_right': {'frame': [(0, 3), (1, 3),(2, 3),(3, 3),(4, 3),(5, 3),
						(0, 4), (1, 4),(2, 4),(3, 4),(4, 4),(5, 4)],
				  'x_flip': False,
				  'y_flip': False,
				  'loop_type': 'once',
				  'rotation': 90
				  },
    'death_left': {'frame': [(0, 3), (1, 3),(2, 3),(3, 3),(4, 3),(5, 3),
						(0, 4), (1, 4),(2, 4),(3, 4),(4, 4),(5, 4)],
				  'x_flip': False,
				  'y_flip': False,
				  'loop_type': 'once',
				  'rotation': -90
				  }
}

GHOST_ANIMATIONS = {
	'right': {'frame': [(0, 0), (1, 0)],
			  'x_flip': False, 
			  'y_flip': False,
			  'loop_type': 'pingpong',
			  'rotation': 0
			  },
	'left':  {'frame': [(4,0), (5, 0)],
			  'x_flip': False, 
			  'y_flip': False,
			  'loop_type': 'pingpong',
			  'rotation': 0
			  },
	'up':    {'frame': [(6, 0), (7, 0)],
			  'x_flip': False, 
			  'y_flip': False,
			  'loop_type': 'pingpong',
			  'rotation': 0
			  },
	'down':  {'frame': [(2, 0), (3, 0)],
			  'x_flip': False, 
			  'y_flip': False,
			  'loop_type': 'pingpong',
			  'rotation': 0
			  },
	'frightened': {'frame': [(0, 5), (1, 5)],
				 'x_flip': False, 
				 'y_flip': False,
				 'loop_type': 'pingpong',
				 'rotation': 0
				 },
}


FOOD = {
	'cherry': (0, 3),
	'strawberry': (1, 3),
	'orange': (2, 3),
	'apple': (3, 3),
	'grape': (4, 3),
	'galaxian': (5, 3),
}

COLORS = {
	'red': (0, 0),
	'pink': (1, 0),
	'cyan': (2, 0),
	'orange': (3, 0),
	'black': (1, 1),
	'yellow': (2, 1),
	'blue': (3, 1),
}


GOMMES_TILES = {
	'small': (15, 1),
	'big': (15, 3)
}


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