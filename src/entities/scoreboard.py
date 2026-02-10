import pygame
BEST_OF_THREE = 3
BEST_OF_FIVE = 5
BEST_OF_SEVEN = 7

class Scoreboard:
    def __init__(self, best_of: int):
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


    def set_win_state(self):
        if self.set_score[0] - self.set_score[1] >= 2 and self.set_score[0] >= 2:
            return 0
        if self.set_score[1] - self.set_score[0] >= 2 and self.set_score[1] >= 2:
            return 1
        return -1

    def match_win_state(self):
        if self.match_score[0] > (self.matches // 2):
            return 0
        if self.match_score[1] > (self.matches // 2):
            return 1
        return -1

    def run_animation(self):
        pass

    def update_score(self, player: int):
        self.set_score[player] += 1
        self.set_numbers[player].next()
        set_win_state = self.set_win_state()
        if set_win_state != -1:
            self.match_score[set_win_state] += 1
            self.match_numbers[player].next()
            self.reset_set()

    def update(self):
        for number in self.set_numbers:
            number.update()
        for number in self.match_numbers:
            number.update()

    def reset_set(self):
        self.set_score = [0, 0]
        for number in self.set_numbers:
            number.reset()

    def reset(self):
        self.reset_set()
        self.match_score = [0, 0]

    def draw(self, screen: pygame.Surface):
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

    def render(self, screen: pygame.Surface):
        if not self.is_animating:
            screen.blit(self.digits[self.current_digit], self.rect.topleft)
        else:
            flip_sprite = self.flip_frames[int(self.current_frame)]
            result = self.create_split_digit(
                self.digits[self.previous_digit],
                self.digits[self.current_digit],
                flip_sprite
            )
            screen.blit(result, self.rect.topleft)

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
