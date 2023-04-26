import random
import pygame

class Render:
    def __init__(self, ball, racket1, racket2, screen):
        self._screen = screen
        self._ball = ball
        self._racket1 = racket1
        self._racket2 = racket2
        self._winner_font = pygame.font.SysFont(
                None,
                100)
        self._font = pygame.font.SysFont(
                None,
                32)

    def display_winner(self, winner):
        display_text = f"the winner is {winner}"
        text = self._winner_font.render(display_text, True, (0, 0, 255))
        self._screen.blit(text,
                (self._screen.get_width()/2-len(display_text)*32/2,
                self._screen.get_height()/2 - 32/2))

    def render(self, ball, racket1, racket2):
        self._ball = ball
        self._racket1 = racket1
        self._racket2 = racket2
        self._screen.fill("black")
        self._draw_ball()
        self._draw_rackets()
        self._draw_names()

    def _draw_ball(self):
        rect = pygame.draw.circle(
                self._screen,
                (255, 0, 100),
                (self._ball.x,
                self._ball.y),
                self._ball.radius
                )

    def _draw_rackets(self):
        if self._racket1.player["side"] == "left":
            rect1 = pygame.draw.rect(
                    self._screen,
                    (0, 0, 255),
                    self._racket1.rect)
            rect2 = pygame.draw.rect(
                    self._screen,
                    (0, 0, 255),
                    self._racket2.rect)
        else:
            rect1 = pygame.draw.rect(
                    self._screen,
                    (0, 0, 255),
                    self._racket2.rect)
            rect2 = pygame.draw.rect(
                    self._screen,
                    (0, 0, 255),
                    self._racket1.rect)
    
    def _draw_names(self):
        left = (15, 20)
        right = (self._screen.get_width() - 100, 20)
        if self._racket1.player["side"] == "left":
            text = self._font.render(self._racket1.player["name"], True, (0, 255, 0))
            self._screen.blit(text, left)
            text = self._font.render(self._racket2.player["name"], True, (0, 255, 0))
            self._screen.blit(text, right)
        else:
            text = self._font.render(self._racket1.player["name"], True, (0, 255, 0))
            self._screen.blit(text, right)
            text = self._font.render(self._racket2.player["name"], True, (0, 255, 0))
            self._screen.blit(text, left)
