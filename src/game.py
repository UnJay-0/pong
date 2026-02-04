import pygame
from sys import exit
from src.entities.player import Player, PlayerNPC
from src.entities.ball import Ball, OUT_STATE
from src.settings import load_settings

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
                self.settings["field_dimensions"]))
        ]
        self.ball = pygame.sprite.GroupSingle(
            Ball(
                self.settings["field_dimensions"],
                [self.players[0].sprite,
                self.players[1].sprite])
        )

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.ball.sprite.reset()
                    for player in self.players:
                        player.sprite.reset()
                    self.game_active = True

    def update(self):
        self.players[0].update()
        self.players[1].update(self.ball.sprite.rect.center)
        self.ball.update()
        pygame.display.update()

    def render(self):
        self.screen.blit(self.field, (0, 100))
        self.players[0].draw(self.screen)
        self.players[1].draw(self.screen)
        self.ball.draw(self.screen)

    def run(self):
        while self.running:
            self.handle_events()
            if self.game_active:
                self.update()
                self.render()
                if self.ball.sprite.state == OUT_STATE:
                    self.game_active = False
            self.clock.tick(60)
