import random
import pygame

class Render:
    def __init__(self, ball, player1, player2):
        self._screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Pong")
        self._ball = ball
        self._player1 = player1
        self._player2 = player2

    def render(self):
        self._screen.fill("black")
        self._draw_ball()
        self._draw_rackets()

    def _draw_ball(self):
        rect = pygame.draw.circle(
                self._screen,
                (255, 0, 100),
                (self._ball.x,
                self._ball.y),
                self._ball.radius
                )

    def _draw_rackets(self):
        rect1 = pygame.draw.rect(
                self._screen,
                (0, 0, 255),
                self._player1.rect)
        rect2 = pygame.draw.rect(
                self._screen,
                (0, 0, 255),
                self._player2.rect)
