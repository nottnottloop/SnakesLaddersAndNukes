import random
import debug
from _thread import *

class Game:
    board = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
             20, 19, 18, 17, 16, 15, 14, 13, 12, 11,
             21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
             40, 39, 38, 37, 36, 35, 34, 33, 32, 31,
             41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
             60, 59, 58, 57, 56, 55, 54, 53, 52, 51,
             61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
             80, 79, 78, 77, 76, 75, 74, 73, 72, 71,
             81, 82, 83, 84, 85, 86, 87, 88, 89, 90,
             100, 99, 98, 97, 96, 95, 94, 93, 92, 91]

    coord_board = [[0 for r in range(10)] for c in range(10)]
    for r in range(10):
        for c in range(10):
            if r % 2 == 0:
                coord_board[c][r] = 1 + c + (r * 10)
            else:
                coord_board[c][r] = 1 + (9 - c) + (r * 10)

    def __init__(self, id):
        self.player_to_move = 1
        self.dice_pips = random.randint(1, 6)
        self.num_of_players = 0
        self.ready_count = 0
        self.players = [None]

        self.players_previous_space = [None]
        self.player_travelled_on_movable = [None]

        self.blocked_colors = []
        self.id = id
        self.player_ids_connected = []

        self.winner = 0
        self.winner_set = False
        self.game_ended = False

        self.time_to_move = 120
        self.nuke_used = False

        self.board = 0
        self.discoloration = 0
        self.pieces_degraded = 0
        self.dice_degraded = 0
        self.degraded_nuke_text = 0
        self.snakes_and_ladders_degraded = 0
        self.piece_shake = 0

        self.nukes_acquired = [None, 0, 0, 0, 0]
        self.snakes_gone_down = 0
        self.ladders_gone_up = 0
        self.num_nukes_used = 0

        self.min_num_of_nukes = 5
        self.max_num_of_nukes = 15

        # self.min_num_of_nukes = 98
        # self.max_num_of_nukes = 98

        # 0: position, 1: color, 2: num of nukes, 3: ready or not, 4: debug mode, 5: new player
        self.INITAL_PLAYER_STARTING_STATE = [[-10, 20], None, 0, False, False, True]
        for i in range(4):
            self.players.append(self.INITAL_PLAYER_STARTING_STATE)
        for i in range(4):
            self.players_previous_space.append([0, 0])
        for i in range(4):
            self.player_travelled_on_movable.append(False)
        self.started = False
        self.nukes = []
        if not debug.disable_snakes_and_ladders:
            self.snakes = []
            self.ladders = []
            self.generate_objects()
            # self.debug_mode_activated = False

    def convert_position_to_board(self, position):
        return self.board[position]

    def convert_board_to_position(self, board_num):
        return self.board.index(board_num)

    def convert_position_to_coords(self, position):
        x = position % 10
        y = position // 10
        return x, y

    def convert_coords_to_position(self, x, y):
        return y * 10 + x

    def generate_movement_amount(self, position, x_offset, y_offset):
        start_x, start_y = self.convert_position_to_coords(position)
        end_x, end_y = start_x + x_offset, start_y + y_offset
        return self.convert_coords_to_position(end_x, end_y)

    def generate_objects(self):

        def check_for_duplicate_positions(pos_x, pos_y, vector = None, is_nuke = False):
            if not is_nuke:
                test_list = []
                test_list.extend(self.snakes) ; test_list.extend(self.ladders)
                for i in range(len(test_list)):
                    # the position of an object cannot equal the position of another object
                    if tuple(test_list[i][0]) == (pos_x, pos_y):
                        return True
                    # the destination of an object cannot equal the destination of another object
                    if tuple(self.calculate_destination_position((pos_x, pos_y), vector)) == \
                            tuple(self.calculate_destination_position((test_list[i][0]), test_list[i][1])):
                        return True
                    # the position of an object cannot equal the destination of another object
                    if (pos_x, pos_y) == tuple(self.calculate_destination_position((test_list[i][0]), test_list[i][1])):
                        return True
                    # the destination of an object cannot equal the position of another object
                    if tuple(self.calculate_destination_position((pos_x, pos_y), vector)) == tuple(test_list[i][0]):
                        return True
            else:
                for i in range(len(self.nukes)):
                    if self.nukes[i] == (pos_x, pos_y):
                        return True
            return False
            # for i in range(len(self.ladders)):
            #     if tuple(self.ladders[i][0]) == (pos_x, pos_y) \
            #     or (pos_x, pos_y) == tuple(self.calculate_destination_position((self.ladders[i][0]), vector)):
            #         return True

        # def check_for_unconventionality(position):
            # if (position // 10) % 2 == 0:
            #     return False
            # return True
            # pass

        # def calculate_movement_amount(position, offset):
        #     tail_position = position

        self.snakes = [[[0, 0], (-1, -1)], [[0, 0], (-2, -2)], [[0, 0], (0, -6)], [[0, 0], (3, -5)]]
        self.ladders = [[[0, 0], (3, 3)], [[0, 0], (0, 2)], [[0, 0], (-1, 2)], [[0, 0], (0, 5)]]
        # snake_movement_amounts_to_append = ((-1, -1), (-2, -2), (0, -6), (3, -5))
        # ladder_movement_amounts_to_append = ((3, 3), (0, 2), (-1, 2), (0, 5))
        for snake in range(4):
            snake_added = False
            while not snake_added:
                snake_pos_x, snake_pos_y = random.randint(0, 9), random.randint(0, 9)
                if (snake_pos_x, snake_pos_y) == (0, 9):
                    continue
                if snake == 0 and snake_pos_x == 0 or snake_pos_y == 0:
                    continue
                elif snake == 1 and snake_pos_x < 2 or snake_pos_y < 2:
                    continue
                elif snake == 2 and snake_pos_y < 6:
                    continue
                elif snake == 3 and snake_pos_x > 6 or snake_pos_y < 5:
                    continue

                if check_for_duplicate_positions(snake_pos_x, snake_pos_y, self.snakes[snake][1]):
                    continue

                self.snakes[snake] = [[snake_pos_x, snake_pos_y], self.snakes[snake][1]]
                # self.snakes.append(((snake_pos_x, snake_pos_y), snake_movement_amounts_to_append[snake]))
                snake_added = True
        for ladder in range(4):
            ladder_added = False
            while not ladder_added:
                ladder_pos_x, ladder_pos_y = random.randint(0, 9), random.randint(0, 9)
                if self.calculate_destination_position((ladder_pos_x, ladder_pos_y), self.ladders[ladder][1]) == (0, 9):
                    continue
                if ladder == 0 and ladder_pos_x > 6 or ladder_pos_y > 6:
                    continue
                elif ladder == 1 and ladder_pos_y > 7:
                    continue
                elif ladder == 2 and ladder_pos_x == 0 or ladder_pos_y > 7:
                    continue
                elif ladder == 3 and ladder_pos_y > 4:
                    continue

                if check_for_duplicate_positions(ladder_pos_x, ladder_pos_y, self.ladders[ladder][1]):
                    continue

                self.ladders[ladder] = [[ladder_pos_x, ladder_pos_y], self.ladders[ladder][1]]
                # self.ladders.append(((ladder_pos_x, ladder_pos_y), ladder_movement_amounts_to_append[ladder]))
                ladder_added = True

        for nuke in range(random.randint(self.min_num_of_nukes, self.max_num_of_nukes)):
            nuke_added = False
            while not nuke_added:
                nuke_pos_x, nuke_pos_y = random.randint(0, 9), random.randint(0, 9)
                if (nuke_pos_x, nuke_pos_y) == (0, 0) or (nuke_pos_x, nuke_pos_y) == (0, 9):
                    continue
                if check_for_duplicate_positions(nuke_pos_x, nuke_pos_y, is_nuke = True) and self.nukes:
                    continue
                self.nukes.append((nuke_pos_x, nuke_pos_y))
                nuke_added = True

    def debug_move(self, p, direction):
        if direction == "Up":
            self.players[p][0][1] += 1
        if direction == "Down":
            self.players[p][0][1] -= 1
        if direction == "Left":
            self.players[p][0][0] -= 1
        if direction == "Right":
            self.players[p][0][0] += 1

    def move_player(self, p, amount):
        self.nuke_used = False
        if self.player_to_move == p or debug.disable_move_turns:
            checking_for_win = False
            initial_x, initial_y = self.players[p][0][0], self.players[p][0][1]
            if self.players[p][0][1] == 9 and self.players[p][0][0] <= 6:
                checking_for_win = True
            if checking_for_win:
                # spaces to win is equal to self.players[p][0][0]
                gone_over_amount = self.players[p][0][0] - amount
                if gone_over_amount == 0:
                    self.player_win(p)
                elif gone_over_amount < 0:
                    self.players[p][0][0] -= gone_over_amount * 2

            if self.players[p][0][1] % 2 == 1:
                moving_backwards = True
            else:
                moving_backwards = False
            if self.players[p][0][0] + amount > 9 and not moving_backwards or self.players[p][0][0] - amount < 0 and moving_backwards:
                self.players[p][0][1] += 1
                if moving_backwards == False:
                    amount -= 1 + (9 - self.players[p][0][0])
                else:
                    amount -= 1 + self.players[p][0][0]
                moving_backwards = not moving_backwards
                if moving_backwards:
                    self.players[p][0][0] = 9
                else:
                    self.players[p][0][0] = 0
                # amount -= 9 - initial_x
            if moving_backwards:
                self.players[p][0][0] -= amount
            else:
                self.players[p][0][0] += amount
            self.check_collision(p, nukes = True)
            if not debug.disable_snakes_and_ladders:
                self.check_collision(p)
            self.next_player_to_move()

    def next_player_to_move(self):
        next_player_to_move_found = False
        while not next_player_to_move_found:
            self.player_to_move += 1
            if self.player_to_move > 4:
                self.player_to_move = 1
            if self.players[self.player_to_move][0] == [-10, 20]:
                continue
            next_player_to_move_found = True

    def roll_dice(self, p = None):
        self.dice_pips = random.randint(1,6)
        # if p != None:
        #     pre_move_position = self.players[p][0]
        #     if pre_move_position + self.dice_pips > 98:
        #         if self.players[p][0] == 99:
        #             self.player_win(p)
        #         else:
        #             spaces_to_win = 99 - pre_move_position
        #             spaces_to_move_back = self.dice_pips - spaces_to_win
        #             self.players[p][0] = pre_move_position + spaces_to_win - spaces_to_move_back
        #             self.check_collision(p)
        #     else:
        self.move_player(p, self.dice_pips)
        # self.players[p][0][0] += self.dice_pips

    def calculate_destination_position(self, start_pos, vector):
        start_x, start_y = start_pos[0], start_pos[1]
        vector_x, vector_y = vector[0], vector[1]
        end_x = start_x + vector_x
        end_y = start_y + vector_y
        return end_x, end_y

    def player_collide(self, p, vector):
        player_x, player_y = self.calculate_destination_position(self.players[p][0], vector)
        self.players[p][0] = [player_x, player_y]
        self.check_collision(p, nukes=True)

    def check_collision(self, p, nukes = False):
        self.player_travelled_on_movable[p] = False
        if not nukes:
            for snake in range(len(self.snakes)):
                if self.players[p][0] == self.snakes[snake][0]:
                    self.players_previous_space[p] = self.snakes[snake][0]
                    self.snakes_gone_down += 1
                    self.player_collide(p, self.snakes[snake][1])
                    self.player_travelled_on_movable[p] = True
                    break
            for ladder in range(len(self.ladders)):
                if self.players[p][0] == self.ladders[ladder][0]:
                    self.players_previous_space[p] = self.ladders[ladder][0]
                    self.ladders_gone_up += 1
                    self.player_collide(p, self.ladders[ladder][1])
                    self.player_travelled_on_movable[p] = True
                    break
        else:
            for nuke in range(len(self.nukes)):
                if tuple(self.players[p][0]) == self.nukes[nuke]:
                    self.nukes_acquired[p] += 1
                    self.player_collect_nuke(p, nuke)
                    break

    def player_collect_nuke(self, p, nuke_index):
        self.players[p][2] += 1
        self.nukes[nuke_index] = [-100, -100]
        # del self.nukes[nuke_index]

    # for i in range(2):
       #     for j in range(4):
       #         if i == 0:
       #             if self.players[p][0] == self.snakes[j][0]:
       #                 self.player_collide(p, self.snakes[j][1], i)
       #         else:
       #             if self.players[p][0] == self.ladders[j][0]:
       #                 self.player_collide(p, self.ladders[j][1], i)

    def player_win(self, p):
        self.winner = p
        self.winner_set = True

        #old code version
        # genuine_win = False
        # for player in range(1, 5):
        #     if self.players[player][0] == [0, 9]:
        #         self.winner = p
        #         genuine_win = True
        #         self.winner_set = True
        # if not genuine_win:
        #     self.winner = self.player_to_move


    # this function originally sent everyone but the nuking player back to the start
    def player_uses_nuke(self, p):
        self.players[p][2] -= 1
        if not debug.disable_nuke_movement:
            for player in range(1, 5):
                if not self.players[player][5]:
                    self.players[player][0] = [random.randint(0, 9), random.randint(0, 8)]
                    self.check_collision(player)
                    self.check_collision(player, nukes = True)
        self.nuke_used = True
        self.num_nukes_used += 1
        self.degrade_game()

    def degrade_game(self):
        degrade_tokens = 1
        if random.randint(1, 4) == 1:
            degrade_tokens += 1
        while degrade_tokens > 0:
            degrade_num = random.randint(1, 5)
            if self.board == 4 and self.discoloration == 5 and self.pieces_degraded == 1 and self.dice_degraded == 1 and self.degraded_nuke_text == 1:
                if self.snakes_and_ladders_degraded == 0:
                    self.snakes_and_ladders_degraded = 1
                    degrade_tokens -= 1
                elif self.piece_shake == 0:
                    self.piece_shake = 1
                    degrade_tokens -= 1
                else:
                    degrade_tokens = 0
            if degrade_num == 1:
                if self.board == 4:
                    continue
                else:
                    self.board += 1
                    degrade_tokens -= 1
            if degrade_num == 2:
                if self.discoloration == 5:
                    continue
                else:
                    self.discoloration += 1
                    degrade_tokens -= 1
            if degrade_num == 3:
                if self.pieces_degraded == 1:
                    continue
                else:
                    self.pieces_degraded += 1
                    degrade_tokens -= 1
            if degrade_num == 4:
                if self.dice_degraded == 1:
                    continue
                else:
                    self.dice_degraded += 1
                    degrade_tokens -= 1
            if degrade_num == 5:
                if self.degraded_nuke_text == 1:
                    continue
                else:
                    self.degraded_nuke_text += 1
                    degrade_tokens -= 1
        # self.nuke_used = False

    def set_color(self, p, color):
        self.players[p][1] = color
        self.blocked_colors.append(color)

    def new_player(self, p, id_count = None, debug = False):
        # 0: position. 1: color. 2: num of nukes. 3: ready to play or not. 4: debug on
        self.num_of_players += 1
        self.players[p] = [[0, 0], None, 0, False, debug, False]
        self.debug_give_stuff(p)
        self.player_ids_connected.append(id_count)
        if debug:
            self.activate_debug(p)

    def player_lost_connection(self, p, id_count):
        if self.players[p][1] != None:
            self.blocked_colors.remove(self.players[p][1])
        self.num_of_players -= 1
        if self.players[p][3]:
            self.ready_count -= 1
        if not self.started:
            self.players[p] = self.INITAL_PLAYER_STARTING_STATE
        else:
            self.players[p][0] = [-10, 20]
            self.players[p][5] = True
        if self.num_of_players > 0:
            if self.player_to_move == p:
                self.next_player_to_move()
        del self.player_ids_connected[self.player_ids_connected.index(id_count)]
        if self.started and self.num_of_players == 1 and not self.winner_set:
            self.player_win(self.player_to_move)

    def player_ready_up(self, p):
        self.players[p][3] = True
        if self.players[p][1] != None and self.players[p][3] == True:
            self.ready_count += 1
        if self.ready_count == self.num_of_players:
            self.started = True

    def activate_debug(self, p):
        debug_color = ""
        if p == 1:
            debug_color = "Red"
        if p == 2:
            debug_color = "Green"
        if p == 3:
            debug_color = "Blue"
        if p == 4:
            debug_color = "Yellow"
        self.set_color(p, debug_color)
        self.player_ready_up(p)

    def debug_give_stuff(self, p):
        if debug.let_there_be_nukes:
            self.players[p][2] = 100
        if debug.i_just_want_to_win:
            self.players[p][0] = [1, 9]

    # def move_player(self, p, amount):
    #     self.players[p][0] += amount
    #     self.check_collision(p)

    #def board_generate(self):
        # generates 1-100 snakes and ladder board with flipping
        # shame that this is infinitesimally slower than a hardcoded board. still needed this to make the list in the first place though lol
        # board = []
        # buffer = []
        # flip = False
        #
        # for row in range(10):
        #     for i in range(10):
        #         buffer.append(i + (row * 10) + 1)
        #     if flip:
        #         buffer.reverse()
        #     print(buffer)
        #     board += buffer
        #     buffer.clear()
        #     flip = not flip
        # return board
# game = Game(1)
# print(sys.getsizeof(game.board))
