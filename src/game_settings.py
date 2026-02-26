import pygame

from src.entities.scoreboard import BEST_OF_FIVE, BEST_OF_SEVEN, BEST_OF_THREE, Number
from src.entities.ui import Button, Menu, SettingButton
from src.utils.constants import DOWN, LEFT, RIGHT, UP

class GameSettings(Menu):
    """
    UI element that defines the settings for the following game.
    Makes the player set:
        - Number of players
        - Number of points per Set
        - Number of Matches
    """
    def __init__(self, keybindings: dict):
        """
        Initialise the GameSetting instance.

        Parameters
        ----------
        keybindings: dict
            controls that allows the menu navigation
        """
        self.logo = None
        self.background = pygame.image.load('assets/graphics/settings_bg.png')
        self.background_rect = self.background.get_rect(center=(400, 250))
        self.is_visible = False
        self.cursor = 0
        self.keybindings = keybindings
        self.mouse_last_pos = (0, 0)
        self.mouse_control = False
        self.hover_sound = pygame.mixer.Sound("assets/audio/hover_sound.mp3")
        self.confirm_sound = pygame.mixer.Sound("assets/audio/selection_sound.mp3")
        self.buttons = [
            Selection((self.background_rect.left, self.background_rect.top), "# players", [1, 2]),
            Selection((self.background_rect.left, self.background_rect.top+100), "Best of ", [BEST_OF_THREE, BEST_OF_FIVE, BEST_OF_SEVEN]),
            Selection((self.background_rect.left, self.background_rect.top+200), "Points per Set", [i for i in range(2,10)]),
            Button((self.background_rect.centerx, self.background_rect.bottom - 50), "Confirm")
        ]

    def selection_highlight(self):
        """
        Select the button to highlight based on the pressed
        button.

        Returns
        -------
        int - cursor of the highlighted button
        """
        keys = pygame.key.get_just_pressed()
        if keys[self.keybindings[UP]]:
            self.mouse_control = False
            return (self.cursor - 1)%len(self.buttons)
        elif keys[self.keybindings[DOWN]]:
            self.mouse_control = False
            return (self.cursor + 1)%len(self.buttons)
        elif keys[self.keybindings[LEFT]] and self.cursor < 3:
            self.mouse_control = False
            self.buttons[self.cursor].setting_buttons_index = 0
            return self.cursor
        elif keys[self.keybindings[RIGHT]] and self.cursor < 3:
            self.mouse_control = False
            self.buttons[self.cursor].setting_buttons_index = 1
            return self.cursor

    def get_settings(self):
        """
        Returns
        -------
        dict - settings selected by the user.
        """
        return {
            "players": self.buttons[0].get_value(),
            "best_of": self.buttons[1].get_value(),
            "set_points": self.buttons[2].get_value()
        }

    def render(self, surface: pygame.Surface):
        """
        Renders the menu for selecting the settings.
        """
        if self.is_visible:
            screen_background = pygame.transform.box_blur(surface, 10)
            screen_background.blit(self.background, self.background_rect)
            for button in self.buttons:
                button.draw(screen_background)
            surface.blit(screen_background, (0,0))

class Selection():
    """
    UI element that allows the user to select a
    number among a set of available options.
    """
    def __init__(self, reference_pos: tuple, text:str, options:list[int], digits=1):
        """
        Initialise the selection options.

        Parameters
        ----------
        reference_pos: tuple
            The position of the menu to use as a reference
        text: str
            Text to show on the selection option
        options: list[int]
            Set of available options
        digits: int
            Max number of digits of the options
        """
        font = pygame.font.Font("assets/fonts/Jersey15-Regular.ttf", 40)
        self.text = font.render(text, False, "White")
        self.text_rect = self.text.get_rect(topleft=(reference_pos[0]+40, reference_pos[1]+60))
        self.action = text
        self.setting_buttons = [SettingButton((reference_pos[0]+370, reference_pos[1]+60)),
            SettingButton((reference_pos[0]+470,reference_pos[1]+60), False)]
        self.setting_buttons_index = 0
        self.box = [pygame.image.load(f"assets/graphics/settings_number_box{i}.png")
            for i in range(2)]
        self.box_rect = self.box[0].get_rect(topleft=(reference_pos[0]+415, reference_pos[1]+60))
        self.box_frame_index = 0
        self.number = Number([(reference_pos[0]+402, reference_pos[1]+42)], digits, 0.9)
        self.option_index = 0
        self.number.set_number(options[self.option_index])
        self.options = options

    def check_position(self, point: tuple) -> bool:
        """
        Checks if the position specified by point collide with this
        selection entity.

        Parameters
        ----------
        point: tuple
            position to check

        Returns
        -------
        bool
            True if the point collide with the selection
            False otherwise
        """
        for i in range(len(self.setting_buttons)):
            if self.setting_buttons[i].rect.collidepoint(point):
                self.setting_buttons_index = i
                return True
            if self.box_rect.collidepoint(point):
                return True
        return False

    def get_value(self) -> int:
        """
        Get the value selected of this selection

        Returns
        -------
        int
            the value selected
        """
        return self.number.get_number()


    def highlight(self, to_highlight: bool):
        """
        Highlights or turns off the highlight from the selection object.

        Parameters
        ----------
        to_highlight: bool
            True if the selection has to be highlighted
            False otherwise
        """
        if to_highlight:
            self.box_frame_index = 1
            self.setting_buttons[self.setting_buttons_index].highlight(True)
            self.setting_buttons[1-self.setting_buttons_index].highlight(False)
        else:
           self.box_frame_index = 0
           for button in self.setting_buttons:
               button.highlight(False)

    def press(self):
        """
        Presses the selected button of the selection
        """
        self.setting_buttons[self.setting_buttons_index].press()
        self.option_index = ((self.option_index + (1 if self.setting_buttons_index else -1))
            % len(self.options))
        self.number.set_number(self.options[self.option_index])

    def update(self):
        """
        Updates the selection
        """
        for button in self.setting_buttons:
            button.update()

    def draw(self, surface: pygame.Surface):
        """
        Draws the selection on the given surface

        Parameters
        ----------
        surface: pygame.Surface
            surface to be drawn over
        """
        for button in self.setting_buttons:
            button.draw(surface)
        surface.blit(self.box[self.box_frame_index], self.box_rect)
        surface.blit(self.text, self.text_rect)
        self.number.render(surface)
