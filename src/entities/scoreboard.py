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
    """
    Defines the Scoreboard of a game.
    It controls the set and match score and score animation.
    """

    def __init__(self, best_of: int, set_points: int, field_dimensions: tuple):
        """
        Initialise the scoreboard.

        Parameters
        ----------
        best_of: int
            maximum number of matches to play.
        set_points: int
            maximum number of set per match.
        field_dimensions:

            dimension of the playing field as ((0, 500), (100, 200))
            where the first element represents the starting and ending
            line of the horizontal border, instead the second of the vertical
            border.
        """
        self.set_score = [0, 0]
        self.match_score = [0, 0]
        self.matches = best_of
        self.max_set_points = set_points
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
        """
        Increase the ball hit counter.
        """
        self.hit_counter +=1

    def set_win_state(self) -> int:
        """
        Verifies if one of the players won the set

        Returns
        -------
        int
            0 if player 1 wins the set.
            1 if player 2 wins the set.
            -1 if there isn't a winner yet.
        """
        if self.set_score[0] - self.set_score[1] >= WIN_STATE_FACTOR and self.set_score[0] >= self.max_set_points:
            return 0
        if self.set_score[1] - self.set_score[0] >= WIN_STATE_FACTOR and self.set_score[1] >= self.max_set_points:
            return 1
        return -1

    def match_win_state(self):
        """
        Verifies if one of the players won the game

        Returns
        -------
        int
            0 if player 1 wins the game.
            1 if player 2 wins the game.
            -1 if there isn't a winner yet.
        """
        if self.match_score[0] > (self.matches // WIN_STATE_FACTOR):
            return 0
        if self.match_score[1] > (self.matches // WIN_STATE_FACTOR):
            return 1
        return -1

    def is_animating(self) -> bool:
        """
        Verifies if the score event message is animating.
        Returns
        -------
        bool
         True if it is animating
         False otherwise.
        """
        return self.message.visible

    def update_score(self, player: int):
        """
        Updates the score of the given player

        Parameters
        ----------
        player: int
            player who scored
        """
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
        """
        Updates the scoreboard.
        """
        for number in self.set_numbers:
            number.update()
        for number in self.match_numbers:
            number.update()
        if (not self.message.message_animation_status()
            and self.message.current != WIN):
            self.message.set_visibility(False)
        self.message.update()

    def reset_set(self):
        """
        Resets the set score.
        """
        self.set_score = [0, 0]
        for number in self.set_numbers:
            number.reset()

    def reset(self):
        """
        Resets the set and match score and hit counter.
        """
        self.reset_set()
        self.match_score = [0, 0]
        for number in self.match_numbers:
            number.reset()
        self.message.reset()
        self.hit_counter = 0

    def draw(self, screen: pygame.Surface):
        """
        Draws the scoreboard on the given surface.

        Parameters
        ----------
        surface: pygame.Surface
            surface to be draw over
        """
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
    """
    Defines the number with various possible digits.
    """
    def __init__(self, positions: list[tuple], number_of_digits: int, scale_factor=1):
        """
        Initialise the number.

        Parameters
        ----------
        positions: list[tuple]
            positions of each digits of the numbers.
        number_of_digits: int
            number of digits.
        scale_factor: int
            the factor for scale the digits.
        """
        self.digits = [
            Digit(positions[digit], scale_factor)
            for digit in range(number_of_digits)
        ]

    def get_position(self) -> tuple:
        """
        Returns
        -------
        tuple
            position of the number.
        """
        return self.digits[0].get_position()

    def next(self):
        """
        Increase the current number.
        """
        index = -1
        while True:
            carry_over = self.digits[index].next()
            if carry_over == 0:
                break
            else:
                index -= 1

    def set_number(self, number:int):
        """
        Set the current number to the given number.

        Parameters
        ----------
        number: int
            number to set.
        """
        if number == 0:
            self.digits[0].set_number(number)
            return
        digit_index = len(self.digits) -1
        while(number != 0 or digit_index != -1):
            number, remainder = divmod(number, 10)
            self.digits[digit_index].set_number(remainder)
            digit_index -= 1

    def get_number(self) -> int:
        """
        Get the number value.

        Returns
        -------
        int
            the int value of the number.
        """
        number = 0
        for i in range(len(self.digits)):
            number += self.digits[i].current_digit * ((i * 10) if i != 0 else 1)
        return number

    def update(self):
        """
        Updates the number
        """
        for digit in self.digits:
            digit.update()

    def reset(self):
        """
        Reset the numbers.
        """
        for digit in self.digits:
            digit.reset()

    def render(self, surface: pygame.Surface):
        """
        Draw the number over the given surface.

        Parameters
        ----------
        surface: pygame.Surface
            surface to be drawn over.
        """
        for digit in reversed(self.digits):
            digit.render(surface)

class Digit(pygame.sprite.Sprite):
    """
    Digit of a number
    """
    def __init__(self, position: tuple, scale_factor=1):
        """
        Initialise the digit

        Parameters
        ----------
        position: tuple
            position of the digit
        scale_factor: int
            the factor for scale the digits.
        """
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

    def get_position(self) -> tuple:
        """
        Returns
        -------
        tuple
            position of the digit.
        """
        return self.rect.topleft

    def set_number(self, number:int):
        """
        Set the digit to the given single digit number.

        Parameters
        ----------
        number: int
            Single digit number to set.

        """
        self.current_digit = number

    def next(self) -> int:
        """
        Returns
        -------
        int
            1 if the digits reach 10
            0 otherwise.
        """
        self.start_flip()
        self.previous_digit = self.current_digit
        self.current_digit = self.current_digit + 1
        if self.current_digit == 10:
            self.previous_digit = 9
            self.current_digit = 0
            return 1
        return 0

    def start_flip(self):
        """
        Start the animation.
        """
        self.is_animating = True
        self.current_frame = 0

    def add(self, to_add: int):
        """
        Add the value given to the current digits.

        Parameters
        ----------
        to_add: int
            value to add
        """
        self.current_digit += to_add
        carry_over = self.current_digit // 10
        self.current_digit %= 10
        return carry_over

    def update(self):
        """
        Updates the digits.
        """
        if self.is_animating:
            self.current_frame += 0.2
            if self.current_frame >= len(self.flip_frames):
                self.is_animating = False
                self.current_frame = 0

    def render(self, surface: pygame.Surface):
        """
        Draws the digits over the given surface.

        Parameters
        ----------
        surface: pygame.Surface
            surface to be drawn over.
        """
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

    def create_split_digit(self, previous: pygame.Surface, current: pygame.Surface, flip: pygame.Surface) -> pygame.Surface:
        """
        Create the animation frame where half of the image is composed
        by the previous number and the other half to the current one.

        Parameters
        ----------
        previous: pygame.image.Image
            Previous digit number.
        current: pygame.image.Image
            Currenr digit number.
        flip_sprite: pygame.Surface
            Separator between the numbers.

        Returns
        -------
        Surface
            Resulting image from the transition.
        """
        width, height = previous.get_size()
        result = pygame.Surface((width, height), pygame.SRCALPHA)
        boundary_y = self.extract_first_boundary(flip)
        for x in range(width):
            split_y = boundary_y[x]
            for y in range(0, split_y):
                result.set_at((x, y), previous.get_at((x, y)))
            for y in range(split_y, height):
                result.set_at((x, y), current.get_at((x, y)))
        result.blit(flip, (0, 0))
        return result

    def extract_first_boundary(self, flip: pygame.Surface) -> list:
        """
        Extract the first boundary from above of the flip animation frame.

        Parameters
        ----------
        flip: pygame.Surface
            surface from which extract the first boundary.

        Returns
        -------
        list
            list of points that determines the boundary.
            The indices are x coordinates, the elements are y coordinate.
        """
        width, height = flip.get_size()
        boundary = []
        for x in range(width):
            boundary_y = height
            for y in range(height):
                pixel = flip.get_at((x, y))
                if pixel.a > 128:  # Found transparent area (flipped part)
                    boundary_y = y
                    break
            boundary.append(boundary_y)
        return boundary

    def reset(self):
        """
        Resets the Digit.
        """
        self.current_digit = 0
        self.is_animating = False
        self.current_frame = 0


    def __str__(self):
        return f"index: {self.current_digit}"


class MessageEvent(pygame.sprite.Sprite):
    """
    Represents a message caused by an event in game.
    Manages the sprite and the animation.
    """
    def __init__(self, position: tuple):
        """
        Constructs the MessageEvent.

        Parameters
        ----------
        position: tuple
            position of the message.
        """
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
        """
        Sets the visibility of the message.

        Parameters
        ----------
        is_visible: bool
            True if the message should be visible
            False otherwise.
        """
        self.visible = is_visible

    def message_animation_status(self) -> bool:
        """
        Determines if the message is still animating.

        Returns
        -------
        bool
            True if the message is still animating
            False otherwise.
        """
        return self.pixel_size > -10

    def set_message(self, message: str, player_number: int=-1):
        """
        Sets the message from the ones available, dedicated to the
        specified player.

        Parameters
        ----------
        message: str
            Type of message to be displayed.
        player_number: int
            Player to dedicate the message.
        """
        self.current = message
        self.image = self.messages[message].copy()
        if player_number != -1:
            self.player_numbers[player_number].render(self.image)
        self.rect = self.image.get_rect(center=self.position)


    def render(self, surface: pygame.Surface):
        """
        Draws the messsage on the given surface if the
        message is set visible.

        Parameters
        ----------
        surface: pygame.Surface
            surface where the message will be drawn.
        """
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
        """
        Resets the message.
        """
        self.pixel_size = 10
        self.current = ""
        self.visible = False

    def update(self):
        """
        Updates the message.
        """
        if self.visible:
            self.pixel_size -= 0.2
