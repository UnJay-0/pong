import pygame
from src.utils.constants import UP, DOWN

START_GAME = "Start Game"
PAUSE = "Pause Game"
RESTART_GAME = "Reset Game"
GAME_SETTINGS = "Confirm"
EXIT_GAME = "Leave"


class Menu():
    def __init__(self, keybindings: dict, button_names: list[str]):
        self.buttons = []
        y_position = 220
        for name in button_names:
            self.buttons.append(Button((400, y_position), name))
            y_position += 80
        self.logo = pygame.image.load('assets/graphics/logo.png')
        self.logo_position = (220, 30)
        self.is_visible = False
        self.cursor = 0
        self.keybindings = keybindings
        self.mouse_last_pos = (0, 0)
        self.mouse_control = False
        self.hover_sound = pygame.mixer.Sound("assets/audio/hover_sound.mp3")
        self.confirm_sound = pygame.mixer.Sound("assets/audio/selection_sound.mp3")

    def check_highlight(self, mouse_pos:tuple):
        new_cursor = self.hover_highlight(mouse_pos)
        if new_cursor != None:
            self.check_hover_sound(new_cursor)
            self.highlight(new_cursor)
            return
        new_cursor = self.selection_highlight()
        if new_cursor != None:
            self.check_hover_sound(new_cursor)
            self.highlight(new_cursor)

    def check_hover_sound(self, new_cursor):
        if new_cursor != None and new_cursor != self.cursor:
            self.hover_sound.play()


    def highlight(self, new_cursor: int):
        self.cursor = new_cursor
        self.buttons[self.cursor].highlight(True)
        for i in range(len(self.buttons)):
            if i != self.cursor:
                self.buttons[i].highlight(False)

    def hover_highlight(self, mouse_pos):
        if self.mouse_last_pos != mouse_pos:
            self.mouse_control = True
            self.mouse_last_pos = mouse_pos
        if self.mouse_control:
            for button in self.buttons:
                if button.check_position(mouse_pos):
                    return self.buttons.index(button)

    def selection_highlight(self):
        keys = pygame.key.get_just_pressed()
        if keys[self.keybindings[UP]]:
            self.mouse_control = False
            return (self.cursor - 1)%len(self.buttons)
        elif keys[self.keybindings[DOWN]]:
            self.mouse_control = False
            return (self.cursor + 1)%len(self.buttons)

    def check_press(self, point) -> str:
        if self.is_visible:
            for i in range(len(self.buttons)):
                if self.buttons[i].check_position(point):
                    return self.press()
        return ""

    def press(self):
        if self.is_visible:
            self.confirm_sound.play()
            self.buttons[self.cursor].press()
            return self.buttons[self.cursor].action

    def display(self, visibility: bool):
        self.is_visible = visibility

    def render(self, surface: pygame.Surface):
        if self.is_visible:
            background = pygame.transform.box_blur(surface, 10)
            if self.logo != None:
                background.blit(self.logo, self.logo_position)
            for button in self.buttons:
                button.draw(background)
            surface.blit(background, (0,0))

    def update(self):
        if self.is_visible:
            self.check_highlight(pygame.mouse.get_pos())
            for button in self.buttons:
                button.update()

    def reset(self):
        self.cursor = 0
        self.mouse_last_pos = (0, 0)
        self.mouse_control = False

class InGameMenu(Menu):
    def __init__(self, keybindings: dict, button_names: list[str]):
        super().__init__(keybindings, button_names)
        self.pause_button = PauseButton((765, 40))

    def check_press(self, point) -> str:
        if self.pause_button.check_position(point):
            self.pause_button.press()
            return PAUSE
        return super().check_press(point)


    def render(self, surface: pygame.Surface):
        if self.is_visible:
            background = pygame.transform.box_blur(surface, 10)
            self.pause_button.draw(background)
            background.blit(self.logo, self.logo_position)
            for button in self.buttons:
                button.draw(background)
            surface.blit(background, (0,0))
        else:
            self.pause_button.draw(surface)

    def update(self):
        super().update()
        self.pause_button.update()

    def reset(self):
        super().reset()
        self.pause_button.reset()

class Button(pygame.sprite.Sprite):
    def __init__(self, position, text: str):
        super().__init__()
        font = pygame.font.Font("assets/fonts/Jersey15-Regular.ttf", 40)
        self.text = font.render(text, False, "White")
        self.action = text
        self.position = position
        self.images = [
            pygame.image.load(f"assets/graphics/standard_button/button{i}.png")
            for i in range(4)
        ]
        self.image = self.images[0].copy()
        self.rect = self.image.get_rect(center=self.position)
        self.frame_index = 0
        self.is_animating = False
        self.animation_direction = +1

    def check_position(self, point) -> bool:
        return self.rect.collidepoint(point)

    def highlight(self, to_highlight: bool):
        if not self.is_animating:
            if to_highlight:
                self.frame_index = 1
            else:
                self.frame_index = 0

    def press(self):
        self.is_animating = True

    def control_animation_status(self):
        if self.frame_index >= len(self.images):
            self.frame_index = len(self.images) -1
            self.animation_direction = -1
        if self.animation_direction == -1 and self.frame_index <= 0:
            self.frame_index = 1
            self.is_animating = False
            self.animation_direction = +1

    def update(self):
        if self.is_animating:
            self.frame_index += 0.4 * self.animation_direction
            self.control_animation_status()

    def draw(self, surface: pygame.Surface):
        self.image = self.images[int(self.frame_index)].copy()
        self.rect = self.image.get_rect(center=self.position)
        text_rect = self.text.get_rect(center=self.position)
        surface.blit(self.image, self.rect.topleft)
        surface.blit(self.text, text_rect.topleft)

class SettingButton(Button):
    def __init__(self, position, is_left=True):
        self.position = position
        if is_left:
            self.images = [
                pygame.image.load(f"assets/graphics/settings_button/settings_button{i}.png")
                for i in range(5)
            ]
        else:
            self.images = [
                pygame.transform.flip(
                    pygame.image.load(f"assets/graphics/settings_button/settings_button{i}.png"), True, False)
                for i in range(5)
            ]
        self.image = self.images[0].copy()
        self.rect = self.image.get_rect(topleft=position)
        self.frame_index = 0
        self.is_animating = False
        self.animation_direction = +1
        self.is_visible = False

    def draw(self, surface: pygame.Surface):
        self.image = self.images[int(self.frame_index)].copy()
        self.rect = self.image.get_rect(topleft=self.position)
        surface.blit(self.image, self.rect.topleft)


class PauseButton(Button):
    def __init__(self, position):
        self.position = position
        self.images = [
            pygame.image.load(f"assets/graphics/pause_button/pause{i}.png")
            for i in range(6)
        ]
        self.image = self.images[0].copy()
        self.rect = self.image.get_rect(center=position)
        self.frame_index = 0
        self.is_animating = False
        self.animation_direction = +1
        self.press_sound = pygame.mixer.Sound("assets/audio/pause_sound.mp3")

    def control_animation_status(self):
        if self.animation_direction == 1 and self.frame_index >= len(self.images):
            self.frame_index = len(self.images) -1
            self.animation_direction = -1
            self.is_animating = False
        if self.animation_direction == -1 and self.frame_index <= 0:
            self.frame_index = 0
            self.animation_direction = +1
            self.is_animating = False

    def press(self):
        super().press()
        self.press_sound.play()

    def draw(self, surface: pygame.Surface):
        self.image = self.images[int(self.frame_index)].copy()
        self.rect = self.image.get_rect(center=self.position)
        surface.blit(self.image, self.rect.topleft)

    def reset(self):
        self.frame_index = 0
        self.is_animating = False
        self.animation_direction = +1
