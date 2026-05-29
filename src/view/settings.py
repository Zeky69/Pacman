
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
	
}

SMALL_BLOCK = {
    'cell_w': 8, 'cell_h': 8, 'cell_margin': 1, 
    'block_w': 199, 'block_margin': 1
}

LARGE_BLOCK = {
    'cell_w': 16, 'cell_h': 16, 'cell_margin': 1, 
    'block_w': 171, 'palette_w': 27, 'block_margin': 2
}





MAZE_TILE = {
  "corner_outer_top_left": [16,0],
  "wall_horizontal_top": [17, 0],
  "corner_outer_top_right": [18,0],
  "corner_outer_top_left_hollow": [19,0],
  "wall_horizontal_top_hollow": [20,0],
  "corner_outer_top_right_hollow": [21,0],
  "wall_vertical_left": [16,1],
  "wall_fill": [17,1],
  "wall_vertical_right": [18,1],
  "wall_vertical_left_hollow": [19,1],
  "empty": [20,1],
  "wall_vertical_right_hollow": [21,1],
  "corner_outer_bottom_left": [16,2],
  "wall_horizontal_bottom": [17,2],
  "corner_outer_bottom_right": [18,2],
  "corner_outer_bottom_left_hollow": [19,2],
  "wall_horizontal_bottom_hollow": [20,2],
  "corner_outer_bottom_right_hollow": [21,2],
  "junction_t_right": [16,4],
  "corner_inner_top_left": [17,4],
  "corner_inner_top_right": [18,4],
  "junction_t_left_b": [19,4],
  "junction_cross": [16,5],
  "corner_inner_bottom_left": [17,5],
  "corner_inner_bottom_right": [18,5],
  "junction_cross_c": [19,5],
  "wall_end_left": [16,6],
  "wall_end_bottom_left": [17,6],
  "wall_end_bottom_right": [18,6],
  "wall_end_right": [19,6],
  "wall_horizontal_bottom_b": [19,7]
}