import socket
from threading import Thread
import pickle
import configparser

from ..shared.game import Game
from ..shared.debug import debug_flags
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
    print(f"{addr[0]} is player {player_id} joining game {game_id}")
    print(addr)
    new_thread = Thread(target=threaded_client, args=(conn, addr, player_id, game_id), daemon=True)
    new_thread.start()

def threaded_client(conn, addr, player_id, game_id):
    # initial pickle for handshake
    game = games[game_id]
    conn.sendall(pickle.dumps(game))
    while True:
        try:
            data = conn.recv(4096).decode()

            if game_id in games:
                game = games[game_id]

                if not data:
                    break
                else:
                    if data == "roll":
                        game.roll_dice(player_id)
                    elif data == "NUKE":
                        game.player_uses_nuke(player_id)
                    elif data in ("Blue", "Green", "Yellow", "Red"):
                        game.set_player_color(player_id, data)
                    elif data == "Ready Up":
                        game.player_ready_up(player_id)
                    elif data == "debug":
                        game.activate_debug(player_id)
                    elif data in ("Up", "Down", "Left", "Right"):
                        game.debug_move(player_id, data)
                    elif data in ("-1", "1", "2", "3", "4", "5", "6"):
                        value = int(data)
                        game.move_player(player_id, value)
                    elif data == "ending":
                        conn.sendall(pickle.dumps(game))
                        break
                    conn.sendall(pickle.dumps(game))

                if game.winner != 0:
                    break
            else:
                break
        except:
            break
    game.player_lost_connection(player_id)
    print(f"Lost connection to {addr[0]}, player {player_id} in game {game_id}")
    if games[game_id].num_of_players == 0:
        print("Closing game", game_id)
        del games[game_id]
    print("Closing thread")

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    game_found = False

    if games:
        for game_id, game in games.items():
            if game.started:
                continue
            if len(game.players) < 4:
                game.add_new_player(player_id_count)
                start_new_threaded_client(player_id_count, game_id)
                game_found = True

    if not game_found:
        games[game_id_count] = Game(game_id_count)
        print("Creating game ID", game_id_count)
        start_new_threaded_client(player_id_count, game_id_count)
        game_id_count += 1
    player_id_count += 1
