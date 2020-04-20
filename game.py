import pygame
import os
import numpy as np
import socket
import threading

from ship import Player, Enemy
from object import Fuel, Ammo, Object
from misc import out_of_bounds, rot_center, out_of_bg


class Game:

    @staticmethod
    def init():
        Game.WIDTH = 1200
        Game.HEIGHT = 800
        pygame.init()
        pygame.mixer.init()

        Game.crash = pygame.mixer.Sound(os.path.join("asset", "crash.wav"))
        Game.reload = pygame.mixer.Sound(os.path.join("asset", "reload.wav"))
        Game.fuel_sound = pygame.mixer.Sound(os.path.join("asset", "fill_fuel.wav"))

        pygame.mixer.music.load(os.path.join("asset", "music.wav"))
        pygame.mixer.music.queue(os.path.join("asset", "music.wav"))

        Game.BG = pygame.transform.scale(pygame.image.load(os.path.join("asset", "space.png")), (Game.WIDTH, Game.HEIGHT))

        class Background(Object):
            def __init__(self, width, height):
                super().__init__(0, 0)

            def get_img(self):
                return BG

        Game.bg = Background(Game.WIDTH, Game.HEIGHT)

        Game.WIN = pygame.display.set_mode((Game.WIDTH, Game.HEIGHT))
        Game.clock = pygame.time.Clock()
        pygame.display.set_caption("Space Invaders")

        Game.big_font = pygame.font.SysFont('comicsans', 70)
        Game.main_font = pygame.font.SysFont('comicsans', 50)
        Game.small_font = pygame.font.SysFont('comicsans', 30)
        Game.very_small_font = pygame.font.SysFont('comicsans', 20)

        Game.FPS = 60

        Game.rot_steer = 0.2
        Game.forward_steer = 0.1

    def __init__(self):
        self.players = [Player(Game.WIDTH // 2, Game.HEIGHT // 2, 1, 0, 1, 0)]

        self.fuels = [Fuel(0, 0).randomize(Game.WIDTH, Game.HEIGHT)]
        self.ammos = [Ammo(0, 0).randomize(Game.WIDTH, Game.HEIGHT)]

    # draw text and oil level on screen for the i_th player
    def draw_gui(self, i):
        # Draw text
        player = self.players[i]
        live_label = Game.main_font.render("lives :" + str(player.live), 1, (255, 255, 255))
        level_label = Game.main_font.render("points " + str(player.point), 1, (255, 255, 255))
        ammo_label = Game.main_font.render("ammo : " + str(player.nb_ammo), 1, (255, 255, 255))
        fps_label = Game.very_small_font.render(str(int(round(Game.clock.get_fps(), 0))) + " FPS", 1, (255, 255, 255))

        Game.WIN.blit(live_label, (10, 10))
        Game.WIN.blit(level_label, (Game.WIDTH - level_label.get_width() - 10, 10))
        Game.WIN.blit(ammo_label, (10, 20 + live_label.get_height()))

        Game.WIN.blit(fps_label, (1, 1))

        # Draw oil level
        oil_label = Game.small_font.render("oil level", 1, (255, 255, 255))
        Game.WIN.blit(oil_label, (Game.WIDTH - oil_label.get_width() - 10, 40 + level_label.get_height()))

        pygame.draw.rect(Game.WIN, (0, 255, 0), (Game.WIDTH - 50, 100, 20, 300), 2)
        # oil level goes from y=102 to y=298
        percentage = player.get_oil_percentage()
        if percentage:
            pygame.draw.rect(Game.WIN, (255, 0, 0), (Game.WIDTH - 50 + 2,
                                                     int((102 * percentage) + (400 * (1 - percentage))),
                                                     20 - 3,
                                                     int((298 * percentage))))

    def draw_objects(self):
        for fuel in self.fuels:
            fuel.draw(Game.WIN)
        for ammo in self.ammos:
            ammo.draw(Game.WIN)
        for player in self.players:
            player.draw(Game.WIN)

    def handle_collision(self):
        for player in self.players:
            for ammo in self.ammos:
                if player.collision(ammo):
                    Game.reload.play()
                    player.nb_ammo += ammo.quantity
                    ammo.randomize(Game.WIDTH, Game.HEIGHT)

            for fuel in self.fuels:
                if player.collision(fuel):
                    Game.fuel_sound.play(maxtime=300)
                    player.fill_oil()
                    fuel.randomize(Game.WIDTH, Game.HEIGHT)

            for i, laser in enumerate(player.laser):
                if out_of_bounds(Game.WIDTH, Game.HEIGHT, laser):
                    player.laser.pop(i)
                else:
                    for enemy in self.players:
                        if laser.collision(enemy):
                            Game.crash.play()
                            enemy.randomize(Game.WIDTH, Game.HEIGHT)
                            player.laser.pop(i)
                            break
                    laser.draw(Game.WIN)

    def next_state(self):
        Game.clock.tick(Game.FPS)
        for player in self.players:
            player.next_state()
            for laser in player.laser:
                laser.next_state()

    def draw(self, i):
        Game.clock.tick(Game.FPS)
        Game.bg.draw(Game.WIN)
        self.draw_objects()
        self.draw_gui(i)
        pygame.display.update()


BG = pygame.transform.scale(pygame.image.load(os.path.join("asset", "space.png")), (Game.WIDTH, Game.HEIGHT))

