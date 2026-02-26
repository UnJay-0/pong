import random
import pygame
from src.utils.constants import UP, DOWN, STAY

MAX_SPEED = 30
PLAYER_1 = "player_1"
PLAYER_2 = "player_2"

class Player(pygame.sprite.Sprite):
    """
    Defines the player visualisation and movement.
    """

    def __init__(self, is_player2: bool, keybindings: dict, field_dimensions: tuple):
        """
        Initialise the player.

        Parameters
        ----------
        is_player2: bool
            True if it is the second player,
            False otherwise.

        keybindings: dict
            Contains the keys references to control the player
            Must contain UP, DOWN keys.

        field_dimensions: tuple

            dimension of the playing field as ((0, 500), (100, 200))
            where the first element represents the starting and ending
            line of the horizontal border, instead the second of the vertical
            border.

        """
        super().__init__()
        self.field_x = field_dimensions[0]
        self.field_y = field_dimensions[1]
        self.image = pygame.image.load('assets/graphics/padel.png').convert_alpha()
        self.is_player2 = is_player2
        if self.is_player2:
            self.name = PLAYER_2
            self.starting_position = (self.field_x[1] - 20,
                (self.field_y[1] - self.field_y[0]) // 2 + self.field_y[0])
            self.rect = self.image.get_rect(
                center=self.starting_position
            )

        else:
            self.name = PLAYER_1
            self.starting_position = (self.field_x[0] + 20,
                (self.field_y[1] - self.field_y[0]) / 2 + self.field_y[0])
            self.rect = self.image.get_rect(
                center=self.starting_position
            )
        self.speed = 0
        self.can_move = False
        self.up = keybindings[UP]
        self.down = keybindings[DOWN]

    def movement(self):
        """
        Controls the movement of the player based on the pressed key.
        """
        keys = pygame.key.get_pressed()
        if keys[self.up] and self.speed >= -MAX_SPEED:
            self.speed -= 2
        elif keys[self.down] and self.speed <= MAX_SPEED:
            self.speed += 2
        else:
            self.speed = 0

    def apply_speed(self):
        """
        Moves the player, limiting it to the field borders.
        """
        self.rect.y += self.speed
        if self.rect.bottom >= self.field_y[1]: self.rect.bottom = self.field_y[1]
        if self.rect.y <= self.field_y[0]: self.rect.y = self.field_y[0]

    def get_vector(self) -> tuple:
        """
        Returns
        -------
        tuple(int, int)
            the vector of the player
        """
        return (0, -self.speed)

    def __str__(self) -> str:
        return self.name

    def update(self, *ball_center):
        """
        Updates the player
        """
        self.movement()
        self.apply_speed()

    def reset(self):
        """
        Resets the player to the starting position.
        """
        self.rect = self.image.get_rect(
            center=self.starting_position
        )
        self.speed = 0

    def serve_position(self, ball_width: int) -> tuple:
        """
        Parameters
        ----------
        ball_width: int
            the width of the ball

        Returns
        -------
        tuple
            the serving position of the ball

        """
        if self.name == PLAYER_1:
            return (self.rect.midright[0] + (ball_width // 2), self.rect.midleft[1])
        else:
            return (self.rect.midleft[0] - (ball_width // 2), self.rect.midleft[1])


class PlayerNPC(Player):
    """
    Defines an NPC player.
    """
    def __init__(self, is_player2: bool, field_dimentions: tuple):
        """
        Initialise the NPC player.

        Parameters
        ----------
        is_player2: bool
            True if it is the second player,
            False otherwise.

        field_dimensions: tuple

            dimension of the playing field as ((0, 500), (100, 200))
            where the first element represents the starting and ending
            line of the horizontal border, instead the second of the vertical
            border.

        """
        super().__init__(is_player2, {UP: 0, DOWN:0}, field_dimentions)
        self.name = "NPC - " + super().__str__()
        self.is_serving = False

    def NPCmovement(self, ball_center: tuple):
        """
        Defines the movement decision of the player based on the ball position.

        Parameters
        ----------
        ball_center: tuple
            the center of the ball.
        """
        if self.is_serving:
            movement_possibilities = [STAY]
            if self.rect.top > self.field_y[0] + 50:
                movement_possibilities.extend([UP, UP])
            if self.rect.bottom < self.field_y[1] - 50:
                movement_possibilities.extend([DOWN, DOWN])
            movement = random.choice(movement_possibilities)
            if movement == UP:
                self.speed -=3
            elif movement == DOWN:
                self.speed +=3
        elif self.can_move:
            if ball_center[1] > self.rect.bottom:
                self.speed +=2
            elif ball_center[1] < self.rect.top:
                self.speed -=2
            else:
                self.speed = 0
        else:
            self.speed = 0

    def serving(self, is_serving: bool):
        """
        Set the player to serve prep or to stop.

        Parameters
        ----------
        is_serving: bool
            True if the player has to serve
            False otherwise.
        """
        self.is_serving = is_serving

    def update(self, ball_center):
        """
        Updates the NPC player
        """
        self.NPCmovement(ball_center)
        self.apply_speed()

    def __str__(self) -> str:
        return self.name
