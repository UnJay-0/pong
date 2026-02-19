import random
import pygame
from src.utils.constants import UP, DOWN, STAY

MAX_SPEED = 30
PLAYER_1 = "player_1"
PLAYER_2 = "player_2"

class Player(pygame.sprite.Sprite):
    def __init__(self, is_player2: bool, keybindings: dict, field_dimensions: tuple):
        super().__init__()
        self.field_x = field_dimensions[0]
        self.field_y = field_dimensions[1]
        self.image = pygame.image.load('assets/graphics/padel.png').convert_alpha()
        self.is_player2 = is_player2
        if self.is_player2:
            self.name = PLAYER_2
            self.starting_position = (self.field_x[1] - 20,
                (self.field_y[1] - self.field_y[0]) / 2 + self.field_y[0])
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
        keys = pygame.key.get_pressed()
        if keys[self.up] and self.speed >= -MAX_SPEED:
            self.speed -= 2
        elif keys[self.down] and self.speed <= MAX_SPEED:
            self.speed += 2
        else:
            self.speed = 0

    def apply_speed(self):
        self.rect.y += self.speed
        if self.rect.bottom >= self.field_y[1]: self.rect.bottom = self.field_y[1]
        if self.rect.y <= self.field_y[0]: self.rect.y = self.field_y[0]

    def get_vector(self):
        return (0, -self.speed)

    def __str__(self) -> str:
        return self.name

    def update(self, *ball_center):
        self.movement()
        self.apply_speed()

    def reset(self):
        self.rect = self.image.get_rect(
            center=self.starting_position
        )
        self.speed = 0

    def serve_position(self, ball_width) -> tuple:
        if self.name == PLAYER_1:
            return (self.rect.midright[0] + (ball_width // 2), self.rect.midleft[1])
        else:
            return (self.rect.midleft[0] - (ball_width // 2), self.rect.midleft[1])


class PlayerNPC(Player):
    def __init__(self, is_player2: bool, field_dimentions: tuple):
        super().__init__(is_player2, {UP: 0, DOWN:0}, field_dimentions)
        self.name = "NPC - " + super().__str__()
        self.is_serving = False

    def NPCmovement(self, ball_center):
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
        self.is_serving = is_serving

    def update(self, ball_center):
        self.NPCmovement(ball_center)
        self.apply_speed()

    def __str__(self) -> str:
        return self.name
