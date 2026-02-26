import pygame
from sys import exit
from src.entities.player import Player, PlayerNPC
from src.entities.ball import PLAYING_STATE, Ball, OUT_STATE, HOLDING_STATE
from src.entities.scoreboard import Scoreboard
import src.entities.ui as ui
from src.game_settings import GameSettings
from src.settings import load_settings
from random import randint
from src import game_status as status


class Game:
    def __init__(self):
        """
        Initializes the game
        """
        pygame.display.set_caption('Pong')
        self.settings = load_settings()
        self.field = pygame.image.load('assets/graphics/field.png')
        self.screen = pygame.display.set_mode(self.settings["resolution"])
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_status = status.START_MENU
        self.previous_status = status.PAUSED
        self.start_menu = ui.Menu(
            self.settings["keybindings"]["ui_movement"],
            [ui.START_GAME, ui.EXIT_GAME],
        )
        self.start_menu.display(True)
        self.in_game_menu = ui.InGameMenu(
            self.settings["keybindings"]["ui_movement"],
            [ui.RESTART_GAME, ui.EXIT_GAME]
        )
        self.game_settings = GameSettings(self.settings["keybindings"]["ui_movement"])
        self.current_menu = self.start_menu
        self.players = []

        self.ball = pygame.sprite.GroupSingle(
            Ball(
                self.settings["field_dimensions"]),
        )
        self.last_hit = randint(0,1)
        self.serving = self.last_hit
        self.serving_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.serving_timer, 0)

    def set_game_settings(self, settings: dict):
        """
        Set the settings for the game:
            - Number of players
            - Set points
            - Match wins

        Parameters
        ----------
        settings: dict
            contains the selected settings for the current game.
            It must contains the followings keys: players,
            best_of and set_points

        """
        self.players = [
            pygame.sprite.GroupSingle(Player(
                False,
                self.settings["keybindings"]["first_player"],
                self.settings["field_dimensions"]))
        ]
        if settings["players"] > 1:
            self.players.append(
                        pygame.sprite.GroupSingle(Player(
                            True,
                            self.settings["keybindings"]["second_player"],
                            self.settings["field_dimensions"])))
        else:
            self.players.append(
                        pygame.sprite.GroupSingle(PlayerNPC(
                            True,
                            self.settings["field_dimensions"]))
                    )
        self.serving_movement(True)
        self.ball.sprite.serve_positioning(self.players[self.serving].sprite.serve_position(self.ball.sprite.get_size()[1]))
        self.scoreboard = Scoreboard(settings["best_of"], settings["set_points"], self.settings["field_dimensions"])

    def handle_events(self):
        """
        Handles the pygames events, like:
            - quit
            - mouse clicks
            - keystrokes
            - timers
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.menu_actions(
                        self.current_menu.check_press(event.pos)
                    )
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.menu_actions(
                        self.current_menu.press()
                    )
                if (self.game_status != status.START_MENU):
                    if event.key == pygame.K_r:
                        self.soft_reset()
                        self.game_status = status.PLAYING
                    if event.key == pygame.K_SPACE and self.ball.sprite.state == HOLDING_STATE:
                        self.serve()
                        self.serving_movement(False)
                        pygame.time.set_timer(self.serving_timer, 0)
                    if event.key == pygame.K_p:
                        self.in_game_menu.pause_button.press()
                        self.menu_actions(ui.PAUSE)
            if event.type == self.serving_timer and self.ball.sprite.state == HOLDING_STATE:
                self.serve()
                self.serving_movement(False)
                pygame.time.set_timer(self.serving_timer, 0)

    def menu_actions(self, action: str):
        """
        Performs the requested menu action. The available actions are:
            - START_GAME
            - RESTART_GAME
            - GAME_SETTINGS
            - EXIT_GAME
            - PAUSE

        Parameters
        ----------
        action: str
            action to perform
        """
        match action:
            case ui.START_GAME:
                self.current_menu.display(False)
                self.current_menu = self.game_settings
                self.current_menu.display(True)
            case ui.RESTART_GAME:
                self.soft_reset()
                self.scoreboard.reset()
            case ui.GAME_SETTINGS:
                self.set_game_settings(self.game_settings.get_settings())
                self.game_status = status.PLAYING
                self.current_menu.display(False)
                self.current_menu = self.in_game_menu
                self.current_menu.display(False)
                pygame.time.set_timer(self.serving_timer, 3000)
            case ui.EXIT_GAME:
                if self.game_status == status.START_MENU:
                    pygame.quit()
                    exit()
                else:
                    self.soft_reset()
                    self.current_menu.reset()
                    self.current_menu.display(False)
                    self.current_menu = self.start_menu
                    self.current_menu.display(True)
                    self.game_status = status.START_MENU
                    self.scoreboard.reset()
                    pygame.time.set_timer(self.serving_timer, 0)
            case ui.PAUSE:
                if self.game_status != status.PAUSED:
                    self.in_game_menu.display(True)
                    self.previous_status = self.game_status
                    pygame.time.set_timer(self.serving_timer, 0)
                    self.game_status = status.PAUSED
                else:
                    self.in_game_menu.display(False)
                    pygame.time.set_timer(self.serving_timer, 3000)
                    self.game_status = self.previous_status

    def serving_movement(self, is_serving: bool):
        """
        Abilitate or disabilitate the serving player to move before serving.

        Parameters
        ----------
        is_serving: bool
            True if the serving player can move
            False otherwise
        """
        if type(self.players[self.serving].sprite) == PlayerNPC:
            self.players[self.serving].sprite.serving(is_serving)
        if type(self.players[1-self.serving].sprite) == PlayerNPC:
            self.players[1-self.serving].sprite.serving(False)

    def serve(self):
        """
        Makes the serve.
        """
        self.players[1 - self.last_hit].sprite.can_move = True
        self.ball.sprite.hit(
            (2*self.ball.sprite.get_ball_vector()[0] * self.last_hit,
                self.players[self.last_hit].sprite.get_vector()[1]))
        self.scoreboard.increase_hit_counter()

    def update(self):
        """
        Updates all the elements of the game
        """
        if self.game_status == status.PLAYING:
            self.players[0].update()
            self.players[1].update(self.ball.sprite.rect.center)
            self.ball.update(self.players[self.last_hit].sprite.serve_position(self.ball.sprite.rect.w))
        if self.game_status == status.UPDATING_SCORE:
            self.scoreboard.update()
        self.current_menu.update()
        pygame.display.update()

    def render(self):
        """
        Render the active elements of the games
        """
        self.screen.blit(self.field, (0, 0))
        if self.game_status != status.START_MENU:
            self.players[0].draw(self.screen)
            self.players[1].draw(self.screen)
            self.ball.draw(self.screen)
            self.scoreboard.draw(self.screen)
        self.current_menu.render(self.screen)

    def soft_reset(self):
        """
        Soft resets elements of the game.
        Specifically, the players and the ball.
        """
        for player in self.players:
            player.sprite.reset()
        self.ball.sprite.reset()
        self.serving = (self.serving + 1)%2
        self.last_hit = self.serving
        self.players[1-self.serving].sprite.can_move = True
        self.players[self.serving].sprite.can_move = False
        self.serving_movement(True)
        self.ball.sprite.serve_positioning(self.players[self.serving].sprite.serve_position(self.ball.sprite.get_size()[1]))

    def run(self):
        """
        Defines the game loop
        """
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            match self.game_status:
                case status.START_MENU:
                    pass
                case status.PLAYING:
                    for player in self.players:
                        self.ball.sprite.is_over_player(player.sprite)
                        if (self.ball.sprite.state == PLAYING_STATE and
                            self.ball.sprite.is_player_collision(player.sprite) and
                            str(self.players[self.last_hit].sprite) != str(player.sprite)):

                            self.players[self.last_hit].sprite.can_move = not self.players[self.last_hit].sprite.can_move
                            self.last_hit = (self.last_hit + 1) % 2
                            self.players[self.last_hit].sprite.can_move = not self.players[self.last_hit].sprite.can_move
                            self.ball.sprite.hit((2*self.ball.sprite.get_ball_vector()[0], player.sprite.get_vector()[1]))
                            self.scoreboard.increase_hit_counter()
                    if self.ball.sprite.state == OUT_STATE:
                        self.scoreboard.update_score(self.last_hit)
                        self.game_status = status.UPDATING_SCORE
                        self.players[self.last_hit].sprite.can_move = False
                        self.players[1-self.last_hit].sprite.can_move = False
                case status.UPDATING_SCORE:
                    if not self.scoreboard.is_animating():
                        if self.scoreboard.match_win_state() == -1:
                            self.soft_reset()
                            pygame.time.set_timer(self.serving_timer, 3000)
                            self.game_status = status.PLAYING
                        else:
                            self.in_game_menu.pause_button.press()
                            self.menu_actions(ui.PAUSE)
                            self.game_status = status.END_GAME
                case status.PAUSED:
                    pass
                case status.END_GAME:
                    pass
            self.clock.tick(60)
