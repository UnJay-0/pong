import pygame
from math import cos, sin, atan2, pi
from .player import Player
from random import randint

HOLDING_STATE = 0
PLAYING_STATE = 1
GOING_OUT_STATE = 2
OUT_STATE = 3

BALL_STATES = [HOLDING_STATE, PLAYING_STATE, GOING_OUT_STATE, OUT_STATE]

class Ball(pygame.sprite.Sprite):
    """
    Ball of the pong game.
    Controls:
    - The visualization
    - The movement
    - The status of the ball.
    """

    def __init__(self, field_dimensions: tuple):
        """
        Initialise the ball object.

        Parameters
        ----------
        field_dimensions: tuple

            dimension of the playing field as ((0, 500), (100, 200))
            where the first element represents the starting and ending
            line of the horizontal border, instead the second of the vertical
            border.
        """
        super().__init__()
        self.sounds = [pygame.mixer.Sound(f'assets/audio/ping_pong_sound_{i}.mp3')
            for i in range(8)]
        self.image = pygame.image.load('assets/graphics/ball.png').convert_alpha()
        self.state = HOLDING_STATE
        self.magnitude = 10
        self.direction = 0
        self.field_x = field_dimensions[0]
        self.field_y = field_dimensions[1]

    def get_ball_vector(self) -> tuple:
        """
        Returns
        -------
        tuple
            The vector of the ball.
            The vector is composed by magnitude and direction.
        """
        x = int(self.magnitude*cos(self.direction))
        y = int(self.magnitude*sin(self.direction))
        return (x, y)

    def get_size(self) -> tuple:
        """
        Returns
        -------
        tuple
            the size of the ball.
        """
        return self.image.get_size()

    def update_center(self):
        """
        Updates the position of the center of the ball.
        """
        ball_vector = self.get_ball_vector()
        self.rect.centerx += ball_vector[0]
        self.rect.centery += ball_vector[1]
        if self.rect.bottom + ball_vector[1] >= self.field_y[1]:
            self.rect.bottom = self.field_y[1]
        if self.rect.top + ball_vector[1] <= self.field_y[0]:
            self.rect.top = self.field_y[0]

    def movement(self, holding_position=None):
        """
        Based on the state of the ball, this method
        updates the position of the ball.
        If the ball is in holding, it must follow the holding position given.
        If the ball is in playing state, it has to just follow its vector.
        if the ball is going out then other than update its position it must
        check if it is out of the field borders.

        Parameters
        ----------
        holding_position: tuple | None
            the position to follow
        """
        match self.state:
            case _ if self.rect.bottom >= self.field_y[1] or self.rect.top <= self.field_y[0]:
                ball_vector = self.get_ball_vector()
                self.hit((0, 2*ball_vector[1]))
                self.update_center()
            case _ if self.state == HOLDING_STATE:
                self.rect = self.image.get_rect(center=holding_position)
            case _ if self.state == PLAYING_STATE:
                self.update_center()
            case _ if self.state == GOING_OUT_STATE:
                self.update_center()
                if self.is_out():
                    self.state = OUT_STATE

    def is_player_collision(self, player: Player) -> bool:
        """
        Checks if the ball is colliding with the given player.

        Parameters
        ----------
        player: Player
            player to check the collision status

        Returns
        -------
        bool
            True if the player is colliding with the ball.
            False otherwise.
        """
        return self.rect.colliderect(player.rect)

    def hit(self, vector: tuple):
        """
        Hit the ball with an external vector.

        Parameters
        ----------
        vector: tuple
            vector to add to the ball vector.
        """
        ball_vector = self.get_ball_vector()
        res = (ball_vector[0] - vector[0], ball_vector[1] - vector[1])
        self.direction = Ball.adjust_direction(atan2(res[1], res[0]))
        if self.state == HOLDING_STATE:
            self.state +=1
        self.sound_effect()

    def sound_effect(self):
        """
        Generates the sound of the ball hitting a wall or a player.
        """
        i = randint(0, len(self.sounds)-1)
        self.sounds[i].play()

    @staticmethod
    def adjust_direction(radians: float) -> float:
        """
        Limits the degree of the given angle to be in a specific boundaries.

        Parameters
        ----------
        radians: float
            the angle in radians to be adjusted.

        Returns
        -------
        float
            the resulting angle in radians.
        """
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

    def is_out(self) -> bool:
        """
        Verifies if the ball is out of the field borders.

        Returns
        -------
        bool
            True if the ball is out.
            False otherwise.
        """
        return ((self.rect.left < self.field_x[0] and self.rect.right < self.field_x[0]) or
            (self.rect.left > self.field_x[1] and self.rect.right > self.field_x[1]))

    def is_over_player(self, player: Player):
        """
        Verifies if the ball is behind the player.

        Parameters
        ----------
        player - Player
            Player to be checked against.
        """
        lines = [((player.rect.centerx, self.field_y[0]),(player.rect.centerx, self.field_y[1]))]
        for line in lines:
            intersection = self.rect.clipline(line)
            if (intersection != () and
                ((self.rect.centerx > intersection[0][0]
                    and self.rect.right > intersection[0][0]) or
                (self.rect.centerx < intersection[0][0]
                    and self.rect.left < intersection[0][0]))):
                self.state = GOING_OUT_STATE

    def ball_position(self) -> tuple:
        """
        Returns
        -------
        tuple
            the position of the ball
            (top, bottom, left, right)
        """
        return (self.rect.top, self.rect.bottom,
            self.rect.left, self.rect.right)

    def update(self, position: tuple):
        """
        Updates the position of the ball

        Parameters
        ----------
        position: tuple
            position that the ball has to follow
            (just in holding state)
        """
        self.movement(position)

    def reset(self):
        """
        Reset the status of the ball
        """
        self.state = HOLDING_STATE
        self.magnitude = 10
        self.direction = 0

    def serve_positioning(self, position: tuple):
        """
        Puts the ball in a serve position

        Parameters
        ----------
        position: tuple
            position of the serve.
        """
        self.rect = self.image.get_rect(
            center = position)
