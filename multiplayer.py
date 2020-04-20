import pygame
import os
import numpy as np
import socket
import threading

from ship import Player, Enemy
from object import Fuel, Ammo
from misc import out_of_bounds, rot_center, out_of_bg
from socket_func import send, receive, handle_client, DISCONNECT
from game import Game

# ** SOCKET CONSTANTS **

HEADER = 5  # Length of the header msg containing the length of the next msg
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())  # local IP adress, to change if we are not server
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

# ** GAME CONSTANTS **
"""
WIDTH = 1200
HEIGHT = 800
pygame.init()
pygame.mixer.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
# WIN = pygame.display.set_mode((0,0), display = pygame.FULLSCREEN)

crash = pygame.mixer.Sound(os.path.join("asset", "crash.wav"))
reload = pygame.mixer.Sound(os.path.join("asset", "reload.wav"))
fuel_sound = pygame.mixer.Sound(os.path.join("asset", "fill_fuel.wav"))

pygame.mixer.music.load(os.path.join("asset", "music.wav"))
pygame.mixer.music.queue(os.path.join("asset", "music.wav"))

bg = Background(WIDTH, HEIGHT)

pygame.display.set_caption("Space Invaders")

pygame.quit()

"""

def main_game(level, lives):
    FPS = 60
    nb_enemies = 5 * level
    clock = pygame.time.Clock()
    big_font = pygame.font.SysFont('comicsans', 70)
    main_font = pygame.font.SysFont('comicsans', 50)
    small_font = pygame.font.SysFont('comicsans', 30)
    very_small_font = pygame.font.SysFont('comicsans', 20)
    run = True
    players = []

    fuel = Fuel(0, 0).randomize(WIDTH, HEIGHT)
    ammo = Ammo(0, 0).randomize(WIDTH, HEIGHT)
    rot_steer = 0.2
    forward_steer = 0.1

    # draw text and oil level on screen
    def draw_gui():

        # Draw text
        live_label = main_font.render("lives :" + str(lives), 1, (255, 255, 255))
        level_label = main_font.render("level " + str(level), 1, (255, 255, 255))
        ammo_label = main_font.render("ammo : " + str(player_ship.nb_ammo), 1, (255, 255, 255))
        enemy_label = main_font.render("enemy : " + str(len(aliens)), 1, (255, 255, 255))
        fps_label = very_small_font.render(str(int(round(clock.get_fps(), 0))) + " FPS", 1, (255, 255, 255))

        WIN.blit(live_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(ammo_label, (10, 20 + live_label.get_height()))
        WIN.blit(enemy_label, (10, 30 + ammo_label.get_height() + live_label.get_height()))

        WIN.blit(fps_label, (1, 1))

        # Draw oil level
        oil_label = small_font.render("oil level", 1, (255, 255, 255))
        WIN.blit(oil_label, (WIDTH - oil_label.get_width() - 10, 40 + level_label.get_height()))

        pygame.draw.rect(WIN, (0, 255, 0), (WIDTH - 50, 100, 20, 300), 2)
        # oil level goes from y=102 to y=298
        percentage = player_ship.get_oil_percentage()
        if percentage:
            pygame.draw.rect(WIN, (255, 0, 0), (WIDTH - 50 + 2,
                                                int((102 * percentage) + (400 * (1 - percentage))),
                                                20 - 3,
                                                int((298 * (percentage)))))

    # game loop
    while run and len(aliens) > 0:
        clock.tick(FPS)
        bg.draw(WIN)

        player_ship.turn_off()
        keys = pygame.key.get_pressed()

        if player_ship.oil_level != 0:
            engine_keys = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP,
                           pygame.K_a, pygame.K_d, pygame.K_w]
            if max([keys[k] for k in engine_keys]):
                player_ship.turn_on()

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player_ship.speed_angle += rot_steer
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player_ship.speed_angle -= rot_steer

            if keys[pygame.K_UP] or keys[pygame.K_w]:
                angle = np.radians(player_ship.angle + 90)
                player_ship.speed += np.array([np.cos(angle),
                                               np.sin(-angle)]) * forward_steer

        if keys[pygame.K_SPACE]:
            player_ship.shoot()

        if keys[pygame.K_RETURN]:
            run = False

        if keys[pygame.K_p]:
            pause_label = big_font.render("Pause - press P to unpause", 1, (255, 255, 255))
            WIN.blit(pause_label, (WIDTH // 2 - pause_label.get_width() // 2, HEIGHT // 2))
            pygame.display.update()
            pygame.time.wait(100)
            paused = True
            while paused:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        quit()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                        paused = False
                    if event.type == pygame.KEYDOWN:
                        print(event.key)
            pygame.time.wait(100)

        fuel.draw(WIN)

        if player_ship.collision(fuel):
            fuel_sound.play(maxtime=300)
            player_ship.fill_oil()
            fuel.randomize(WIDTH, HEIGHT)

        ammo.draw(WIN)

        if player_ship.collision(ammo):
            reload.play()
            player_ship.nb_ammo += ammo.quantity
            ammo.randomize(WIDTH, HEIGHT)

        for i, enemy in enumerate(aliens):
            enemy.next_state()
            if enemy.went_out(WIDTH, HEIGHT):
                enemy.randomize(WIDTH, HEIGHT, player_ship)

            enemy.draw(WIN)
            if player_ship.collision(enemy):
                crash.play()
                player_ship.health -= 20
                aliens.pop(i)
                enemy.randomize(WIDTH, HEIGHT, player_ship)

        if player_ship.health <= 0 or (not player_ship.collision(bg)):
            run = False

        for i, laser in enumerate(player_ship.laser):
            laser.next_state()
            if out_of_bounds(WIDTH, HEIGHT, laser):
                player_ship.laser.pop(i)
            else:
                for i2, enemy in enumerate(aliens):
                    if laser.collision(enemy):
                        crash.play()
                        aliens.pop(i2)
                        enemy.randomize(WIDTH, HEIGHT, player_ship)
                        player_ship.laser.pop(i)
                        break
                laser.draw(WIN)

        player_ship.next_state()
        player_ship.draw(WIN)

        draw_gui()

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

    if len(aliens) == 0 and player_ship.health > 0:
        return True
    return False


def main_menu():
    pygame.mixer.music.play(loops=1)

    level = 1
    lives = 5
    big_font = pygame.font.SysFont('comicsans', 70)
    play_label = big_font.render("Press SPACE to play", 1, (255, 255, 255))
    respawn_label = big_font.render("Press SPACE to respawn", 1, (255, 255, 255))
    continue_label = big_font.render("Press SPACE to level up", 1, (255, 255, 255))
    lost_label = big_font.render("You lost ! score: " + str(level), 1, (255, 255, 255))

    has_won = -1
    run = True
    while run:

        play_label = big_font.render("Press SPACE to play", 1, (255, 255, 255))
        respawn_label = big_font.render("Press SPACE to respawn", 1, (255, 255, 255))
        continue_label = big_font.render("Press SPACE to level up", 1, (255, 255, 255))
        lost_label = big_font.render("You lost ! score: " + str(level), 1, (255, 255, 255))

        if has_won == -1:
            WIN.blit(play_label, (WIDTH // 2 - play_label.get_width() // 2, HEIGHT // 2))
        elif has_won:
            WIN.blit(continue_label, (WIDTH // 2 - continue_label.get_width() // 2, HEIGHT // 2))
        else:
            WIN.blit(respawn_label, (WIDTH // 2 - respawn_label.get_width() // 2, HEIGHT // 2))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE]:
            pygame.time.wait(100)
            has_won = main_game(level, lives)
            if has_won:
                level += 1
            else:
                lives -= 1

        if lives == 0:
            bg.draw(WIN)
            WIN.blit(lost_label, (WIDTH // 2 - lost_label.get_width() // 2, HEIGHT // 2))
            pygame.display.update()
            pygame.time.wait(2000)
            quit()


def start():
    ans = input("Do you want to host (type 'h') or join (type 'j') a game ? >").lower()
    while ans not in ['h', 'j']:
        ans = input("Write h or j >").lower()

    is_server = (ans == 'h')

    if is_server:

        nb_player = input("How many player in the game ? >")
        while not nb_player.isdigit():
            nb_player = input("Type a valid number. >")
        nb_player = int(nb_player)
        start_server(nb_player)

    else:
        #We are the client
        SERVER = input("Which server do you want to join ? >")
        ADDR = (SERVER, PORT)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        connected = True
        Game.init()
        while connected:
            obj = receive(client)
            if obj == DISCONNECT:
                connected = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    connected = False

            if type(obj) == Game:
                pygame.event.get()
                obj.draw(0)
                pygame.display.flip()


def start_server(nb_players):
    print("Starting server...")
    Game.init()
    game = Game()
    print("Server adress is : " + str(SERVER))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)  # open the server
    compteur = 0
    server.listen()
    print("[LISTENING] Server is listening on " + str(SERVER))

    while compteur < nb_players:
        conn, addr = server.accept()
        compteur += 1
        thread = threading.Thread(target=handle_client, args=(conn, addr, game))
        thread.start()
        print("[ACTIVE CONNECTIONS] " + str(threading.activeCount()))

    print("starting game !")
    while True:
        game.next_state()


start()
