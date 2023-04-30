import random
import pygame

class Ball:
    def __init__(self, x, y, radius, speed):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self._init_speed()

    @property
    def rect(self):
        rect = pygame.Rect(0, 0, self.radius*2, self.radius*2)
        rect.center = (self.x, self.y)
        return rect

    def _init_speed(self):
        choice = (self.speed, -self.speed)
        self.dx = random.choice(choice)
        self.dy = random.choice(choice)

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def __eq__(self, other):
        if not isinstance(other, Ball):
            return NotImplemented
        return (self.x == other.x and self.y == other.y and self.radius == other.radius and
               self.speed == other.speed and self.dx == other.dx and self.dy == other.dy)

    def __repr__(self):
        return f"Ball: ({self.x}, {self.y}) speed ({self.dx},{self.dy}), radius {self.radius}"

    @classmethod
    def from_dict(cls, dict_init):
        obj = cls(dict_init["x"],
                dict_init["y"],
                dict_init["radius"],
                dict_init["speed"])

        obj.dx = dict_init["dx"]
        obj.dy = dict_init["dy"]
        return obj


class Racket:
    def __init__(self, player, size, width, speed, screen_height, screen_width):
        self.player = player
        self._size = size
        self._speed = speed
        self._width = width
        self._screen_height = screen_height
        self._screen_width = screen_width
        self._init_position()

    @property
    def rect(self):
        rect = pygame.Rect(self.x, self.y, self._width, self._size)
        return rect

    def _init_position(self):
        self.y = self._screen_height / 2 - self._size / 2
        if self.player["side"] == "left":
            self.x = 1
        else:
            self.x = self._screen_width - self._width 

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

    def __repr__(self):
        return f"Racket {self.player['name']}: ({self.x}, {self.y})"

    @classmethod
    def from_dict(cls, dict_init):
        obj =  cls(dict_init["player"],
                dict_init["_size"],
                dict_init["_speed"],
                dict_init["_width"],
                dict_init["_screen_height"],
                dict_init["_screen_width"],)
        return obj

    def __eq__(self, other):
        if not isinstance(other, Racket):
            return NotImplemented
        return (self.player == other.player and self._size == other._size and
                self._width== other._width and self.x == other.x and self.y == other.y and
               self._screen_height == other._screen_height)
