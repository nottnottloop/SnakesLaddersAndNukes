import socket
from threading import Thread
import pickle
import configparser

from src.shared.game import Game
import src.shared.debug as debug
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

games = {}
game_id = 0
total_id_count = 0
p = 0
game_found = False

def start_new_threaded_client(player_id, unique_game_id):
    conn.send(str.encode(str(player_id)))
    games[unique_game_id].new_player(player_id, id_count=total_id_count, debug=debug.debug)
    print(f"{addr[0]} is player {p} with ID {total_id_count} joining game {unique_game_id}")
    new_thread = Thread(target=threaded_client, args=(conn, p, unique_game_id, total_id_count, addr), daemon=True)
    new_thread.start()

def threaded_client(conn, p, local_game_id, id_count, addr):
    global total_id_count

    game = games[local_game_id]
    while True:
        try:
            data = conn.recv(4096).decode()

            if local_game_id in games:
                game = games[local_game_id]

                if not data:
                    break
                else:
                    if data == "roll":
                        game.roll_dice(p)
                    elif data == "NUKE":
                        game.player_uses_nuke(p)
                    elif data in ("Blue", "Green", "Yellow", "Red"):
                        game.set_color(p, data)
                    elif data == "Ready Up":
                        game.player_ready_up(p)
                    elif data == "debug":
                        game.activate_debug(p)
                    elif data in ("Up", "Down", "Left", "Right"):
                        game.debug_move(p, data)
                    elif data in ("-1", "1", "2", "3", "4", "5", "6"):
                        value = int(data)
                        game.move_player(p, value)
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
    game.player_lost_connection(p, id_count)
    print("Lost connection to", addr, ", player", p, "in game", game_id)
    close_game_if_empty(local_game_id)
    print("Closing thread")

def close_game_if_empty(game_id):
    global games
    if games[game_id].num_of_players == 0:
        print("Closing game", game_id)
        del games[game_id]

def start_new_game(game_id):
    games[game_id] = Game(game_id)
    print("Creating game ID", game_id)

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    total_id_count += 1

    if games:
        for id in games:
            if games[id].started:
                continue
            if not game_found and games[id].num_of_players < 4:
                for potential_player in range(1, 5):
                    if games[id].players[potential_player][5]:
                        p = potential_player
                        game_found = True
                        start_new_threaded_client(p, id)
                        break
            else:
                break
    if not game_found:
        p = 1
        start_new_game(game_id)
        start_new_threaded_client(p, game_id)
        game_id += 1
    game_found = False
