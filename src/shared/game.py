import random
from ..shared.debug import DEBUG_FLAGS
from ..shared.constants import *

class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.position: Position = (0, 0)
        self.color: Color | None = None
        self.nukes = 0
        self.ready = False
        self.debug = False
    
class Movable:
    def __init__(self, position, vector, sprite):
        self.position: Position = position
        self.vector: Position = vector
        self.sprite: str = sprite

class Nuke:
    def __init__(self, position):
        self.position: Position = position

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

    def __init__(self, game_id):
        self.game_id = game_id
        self.started = False
        
        self.players: dict[int, Player] = {}
        self.player_to_move: Player = None
        self.winner: Player = None
        self.dice_pips = random.randint(1, 6)
        self.players_previous_space = []
        self.player_travelled_on_movable = []

        self.nuke_used = False
        self.board = 0
        self.discoloration = 0
        self.pieces_degraded = 0
        self.dice_degraded = 0
        self.degraded_nuke_text = 0
        self.snakes_and_ladders_degraded = 0
        self.piece_shake = 0

        self.min_num_of_nukes = 5
        self.max_num_of_nukes = 15

        # self.min_num_of_nukes = 98
        # self.max_num_of_nukes = 98

        self.movables: list[Movable] = []
        self.nukes = []
        self.generate_objects()
        # self.debug = False

    @property
    def taken_colors(self) -> set[str]:
        return {player.color.text for player in self.players.values() if player.color is not None}

    @property
    def players_are_ready(self) -> set[str]:
        return all(player.ready for player in self.players.values())

    # Lobby screen
    def add_new_player(self, player_id):
        self.players[player_id] = Player(player_id)

    def set_player_color(self, player, color):
        player.color = COLOR_MAP[color]

    def player_lost_connection(self, player):
        del self.players[player.player_id]
        if self.started and len(self.players) == 1 and not self.winner:
            self.winner = self.player_to_move

    # Gameplay
    def calculate_destination_position(self, start_pos: Position, vector: Position) -> Position:
        return Position(start_pos.x + vector.x, start_pos.y + vector.y)

    def generate_objects(self):
        movables_to_place = [
            Movable(None, (-1, -1), "snake1"),
            Movable(None, (-2, -2), "snake2"),
            Movable(None, (0, -6), "snake3"),
            Movable(None, (3, -5), "snake4"),
            Movable(None, (3, 3), "ladder1"),
            Movable(None, (0, 2), "ladder2"),
            Movable(None, (-1, 2), "ladder3"),
            Movable(None, (0, 5), "ladder4"),
        ]
        random.shuffle(movables_to_place)

        for movable in movables_to_place:
            while True:
                possible_position = Position(random.randint(0, 9), random.randint(0, 9))
                destination_pos = self.calculate_destination_position(possible_position, movable.vector)
                if destination_pos.x < 0 or destination_pos.x > 9 or destination_pos.y < 0 or destination_pos.y > 9:
                    continue
                for existing in self.movables:
                    existing_destination_pos = self.calculate_destination_position(existing.position, existing.vector)
                    if (
                        possible_position == existing.position or
                        possible_position == existing_destination_pos or
                        destination_pos == existing.position or
                        destination_pos == existing_destination_pos
                    ):
                        break
                else:
                    movable.position = possible_position
                    self.movables.append(movable)

        for _ in range(random.randint(self.min_num_of_nukes, self.max_num_of_nukes)):
            while True:
                possible_position = Position(random.randint(0, 9), random.randint(0, 9))
                if possible_position == (0, 0) or possible_position == (0, 9) or possible_position in self.nukes:
                    continue
                self.nukes.append(possible_position)

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
        if self.player_to_move == p or DEBUG_FLAGS.get("disable_move_turns"):
            checking_for_win = False
            initial_x, initial_y = self.players[p][0][0], self.players[p][0][1]
            if self.players[p][0][1] == 9 and self.players[p][0][0] <= 6:
                checking_for_win = True
            if checking_for_win:
                # spaces to win is equal to self.players[p][0][0]
                gone_over_amount = self.players[p][0][0] - amount
                if gone_over_amount == 0:
                    self.winner = player_id
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
            if moving_backwards:
                self.players[p][0][0] -= amount
            else:
                self.players[p][0][0] += amount
            self.check_collision(p, nukes = True)
            if not DEBUG_FLAGS.get("disable_snakes_and_ladders"):
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
        self.move_player(p, self.dice_pips)

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

    # this function originally sent everyone but the nuking player back to the start
    def player_uses_nuke(self, p):
        self.players[p][2] -= 1
        if not DEBUG_FLAGS.get("disable_nuke_movement"):
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
        if DEBUG_FLAGS.get("let_there_be_nukes"):
            self.players[p][2] = 100
        if DEBUG_FLAGS.get("i_just_want_to_win"):
            self.players[p][0] = [1, 9]
