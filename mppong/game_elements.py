import random
import pygame

class Game:
    def __init__(self, index, racket1, racket2):
        self.index = index
        self.racket1 = racket1
        self.racket2 = racket2
        self.pause = True
        self.winner = False
        self.end = False
        self.speed = 0.5

    def switch_pause(self):
        if self.pause:
            self.pause = False
        else:
            self.pause = True

    def __repr__(self):
        return f"Game {self.index} wit {self.racket1!r} and {self.racket2!r}"

class Ball:
    def __init__(self, x, y, radius, speed):
        self.x = x
        self.y = y
        self.radius = radius
        choice = (speed, -speed)
        self.dx = random.choice(choice)
        self.dy = random.choice(choice)

    @property
    def rect(self):
        rect = pygame.Rect(0, 0, self.radius*2, self.radius*2)
        rect.center = (self.x, self.y)
        return rect

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def __repr__(self):
        return f"Ball: ({self.x}, {self.y})"

class Racket:
    def __init__(self, player, size, width, speed, screen_height, screen_width):
        self.player = player
        self._size = size
        self._speed = speed
        self._width = width
        self._screen_height = screen_height
        self._screen_width = screen_width
        self.x, self.y = self._init_position()

    @property
    def rect(self):
        rect = pygame.Rect(self.x, self.y, self._width, self._size)
        return rect

    def _collision(self):
        if self.y - self._speed<= 0:
            return True
        elif self.y + self._size + self._speed >= self._screen_height:
            return True
        return False

    def move(self, direction):
        if self._collision() == False:
            if direction == "up":
                self.y -= self._speed
            else:
                self.y += self._speed

    def _init_position(self):
        y = self._screen_height / 2 - self._size / 2
        if self.player["side"] == "left":
            x = 1
        else:
            x = self._screen_width - self._width 
        return (x, y)

    def __repr__(self):
        return f"Racket {self.player['name']}: ({self.x}, {self.y})"
