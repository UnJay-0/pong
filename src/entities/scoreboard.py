import os
import pygame
from src.utils.constants import FILE_NAME_SEPARATOR
BEST_OF_THREE = 3
BEST_OF_FIVE = 5
BEST_OF_SEVEN = 7
WIN_STATE_FACTOR = 2
ACE = "ace"
SCORE = "score"
WIN = "win"
MESSAGES = [ACE, SCORE, WIN]

class Scoreboard:
    def __init__(self, best_of: int, field_dimensions):
        self.set_score = [0, 0]
        self.match_score = [0, 0]
        self.matches = best_of
        self.set_numbers = [Number([(215, 9), (290, 9)], 2), Number([(424, 9), (499, 9)], 2)]
        self.match_numbers = [Number([(360, 20)], 1, 1/2), Number([(395, 20)], 1, 1/2)]
        self.background = pygame.image.load("assets/graphics/scoreboard_back_v2.png").convert_alpha()
        self.match_score_background = pygame.transform.scale_by(
            pygame.image.load("assets/graphics/scoreboard_back.png").convert_alpha(),
            1/2)
        self.last_hit = 0
        self.hit_counter = 0
        self.message = MessageEvent((field_dimensions[0][1]//2,
            field_dimensions[1][1]//2))

    def increase_hit_counter(self):
        self.hit_counter +=1

    def set_win_state(self):
        if self.set_score[0] - self.set_score[1] >= WIN_STATE_FACTOR and self.set_score[0] >= WIN_STATE_FACTOR:
            return 0
        if self.set_score[1] - self.set_score[0] >= WIN_STATE_FACTOR and self.set_score[1] >= WIN_STATE_FACTOR:
            return 1
        return -1

    def match_win_state(self):
        if self.match_score[0] > (self.matches // WIN_STATE_FACTOR):
            return 0
        if self.match_score[1] > (self.matches // WIN_STATE_FACTOR):
            return 1
        return -1

    def is_animating(self):
        return self.message.visible

    def update_score(self, player: int):
        self.message.reset()
        self.message.set_visibility(True)
        if self.hit_counter == 1:
            self.message.set_message(ACE)
        else:
            self.message.set_message(SCORE, player)
        self.set_score[player] += 1
        self.set_numbers[player].next()
        set_win_state = self.set_win_state()
        if set_win_state != -1:
            self.match_score[set_win_state] += 1
            self.match_numbers[player].next()
            self.reset_set()
            if self.match_win_state() != -1:
                self.message.set_message(WIN, player)

    def update(self):
        for number in self.set_numbers:
            number.update()
        for number in self.match_numbers:
            number.update()
        if (not self.message.message_animation_status()
            and self.message.current != WIN):
            self.message.set_visibility(False)
        self.message.update()

    def reset_set(self):
        self.set_score = [0, 0]
        for number in self.set_numbers:
            number.reset()

    def reset(self):
        self.reset_set()
        self.match_score = [0, 0]
        for number in self.match_numbers:
            number.reset()
        self.message.reset()
        self.hit_counter = 0

    def draw(self, screen: pygame.Surface):
        self.message.render(screen)
        screen.blit(self.background, (227, 13))
        for number in self.set_numbers:
            number.render(screen)
        for number in self.match_numbers:
            screen.blit(self.match_score_background, number.get_position())
            number.render(screen)

    def __str__(self):
        return f"set: {self.set_score[0]} - {self.set_score[1]}\nmatch: {self.match_score[0]} - {self.match_score[1]}"


class Number():
    def __init__(self, positions: list[tuple], digits_number: int, scale_factor=1):
        self.digits = [
            Digit(positions[digit], scale_factor)
            for digit in range(digits_number)
        ]

    def get_position(self):
        return self.digits[0].get_position()

    def next(self):
        index = -1
        while True:
            carry_over = self.digits[index].next()
            if carry_over == 0:
                break
            else:
                index -= 1

    def update(self):
        for digit in self.digits:
            digit.update()

    def reset(self):
        for digit in self.digits:
            digit.reset()

    def render(self, screen):
        for digit in reversed(self.digits):
            digit.render(screen)

class Digit(pygame.sprite.Sprite):
    def __init__(self, position: tuple, scale_factor=1):
        super().__init__()
        self.current_digit = 0
        self.previous_digit = 0
        self.digits = [
            pygame.transform.scale_by(
                pygame.image.load(f'assets/graphics/numbers/{digit}.png').convert_alpha(), scale_factor)
            for digit in range(10)
        ]
        self.image = self.digits[self.current_digit]
        self.rect = self.image.get_rect(topleft=position)
        self.is_animating = False
        self.current_frame = 0
        self.flip_frames = [
            pygame.transform.scale_by(
                pygame.image.load(f"assets/graphics/scoreboard_animation/scoreboard_animation{frame}.png").convert_alpha(), scale_factor)
            for frame in range(1, 10)
        ]

    def get_position(self):
        return self.rect.topleft

    def set_number(self, number:int):
        self.current_digit = number

    def next(self) -> int:
        self.start_flip()
        self.previous_digit = self.current_digit
        self.current_digit = self.current_digit + 1
        if self.current_digit == 10:
            self.previous_digit = 9
            self.current_digit = 0
            return 1
        return 0

    def start_flip(self):
        self.is_animating = True
        self.current_frame = 0

    def add(self, to_add: int):
        self.current_digit += to_add
        carry_over = self.current_digit // 10
        self.current_digit %= 10
        return carry_over

    def update(self):
        if self.is_animating:
            self.current_frame += 0.2
            if self.current_frame >= len(self.flip_frames):
                self.is_animating = False
                self.current_frame = 0

    def render(self, surface: pygame.Surface):
        if not self.is_animating:
            surface.blit(self.digits[self.current_digit], self.rect.topleft)
        else:
            flip_sprite = self.flip_frames[int(self.current_frame)]
            result = self.create_split_digit(
                self.digits[self.previous_digit],
                self.digits[self.current_digit],
                flip_sprite
            )
            surface.blit(result, self.rect.topleft)

    def create_split_digit(self, previous, current, flip_sprite):
        width, height = previous.get_size()
        result = pygame.Surface((width, height), pygame.SRCALPHA)
        boundary_y = self.extract_first_boundary(flip_sprite)
        for x in range(width):
            split_y = boundary_y[x]
            for y in range(0, split_y):
                result.set_at((x, y), previous.get_at((x, y)))
            for y in range(split_y, height):
                result.set_at((x, y), current.get_at((x, y)))
        result.blit(flip_sprite, (0, 0))
        return result

    def extract_first_boundary(self, flip_sprite):
        width, height = flip_sprite.get_size()
        boundary = []
        for x in range(width):
            boundary_y = height
            for y in range(height):
                pixel = flip_sprite.get_at((x, y))
                if pixel.a > 128:  # Found transparent area (flipped part)
                    boundary_y = y
                    break
            boundary.append(boundary_y)
        return boundary

    def reset(self):
        self.current_digit = 0


    def __str__(self):
        return f"index: {self.current_digit}"


class MessageEvent(pygame.sprite.Sprite):
    def __init__(self, position: tuple):
        self.visible = False
        self.pixel_size = -10
        self.position = position
        self.messages = {}
        self.current = ""
        path = "assets/graphics/event_messages/"
        event_messages = os.listdir(path)
        for message in event_messages:
            name = message.split(FILE_NAME_SEPARATOR)[0]
            if name in MESSAGES:
                self.messages[name] = pygame.image.load(path + message).convert_alpha()

        self.player_numbers = [Digit((400, 230)), Digit((400, 230))]
        self.player_numbers[0].set_number(1)
        self.player_numbers[1].set_number(2)

    def set_visibility(self, is_visible: bool):
        self.visible = is_visible

    def message_animation_status(self):
        return self.pixel_size > -10

    def set_message(self, message: str, player_number: int=-1):
        self.current = message
        self.image = self.messages[message].copy()
        if player_number != -1:
            self.player_numbers[player_number].render(self.image)
        self.rect = self.image.get_rect(center=self.position)


    def render(self, surface: pygame.Surface):
        if self.visible:
            background = pygame.transform.box_blur(surface, 5)
            if self.pixel_size >= 1:
                pixelated_message = pygame.transform.pixelate(self.image, int(self.pixel_size))
                surface.blit(background, (0,0))
                surface.blit(pixelated_message, self.rect.topleft)
            else:
                surface.blit(background, (0,0))
                surface.blit(self.image, self.rect.topleft)

    def reset(self):
        self.pixel_size = 10
        self.current = ""

    def update(self):
        if self.visible:
            self.pixel_size -= 0.2
