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
        self.ball.sprite.serve_positioning(self.players[self.serving].sprite.serve_position(self.ball.sprite.get_size()[1]))
        self.scoreboard = Scoreboard(BEST_OF_THREE)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.soft_reset()
                if event.key == pygame.K_SPACE and self.ball.sprite.state == HOLDING_STATE:
                    print(f"player serving: {self.players[self.serving].sprite}")
                    other_player = 1 - self.last_hit
                    self.players[other_player].sprite.can_move = True
                    self.ball.sprite.hit(
                        (2*self.ball.sprite.get_ball_vector()[0] * self.last_hit,
                            self.players[self.last_hit].sprite.get_vector()[1]))


    def update(self):
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
        self.ball.sprite.serve_positioning(self.players[self.serving].sprite.serve_position(self.ball.sprite.get_size()[1]))
        self.players[1-self.last_hit].sprite.can_move = True
        self.game_active = True

    def run(self):
        while self.running:
            self.handle_events()
            if self.game_active:
                self.update()
                self.render()
                for player in self.players:
                    self.ball.sprite.is_over_player(player.sprite)
                    if self.ball.sprite.state == PLAYING_STATE and self.ball.sprite.is_player_collision(player.sprite) and str(self.players[self.last_hit].sprite) != str(player.sprite):
                        self.players[self.last_hit].sprite.can_move = not self.players[self.last_hit].sprite.can_move
                        self.last_hit = (self.last_hit + 1) % 2
                        self.players[self.last_hit].sprite.can_move = not self.players[self.last_hit].sprite.can_move
                        self.ball.sprite.hit((2*self.ball.sprite.get_ball_vector()[0], player.sprite.get_vector()[1]))
                if self.ball.sprite.state == OUT_STATE:
                    self.scoreboard.update_score(self.last_hit)
                    self.players[self.last_hit].sprite.can_move = False
                    self.players[1-self.last_hit].sprite.can_move = False
                    print(self.scoreboard)
                    print(self.scoreboard.match_win_state())
                    self.game_active = False
            self.clock.tick(60)
