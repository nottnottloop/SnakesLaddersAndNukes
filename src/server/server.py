import socket
from threading import Thread
import configparser

from .game_serializer import *
from ..shared.game import Game, Player
from ..shared.constants import *
config = configparser.ConfigParser()

config.read('serverconfig.ini')
host = config['Server']['host']
port = int(config['Server']['port'])

server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
server_socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)

try:
    server_socket.bind((host, port))
except socket.error as e:
    str(e)
server_socket.listen()

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
    # initial handshake
    game = games[game_id]
    conn.sendall(serialize_game(game))
    player: Player = game.players[player_id]
    while True:
        try:
            data = conn.recv(4096).decode()
            if not data:
                break

            if game_id in games:
                game = games[game_id]
                game.events = []
                if not game.winner:
                    if data in (TEXT_TO_ENUM_COLOR_MAP.keys()):
                        game.set_player_color(player, data)
                    elif data in ["Ready Up", "Play Single Player"]:
                        game.set_player_ready(player)
                    elif data == "cycle_game_mode":
                        game.cycle_game_mode()
                    elif data == "roll":
                        game.roll_dice(player)
                    elif data == "NUKE":
                        game.nuke(player)
                    elif data == "debug":
                        game.toggle_debug()
                    # Debug
                    if game.debug:
                        if data in ("Up", "Down", "Right", "Left"):
                            game.debug_move(player, data)
                        elif data == "generate_objects":
                            game.generate_objects()
                        elif data == "reset_deg":
                            game.reset_degredation()
                conn.sendall(serialize_game(game))
            else:
                break
        except:
            break
    game.player_lost_connection(player)
    print(f"Lost connection to {addr[0]}, player {player.player_id} in game {game_id}")
    if len(games[game_id].players) == 0:
        print(f"Closing game ID {game_id}")
        del games[game_id]

while True:
    conn, addr = server_socket.accept()
    print(f"Connected to:", addr[0])
    player_id_count += 1
    game_found = False
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
