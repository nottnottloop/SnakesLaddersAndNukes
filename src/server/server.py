import socket
from threading import Thread
import pickle
import configparser

from ..shared.game import Game, Player
from ..shared.debug import DEBUG_FLAGS
from ..shared.constants import *
config = configparser.ConfigParser()

config.read('serverconfig.ini')
host = config['Server']['host']
port = int(config['Server']['port'])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((host, port))
except socket.error as e:
    str(e)
s.listen()

print(f"Hosting server on {host} on {port}")
print("Waiting for a connection, Server Started")

games: dict[int, Game] = {}
game_id_count = 0
player_id_count = 0

def start_new_threaded_client(player_id, game_id):
    games[game_id].add_new_player(player_id)
    print(f"{addr[0]} is player ID {player_id} joining game {game_id}")
    new_thread = Thread(target=threaded_client, args=(conn, addr, player_id, game_id), daemon=True)
    new_thread.start()

def threaded_client(conn, addr, player_id, game_id):
    # initial pickle for handshake
    game = games[game_id]
    conn.sendall(pickle.dumps(game))
    player: Player = game.players[player_id]
    while True:
        try:
            data = conn.recv(4096).decode()
            if not data:
                break

            if game_id in games:
                game = games[game_id]
                if data in (COLOR_MAP.keys()):
                    game.set_player_color(player, data)
                elif data == "Ready Up":
                    player.ready = True
                elif data == "roll":
                    game.roll_dice(player)
                elif data == "NUKE":
                    game.nuke(player)
                # Debug
                elif data == "debug":
                    game.activate_debug(player)
                elif data in ("Up", "Down", "Left", "Right"):
                    game.debug_move(player, data)
                elif data in ("-1", "1", "2", "3", "4", "5", "6"):
                    game.move_player(player, int(data))
                conn.sendall(pickle.dumps(game))
            else:
                break
        except:
            break
    game.player_lost_connection(player)
    print(f"Lost connection to {addr[0]}, player {player.player_id} in game {game_id}")
    if len(games[game_id].players) == 0:
        print("Closing game", game_id)
        del games[game_id]

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    game_found = False

    if games:
        for game_id, game in games.items():
            if game.started:
                continue
            if len(game.players) < 4:
                start_new_threaded_client(player_id_count, game_id)
                game_found = True

    if not game_found:
        games[game_id_count] = Game(game_id_count)
        print("Creating game ID", game_id_count)
        start_new_threaded_client(player_id_count, game_id_count)
        game_id_count += 1
    player_id_count += 1
