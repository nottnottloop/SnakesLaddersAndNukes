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

games = {}
game_id_count = 0
player_id_count = 0

def start_new_threaded_client(player_id, game_id):
    p = games[game_id].new_player()
    print(f"{addr[0]} is player {p} joining game {game_id}")
    new_thread = Thread(target=threaded_client, args=(conn, addr, p, game_id), daemon=True)
    new_thread.start()

def threaded_client(conn, addr, p, game_id):
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
    game.player_lost_connection(p)
    print("Lost connection to", addr, ", player", p, "in game", game_id)
    close_game_if_empty(game_id)
    print("Closing thread")

def close_game_if_empty(game_id):
    global games
    if games[game_id].num_of_players == 0:
        print("Closing game", game_id)
        del games[game_id]

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    game_found = False

    if games:
        for game_id, game in games:
            if game.started:
                continue
            if game.num_of_players < 4:
                for potential_player in range(1, 5):
                    if game.players[potential_player][5]:
                        p = potential_player
                        game_found = True
                        start_new_threaded_client(p, game_id)
    if not game_found:
        games[game_id_count] = Game(game_id_count)
        print("Creating game ID", game_id_count)
        start_new_threaded_client(1, game_id_count)
        game_id_count += 1
