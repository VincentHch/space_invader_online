import pygame
import os
import numpy as np
import socket
import threading
import pickle

from ship import Player, Enemy
from object import Fuel, Ammo
from misc import out_of_bounds, rot_center, out_of_bg
from game import Game

HEADER = 32  # Length of the header msg containing the length of the next msg
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT = "disconnected"


def send(obj, client):
    message = pickle.dumps(obj)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)


def receive(conn):
    msg_length = conn.recv(HEADER).decode(FORMAT)  # Get the header
    if msg_length:
        msg_length = int(msg_length)
        msg = conn.recv(msg_length)  # Get the msg
        obj = pickle.loads(msg)
        return obj


def handle_client(conn, addr, game):
    print("[NEW CONNECTION] " + str(addr) + " connected.")
    index_player = threading.activeCount() - 1
    connected = True
    while connected:
        print(game.players[0].pos)
        send(game, conn)

    conn.close()
