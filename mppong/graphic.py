import random
import pygame

class GameEngine:
    def __init__(
            self,
            player1="Player 1",
            player2="Player 2",
            width=1200,
            height=700,
            ball_size=40,
            speed=3,
            racket_size=150,
            racket_width=15,
            racket_speed=15,
            multiplayer=False,
            ):
        pygame.init()
        self._width=width
        self._height=height
        self._screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Pong")
        self._multip = multiplayer
        self._ball = Ball(
                width/2,
                height/2,
                ball_size,
                speed,
                )
        self._player1 = Player(player1, racket_size, racket_width,
                racket_speed, "left", height, width)
        self._player2 = Player(player2, racket_size, racket_width,
                racket_speed, "right", height, width)
        self._clock = pygame.time.Clock()
        self._winner = 0
        self._pause = True

    def run(self):
        while self._manage_event():
            if not self._pause:
                self._ball.move()
            self._render()
            if not self._collision():
                break
            pygame.display.flip()
            self._clock.tick(60)
        if self._winner == 0:
            print("No winner")
        else:
            print(f"Player {self._winner} win")
        pygame.quit()

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

    def _move_racket(self, player, direction):
        if self._pause == False:
            player.move(direction)

    def _collision(self):
        if (self._ball.y - self._ball.radius <= 0
            or self._ball.y + self._ball.radius >= self._height):
            self._ball.dy *= -1
        elif (self._ball.rect.colliderect(self._player1.rect)
                or self._ball.rect.colliderect(self._player2.rect)):
            self._ball.dx *= -1
        elif self._ball.x - self._ball.radius <= 0:
            self._winner = self._player2.name
            return False
        elif self._ball.x + self._ball.radius >= self._width:
            self._winner = self._player1.name
            return False
        return True

    def _render(self):
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

class Ball:
    def __init__(self, x, y, radius, speed):
        self._x = x
        self._y = y
        self._radius = radius
        choice = (speed, -speed)
        self._dx = random.choice(choice)
        self._dy = random.choice(choice)

    @property
    def rect(self):
        rect = pygame.Rect(0, 0, self._radius*2, self._radius*2)
        rect.center = (self._x, self._y)
        return rect

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y
    
    @property
    def radius(self):
        return self._radius

    @property
    def dy(self):
        return self._dy

    @dy.setter
    def dy(self, new_dy):
        self._dy = new_dy

    @property
    def dx(self):
        return self._dx

    @dx.setter
    def dx(self, new_dx):
        self._dx = new_dx

    def move(self):
        self._x += self._dx
        self._y += self._dy


class Player:
    def __init__(self, player, size, width, speed, side, screen_height, screen_width):
        self._player = player
        self._size = size
        self._speed = speed
        self._side = side
        self._width = width
        self._screen_height = screen_height
        self._screen_width = screen_width
        self._x, self._y = self._init_position()

    @property
    def rect(self):
        rect = pygame.Rect(self._x, self._y, self._width, self._size)
        return rect

    @property
    def name(self):
        return self._player

    def _collision(self):
        if self._y - self._speed<= 0:
            return True
        elif self._y + self._size + self._speed >= self._screen_height:
            return True
        return False

    def move(self, direction):
        if self._collision() == False:
            if direction == "up":
                self._y -= self._speed
            else:
                self._y += self._speed

    def _init_position(self):
        y = self._screen_height / 2 - self._size / 2
        if self._side == "left":
            x = 1
        else:
            x = self._screen_width - self._width 
        return (x, y)
