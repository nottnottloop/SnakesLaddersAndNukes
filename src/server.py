import socket
import threading
import pickle
import game
import debug
import configparser
import sys
config = configparser.ConfigParser()

config.read('serverconfig.ini')
server = config['Server']['ip']
port = int(config['Server']['port'])

# server = "::"
# port = 5555

# socket.setdefaulttimeout(1)
s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen()
print(f"Hosting server on {server} on {port}")
print("Waiting for a connection, Server Started")

# connected = set()
games = {}
game_id = 0
total_id_count = 0
p = 0
game_found = False

def threaded_client(conn, p, local_game_id, id_count, addr):
    global total_id_count

    reply = ""
    game = games[local_game_id]
    while True:
        try:
            data = conn.recv(8192).decode()

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
                        # conn.close()
                    # reply = game
                    conn.sendall(pickle.dumps(game))

                if game.winner != 0:
                    break
            else:
                break
        except:
            break
    # print("discon")
    game.player_lost_connection(p, id_count)
    print("Lost connection to", addr, ", player", p, "in game", game_id)
    close_game_if_empty(local_game_id)
    print("Closing thread")

def close_game_if_empty(game_id):
    global games
    if games[game_id].num_of_players == 0 and games[game_id].started:
        print("Closing game", game_id)
        del games[game_id]
    else:
        print("Not closing game")

def start_new_game(game_id):
    games[game_id] = game.Game(game_id)
    print("Creating game ID", game_id)

# def set_new_game_id(new_game_id):
#     global game_id
#     game_id = new_game_id

def start_new_threaded_client(p, unique_game_id):
    conn.send(str.encode(str(p)))
    games[unique_game_id].new_player(p, id_count=total_id_count, debug=debug.debug)
    print(addr[0], "is player", p, "with ID", total_id_count, "joining game", unique_game_id)
    new_thread = threading.Thread(target=threaded_client, args=(conn, p, unique_game_id, total_id_count, addr), daemon=True)
    new_thread.start()

# game_closer_daemon = threading.Thread(target=close_game_if_empty, daemon=True)
# game_closer_daemon.start()
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    total_id_count += 1

    # if game_id == None:
    #     game_id = 0
    #     start_new_game(game_id)

    if games:
        for id in games:
            if games[id].started:
                continue
            if not game_found:
                # if not games[id].started:
                #     if games[id].num_of_players < 4:
                if games[id].num_of_players < 4:
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
