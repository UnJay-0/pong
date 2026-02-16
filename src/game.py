import pygame
from sys import exit
from src.entities.player import Player, PlayerNPC
from src.entities.ball import PLAYING_STATE, Ball, OUT_STATE, HOLDING_STATE
from src.entities.scoreboard import Scoreboard, BEST_OF_THREE
from src.settings import load_settings
from random import randint

class Game:
    def __init__(self):
        pygame.display.set_caption('Pong')
        self.settings = load_settings()
        self.field = pygame.image.load('assets/graphics/field.png')
        self.screen = pygame.display.set_mode(self.settings["resolution"])
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_active = True
        self.players = [
            pygame.sprite.GroupSingle(Player(
                False,
                self.settings["keybindings"]["first_player"],
                self.settings["field_dimensions"])),
            pygame.sprite.GroupSingle(PlayerNPC(
                True,
                self.settings["field_dimensions"]))
        ]
        self.ball = pygame.sprite.GroupSingle(
            Ball(
                self.settings["field_dimensions"]),
        )
        self.last_hit = randint(0,1)
        self.serving = self.last_hit
        self.serving_movement(True)
        self.ball.sprite.serve_positioning(self.players[self.serving].sprite.serve_position(self.ball.sprite.get_size()[1]))
        self.scoreboard = Scoreboard(BEST_OF_THREE, self.settings["field_dimensions"])
        self.serving_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.serving_timer, 3000)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.soft_reset()
                if event.key == pygame.K_SPACE and self.ball.sprite.state == HOLDING_STATE:
                    self.serve()
                    self.serving_movement(False)
                    pygame.time.set_timer(self.serving_timer, 0)
            if event.type == self.serving_timer and self.ball.sprite.state == HOLDING_STATE:
                self.serve()
                self.serving_movement(False)
                pygame.time.set_timer(self.serving_timer, 0)

    def can_move(self):
        pass

    def serving_movement(self, is_serving: bool):
        if type(self.players[self.serving].sprite) == PlayerNPC:
            self.players[self.serving].sprite.serving(is_serving)

    def serve(self):
        other_player = 1 - self.last_hit
        self.players[other_player].sprite.can_move = True
        self.ball.sprite.hit(
            (2*self.ball.sprite.get_ball_vector()[0] * self.last_hit,
                self.players[self.last_hit].sprite.get_vector()[1]))
        self.scoreboard.increase_hit_counter()

    def update(self):
        if not self.scoreboard.is_animating():
            self.players[0].update()
            self.players[1].update(self.ball.sprite.rect.center)
            self.ball.update(self.players[self.last_hit].sprite.serve_position(self.ball.sprite.rect.w))
        self.scoreboard.update()
        pygame.display.update()

    def render(self):
        self.screen.blit(self.field, (0, 0))
        self.players[0].draw(self.screen)
        self.players[1].draw(self.screen)
        self.ball.draw(self.screen)
        self.scoreboard.draw(self.screen)

    def soft_reset(self):
        for player in self.players:
            player.sprite.reset()
        self.ball.sprite.reset()
        self.serving = (self.serving + 1)%2
        self.last_hit = self.serving
        print(f"player serving: {self.players[self.serving].sprite}")
        pygame.time.set_timer(self.serving_timer, 3000)
        self.serving_movement(True)
        self.ball.sprite.serve_positioning(self.players[self.serving].sprite.serve_position(self.ball.sprite.get_size()[1]))
        self.players[1-self.last_hit].sprite.can_move = True
        self.players[self.last_hit].sprite.can_move = False
        self.game_active = True
        self.scoreboard.hit_counter = 0

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            if self.game_active:
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
                    print(f"hit counter: {self.scoreboard.hit_counter}")
                    self.scoreboard.update_score(self.last_hit)
                    self.players[self.last_hit].sprite.can_move = False
                    self.players[1-self.last_hit].sprite.can_move = False
                    print(self.scoreboard)
                    print(self.scoreboard.match_win_state())
                    self.game_active = False
            else:
                if not self.scoreboard.is_animating():
                    if self.scoreboard.match_win_state() == -1:
                        self.soft_reset()
                    else:
                        # go to finished game menu
                        pass
            self.clock.tick(60)
