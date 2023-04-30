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

