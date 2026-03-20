import random
from itertools import cycle

from ..shared.debug import DEBUG_FLAGS
from ..shared.constants import *


class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.position: Position = Position(0, 0)
        self.color: Color | None = None
        self.nukes = 999
        self.ready = False
        self.debug = False
    
    @property
    def board_number(self):
        return POSITION_TO_BOARD_NUMBER[self.position]
    
class Movable:
    def __init__(self, position, vector, sprite):
        self.position: Position = position
        self.vector: Position = vector
        self.sprite: str = sprite

class Nuke:
    def __init__(self, position):
        self.position: Position = position

class Game:
    def __init__(self, game_id):
        self.game_id: int = game_id
        self.started = False
        
        self.players: dict[int, Player] = {}
        self.player_to_move: Player = None
        self.player_cycle: cycle = None
        self.winner: Player = None
        self.dice_pips = random.randint(1, 6)

        self.nuke_used_this_game = False
        self.min_num_of_nukes = 5
        self.max_num_of_nukes = 15
        # self.min_num_of_nukes = 98
        # self.max_num_of_nukes = 98

        self.movables: list[Movable] = []
        self.nukes: list[Position] = []
        self.generate_objects()

        self.deg_board = 0
        self.deg_color = 0
        self.deg_pieces = 0
        self.deg_dice = 0
        self.deg_nuke_text = 0
        self.deg_snakes_and_ladders = 0
        self.deg_piece_shake = 0
        self.deg_music = 0

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

    def set_player_color(self, player: Player, color: str):
        player.color = COLOR_MAP[color]

    def set_player_ready(self, player: Player):
        player.ready = True
        if self.players_are_ready:
            self.player_cycle = cycle(self.players.values())
            self.player_to_move = next(self.player_cycle)
            self.started = True

    def player_lost_connection(self, player: Player):
        del self.players[player.player_id]

    # Gameplay
    def calculate_destination_position(self, start_pos: Position, vector: Position) -> Position:
        return Position(start_pos.x + vector.x, start_pos.y + vector.y)

    def generate_objects(self):
        movables_to_place = [
            Movable(None, Position(-1, -1), "snake1"),
            Movable(None, Position(-2, -2), "snake2"),
            Movable(None, Position(0, -6), "snake3"),
            Movable(None, Position(3, -5), "snake4"),
            Movable(None, Position(3, 3), "ladder1"),
            Movable(None, Position(0, 2), "ladder2"),
            Movable(None, Position(-1, 2), "ladder3"),
            Movable(None, Position(0, 5), "ladder4"),
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
                    break

        for _ in range(random.randint(self.min_num_of_nukes, self.max_num_of_nukes)):
            while True:
                possible_position = Position(random.randint(0, 9), random.randint(0, 9))
                if possible_position == (0, 0) or possible_position == (0, 9) or possible_position in self.nukes:
                    continue
                self.nukes.append(possible_position)
                break
    
    def potentially_collect_nuke(self, player:Player):
        for i, nuke_position in enumerate(self.nukes):
            if player.position == nuke_position:
                player.nukes += 1
                del self.nukes[i]

    def check_player_iteraction(self, player: Player):
        self.potentially_collect_nuke(player)
        for movable in self.movables:
            if player.position == movable.position:
                player.position = self.calculate_destination_position(player.position, movable.vector)
        self.potentially_collect_nuke(player)

    def roll_dice(self, player: Player):
        if not self.player_to_move == player:
            return
        self.dice_pips = random.randint(1, 6)
        destination_number = player.board_number + self.dice_pips
        if destination_number > 100:
            destination_number = 100 - (destination_number - 100)
        player.position = BOARD_NUMBER_TO_POSITION[destination_number]
        self.check_player_iteraction(player)
        self.player_to_move = next(self.player_cycle)

    def nuke(self, player: Player):
        player.nukes -= 1
        self.nuke_used_this_game = True
        self.degrade()
        for player in self.players.values():
            player.position = Position(random.randint(0, 9), random.randint(0, 8))
            self.check_player_iteraction(player)

    def degrade(self):
        tokens = 1
        if random.randint(1, 3) == 1:
            tokens += 1

        while tokens > 0:
            degrade_num = random.randint(1, 6)

            if (
                self.deg_board == DEG_MAX.DEG_BOARD.value and
                self.deg_color == DEG_MAX.DEG_COLOR.value and
                self.deg_pieces == DEG_MAX.DEG_PIECES.value and
                self.deg_dice == DEG_MAX.DEG_DICE.value and
                self.deg_nuke_text == DEG_MAX.DEG_NUKE_TEXT.value
            ):
                if self.deg_piece_shake < DEG_MAX.DEG_PIECE_SHAKE.value:
                    self.deg_piece_shake = 1
                else:
                    break

            if degrade_num == 1 and self.deg_board < DEG_MAX.DEG_BOARD.value:
                self.deg_board += 1
                tokens -= 1
            elif degrade_num == 2 and self.deg_color < DEG_MAX.DEG_COLOR.value:
                self.deg_color += 1
                tokens -= 1
            elif degrade_num == 3 and self.deg_pieces < DEG_MAX.DEG_PIECES.value:
                self.deg_pieces += 1
                tokens -= 1
            elif degrade_num == 4 and self.deg_dice < DEG_MAX.DEG_DICE.value:
                self.deg_dice += 1
                tokens -= 1
            elif degrade_num == 5 and self.deg_nuke_text < DEG_MAX.DEG_NUKE_TEXT.value:
                self.deg_nuke_text += 1
                tokens -= 1
            elif degrade_num == 6 and self.deg_snakes_and_ladders < DEG_MAX.DEG_SNAKES_AND_LADDERS.value:
                self.deg_snakes_and_ladders += 1
                tokens -= 1

    # Debug code
    def activate_debug(self, player: Player):
        self.set_player_color(player, "Red")
        player.ready = True

    def debug_give_stuff(self, player: Player):
        if DEBUG_FLAGS.get("let_there_be_nukes"):
            player.nukes = 100
        if DEBUG_FLAGS.get("i_just_want_to_win"):
            player.position = (1, 9)

    def debug_move(self, player: Player, direction):
        if direction == "Up":
            player.y += 1
        if direction == "Down":
            player.y -= 1
        if direction == "Left":
            player.x -= 1
        if direction == "Right":
            player.x += 1
        self.check_player_iteraction(player)
