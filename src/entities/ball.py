import pygame
from math import cos, sin, atan2, pi
from .player import Player

HOLDING_STATE = "holding"
SERVE_STATE = "serve"
PLAYING_STATE = "playing"
GOING_OUT_STATE = "going out"
OUT_STATE = "out"

class Ball(pygame.sprite.Sprite):
    def __init__(self, field_dimensions: tuple, players: list[Player]):
        super().__init__()
        self.image = pygame.image.load('assets/graphics/ball.png')
        self.rect = self.image.get_rect(
            midleft = players[0].rect.midright)
        self.state = HOLDING_STATE
        self.players = players
        self.magnitude = 10
        self.direction = 0
        self.last_hit = ""
        self.field_x = field_dimensions[0]
        self.field_y = field_dimensions[1]

    def player_input(self):
         keys = pygame.key.get_pressed()
         if keys[pygame.K_SPACE] and self.state == HOLDING_STATE:
             self.state = SERVE_STATE

    def get_ball_vector(self) -> tuple:
        x = int(self.magnitude*cos(self.direction))
        y = int(self.magnitude*sin(self.direction))
        return (x, y)

    def update_center(self):
        ball_vector = self.get_ball_vector()
        self.rect.centerx += ball_vector[0]
        self.rect.centery += ball_vector[1]
        if self.rect.bottom + ball_vector[1] >= self.field_y[1]:
            self.rect.bottom = self.field_y[1]
        if self.rect.top + ball_vector[1] <= self.field_y[0]:
            self.rect.top = self.field_y[0]


    def movement(self):
        match self.state:
            case _ if self.rect.bottom >= self.field_y[1] or self.rect.top <= self.field_y[0]:
                print(self.rect.bottom, self.rect.top)
                ball_vector = self.get_ball_vector()
                print("Wall hit!")
                self.hit((0, 2*ball_vector[1]))
                self.update_center()
            case _ if self.state == HOLDING_STATE:
                self.rect = self.image.get_rect(midleft=self.players[0].rect.midright)
            case _ if self.state == SERVE_STATE:
                self.hit(self.players[0].get_vector())
                self.update_center()
                self.state = PLAYING_STATE
            case _ if self.state == PLAYING_STATE:
                self.update_center()
                for player in self.players:
                    if self.is_player_collision(player) and self.last_hit != str(player):
                        print("Collision!")
                        self.last_hit = str(player)
                        self.hit((2*self.get_ball_vector()[0], player.get_vector()[1]))
                    elif self.is_over_player(player):
                        self.state = GOING_OUT_STATE
            case _ if self.state == GOING_OUT_STATE:
                self.update_center()
                if self.is_out():
                    self.state = OUT_STATE


    def is_player_collision(self, player: Player):
        return self.rect.colliderect(player.rect)

    def hit(self, vector: tuple):
        ball_vector = self.get_ball_vector()
        print(f"ball vector: {ball_vector} \nvector:{vector}")
        res = (ball_vector[0] - vector[0], ball_vector[1] - vector[1])
        print(f"resultant vector: {res}")
        self.direction = Ball.adjust_direction(atan2(res[1], res[0]))
        print(f"direction: {self.direction} , {self.direction*180/pi}\n")
        print(self.last_hit)
        can_move = False
        if self.get_ball_vector()[0] > 0:
            can_move = True
        for player in self.players:
            player.can_move = can_move

    @staticmethod
    def adjust_direction(radians: float) -> float:
        if radians <= (110*pi/180) and radians >= (70*pi/180):
            if radians >= (pi/2):
                return radians + (pi/6)
            else:
                return radians - (pi/6)
        elif radians >= -(110*pi/180) and radians <= -(70*pi/180):
            if radians <= -(pi/2):
                return radians - (pi/6)
            else:
                return radians + (pi/6)
        return radians

    def is_out(self):
        return ((self.rect.left < self.field_x[0] and self.rect.right < self.field_x[0]) or
            (self.rect.left > self.field_x[1] and self.rect.right > self.field_x[1]))

    def is_over_player(self, player: Player):
        lines = [((player.rect.centerx, self.field_y[0]),(player.rect.centerx, self.field_y[1]))]
        for line in lines:
            intersection = self.rect.clipline(line)
            if (intersection != () and
                ((self.rect.centerx > intersection[0][0]
                    and self.rect.right > intersection[0][0]) or
                (self.rect.centerx < intersection[0][0]
                    and self.rect.left < intersection[0][0]))):
                return True
        return False

    def ball_position(self):
        return (self.rect.top, self.rect.bottom,
            self.rect.left, self.rect.right)

    def update(self):
        self.player_input()
        self.movement()

    def reset(self):
        self.rect = self.image.get_rect(
            midleft = self.players[0].rect.midright)
        self.state = HOLDING_STATE
        self.magnitude = 10
        self.direction = 0
        self.last_hit = ""
