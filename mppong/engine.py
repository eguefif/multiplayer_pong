from graphic import Render
from game_elements import Player, Ball
import pygame
import random

class GameEngine:
    def __init__(
            self,
            player1,
            player2,
            server=False,
            width=1200,
            height=700,
            ball_size=40,
            speed=3,
            racket_size=150,
            racket_width=15,
            racket_speed=15,
            ):
        self._width=width
        self._height=height
        self._ball = Ball(
                width/2,
                height/2,
                ball_size,
                speed,
                )
        self._pause = True
        self._racket1 = Racket(player1, racket_size, racket_width,
                racket_speed, height, width)
        self._racket2 = Racket(player2, racket_size, racket_width,
                racket_speed, height, width)
        self._screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Pong")
        if not server:
            self._clock = pygame.time.Clock()
            render = Render(ball, racket1, racket2, self._screen)

    def run(self):
        while self._manage_event():
            if not self._pause:
                self._ball.move()
            self._render(ball, racket1, racket2)
            if self._collision():
                break
            pygame.display.flip()
            self._clock.tick(60)
        pygame.quit()

    def get_winner(self):
        if self._racket1.player["winner"]:
            return self._racket1.player
        else:
            return self._racket2.player

    def run_as_client(self, opponent, ball, pause):
        if pause == "pause":
            self._pause = True
        else:
            self._pause = False
        self._ball = ball
        local_player = self._get_local
        self._render(ball, local_player, opponent)
        event = self._manage_event()
        return (event, local_player)
    
    def _get_local(self):
        if self._racket1.player["local"]:
            return self._racket1
        else:
            return self._racket2

    def run_as_server(self, racket1, racket2, event):
        self._manager_event_server(event)
        if event != "pause":
            self._ball.move()
            self._racket1 = racket1
            self._racket2 = racket2
            if not self.collision():
                return (1, self._winner)
            return (0, ball, racket1, racket2)

    def _manage_event(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_w:
                    self._move_racket(self._player1, "up")
                elif event.key == pygame.K_s:
                    self._move_racket(self._player1, "down")
                elif event.key == pygame.K_UP:
                    self._move_racket(self._player2, "up")
                elif event.key == pygame.K_DOWN:
                    self._move_racket(self._player2, "down")
                elif event.key == pygame.K_SPACE:
                    self._switch_pause()
            if event.type == pygame.QUIT:
                return False
        return True

    def _switch_pause(self):
        if self._pause == True:
            self._pause = False
        else:
            self._pause = True

    def _move_racket(self, racket, direction):
        if not self._pause and racket.player["local"]:
            player.move(direction)

    def _collision(self):
        if (self._ball.y - self._ball.radius <= 0
            or self._ball.y + self._ball.radius >= self._height):
            self._ball.dy *= -1
        elif (self._ball.rect.colliderect(self._player1.rect)
                or self._ball.rect.colliderect(self._player2.rect)):
            self._ball.dx *= -1
        elif self._ball.x - self._ball.radius <= 0:
            self._racket2.player["winner"] = True
            return False
        elif self._ball.x + self._ball.radius >= self._width:
            self._racket1.player["winner"] = True
            return False
        return True
