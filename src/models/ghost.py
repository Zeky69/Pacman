import pygame


class Ghost:
    def __init__(self, x=0.0, y=0.0, tile_px=16, speed=2.0, direction="right", color="red"):
        self.x = float(x)
        self.y = float(y)
        self._tile = tile_px
        self.size = tile_px // 2
        self.speed = speed
        self.direction = direction
        self.color = color
        self.frightened = False

    @property
    def col(self):
        return int(self.x // self._tile)

    @property
    def row(self):
        return int(self.y // self._tile)

    @property
    def rect(self):
        h = self.size // 2
        return pygame.Rect(int(self.x) - h, int(self.y) - h, self.size, self.size)

    def update(self, maze, pacman):
        pass


class Blinky(Ghost):
    def __init__(self, x=0.0, y=0.0, tile_px=16, speed=2.0, direction="right"):
        super().__init__(x, y, tile_px, speed, direction, color="red")


class Pinky(Ghost):
    def __init__(self, x=0.0, y=0.0, tile_px=16, speed=2.0, direction="right"):
        super().__init__(x, y, tile_px, speed, direction, color="pink")


class Inky(Ghost):
    def __init__(self, x=0.0, y=0.0, tile_px=16, speed=2.0, direction="right"):
        super().__init__(x, y, tile_px, speed, direction, color="cyan")


class Clyde(Ghost):
    def __init__(self, x=0.0, y=0.0, tile_px=16, speed=2.0, direction="right"):
        super().__init__(x, y, tile_px, speed, direction, color="orange")
