from graphic import Render
from game_elements import Racket, Ball
import pygame
import random

class GameEngine:
    def __init__(
            self,
            player1,
            player2,
            server=False,
            internet=False,
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
        self.ball = Ball(
                width/2,
                height/2,
                ball_size,
                speed,
                )
        self._internet = internet
        self._pause = True
        self.racket1 = Racket(player1, racket_size, racket_width,
                racket_speed, height, width)
        self.racket2 = Racket(player2, racket_size, racket_width,
                racket_speed, height, width)
        self._winner = False
        if not server:
            pygame.init()
            self._screen = pygame.display.set_mode((width, height))
            pygame.display.set_caption("Pong")
            self._clock = pygame.time.Clock()
            self._render = Render(self.ball, self.racket1, self.racket2, self._screen)

    @classmethod
    def from_game(cls, game):
        obj = cls(game.racket1.player, game.racket2.player)
        obj.racket1 = game.racket1
        obj.racket2 = game.racket2
        obj.internet = True

    def run(self):
        while self._manage_event():
            if not self._pause:
                self.ball.move()
            self._render.render(self.ball, self.racket1, self.racket2)
            if self._collision():
                self._winner = True
                self._pause = True
            if self._winner == True:
                self._render.display_winner(self.get_winner()["name"])
            pygame.display.flip()
            self._clock.tick(60)
        pygame.quit()

    def get_winner(self):
        if self._winner == True:
            if self.racket1.player["winner"]:
                return self.racket1.player
            else:
                return self.racket2.player
        return False

    def run_as_client(self, name, game):
        if game.pause:
            self._pause = True
        else:
            self._pause = False
        self._ball = ball
        local_racket, opponent = self._get_local(name)
        self._render(ball, local_player, opponent)
        if not self._manage_event():
            game.end = True
        if self._pause:
            game.pause = True
        return (event, local_player)

    def run_as_server(self, game):
        self._manager_event_server(event)
        if not game.pause:
            self.game.ball.move()
            self.racket1 = game.racket1
            self.racket2 = game.racket2
            if not self.collision():
                return False
            return True

    def _get_local(self, name):
        if self._racket1.player["name"] == name:
            return self._racket1, self._racket2
        else:
            return self._racket2, self._racket1

    def _get_left_and_right(self):
        if self._internet:
            if self.racket1.player["local"]:
                return self.racket2, self.racket1
            else:
                return self.racket1, self.racket2
        if self.racket1.player["side"] == "left":
            return self.racket1, self.racket2
        else:
            return self.racket2, self.racket1

    def _manage_event(self):
        left, right = self._get_left_and_right()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_w:
                    self._move_racket(left, "up")
                elif event.key == pygame.K_s:
                    self._move_racket(left, "down")
                elif event.key == pygame.K_UP:
                    self._move_racket(right, "up")
                elif event.key == pygame.K_DOWN:
                    self._move_racket(right, "down")
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
            racket.move(direction)

    def _collision(self):
        if (self.ball.y - self.ball.radius <= 0
            or self.ball.y + self.ball.radius >= self._height):
            self.ball.dy *= -1
        elif (self.ball.rect.colliderect(self.racket1.rect)
                or self.ball.rect.colliderect(self.racket2.rect)):
            self.ball.dx *= -1
        elif self.ball.x - self.ball.radius <= 0:
            self.racket2.player["winner"] = True
            return True
        elif self.ball.x + self.ball.radius >= self._width:
            self.racket1.player["winner"] = True
            return True
        return False
