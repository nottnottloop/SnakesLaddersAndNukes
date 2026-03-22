import random

from ..shared.constants import *
from .game_pb2 import ColorEnum

class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.position: Position = Position(0, 0)
        self.color: ColorEnum | None = None
        self.nukes = 0
        self.ready = False
    
    @property
    def board_number(self):
        return POSITION_TO_BOARD_NUMBER[self.position]
    
    def __repr__(self):
        return str(f"Player ID: {self.player_id}")
    
class Movable:
    def __init__(self, position, vector, sprite, type):
        self.position: Position = position
        self.vector: Position = vector
        self.sprite: str = sprite
        self.type: str = type

class Nuke:
    def __init__(self, position):
        self.position: Position = position

class Game:
    def __init__(self, game_id):
        self.game_id: int = game_id
        self.debug = False
        self.started = False
        self.game_mode = "Normal"
        
        self.players: dict[int, Player] = {}
        self.player_to_move: Player = None
        self.player_cycle: PlayerCycler = None
        self.winner: Player = None
        self.dice_pips = random.randint(1, 6)

        self.nukes_used = 0

        self.events: list[str] = []
        self.movables: list[Movable] = []
        self.nukes: list[Position] = []

        self.deg_board = 0
        self.deg_color = 0
        self.deg_pieces = 0
        self.deg_dice = 0
        self.deg_nuke_text = 0
        self.deg_snakes_and_ladders = 0
        self.deg_piece_shake = 0

    @property
    def taken_colors(self) -> set[str]:
        return [player.color for player in self.players.values() if player.color is not None]

    @property
    def players_are_ready(self) -> set[str]:
        return all(player.ready for player in self.players.values())

    # Connection and lobby screen
    def add_new_player(self, player_id):
        self.players[player_id] = Player(player_id)
        self.player_cycle = PlayerCycler(self.players.values())
        self.player_to_move = next(self.player_cycle)

    def player_lost_connection(self, player: Player):
        current_id = self.player_to_move.player_id
        leaver_id = player.player_id
        del self.players[leaver_id]
        if not self.players:
            self.player_to_move = None
            return
        
        if current_id == leaver_id:
            player_after_leaver_id = next(self.player_cycle).player_id
            self.player_cycle = PlayerCycler(self.players.values())
            self.player_cycle.set_index_to_player_id(player_after_leaver_id)
        else:
            self.player_cycle = PlayerCycler(self.players.values())
            self.player_cycle.set_index_to_player_id(current_id)
        self.player_to_move = next(self.player_cycle)

    def set_player_color(self, player: Player, color: str):
        player.color = TEXT_TO_ENUM_COLOR_MAP[color]

    def cycle_game_mode(self):
        self.game_mode = GAME_MODES[(GAME_MODES.index(self.game_mode) + 1) % len(GAME_MODES)]

    def set_player_ready(self, player: Player):
        player.ready = True
        if self.players_are_ready:
            self.started = True
            self.events.append("papers_please")
            self.generate_objects()
            if self.debug:
                for player in self.players.values():
                    player.nukes = 2**31 - 1
                    player.position = Position(5, 5)

    # Gameplay
    def calculate_destination_position(self, start_pos: Position, vector: Position) -> Position:
        return Position(start_pos.x + vector.x, start_pos.y + vector.y)

    def generate_objects(self):
        self.movables = []
        self.nukes = []
        movables_to_place = [
            Movable(None, Position(-2, -2), "snake2", "snake"),
            Movable(None, Position(0, -6), "snake3", "snake"),
            Movable(None, Position(3, -5), "snake4", "snake"),
            # Make the little snake1 render above the other, snakier snakes
            Movable(None, Position(-1, -1), "snake1", "snake"),
            Movable(None, Position(3, 3), "ladder1", "ladder"),
            Movable(None, Position(0, 2), "ladder2", "ladder"),
            Movable(None, Position(-1, 2), "ladder3", "ladder"),
            Movable(None, Position(0, 5), "ladder4", "ladder"),
        ]

        for movable in movables_to_place:
            while True:
                possible_position = Position(random.randint(0, 9), random.randint(0, 9))
                if possible_position == Position(0, 9):
                    continue
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

        if self.game_mode == "Normal":
            nukes_to_generate = (5, 15)
        elif self.game_mode == "Peaceful":
            nukes_to_generate = (0, 0)
        elif self.game_mode == "WW3":
            nukes_to_generate = (98, 98)

        for _ in range(random.randint(nukes_to_generate[0], nukes_to_generate[1])):
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
                self.events.append("nuke_collected")
                del self.nukes[i]

    def check_player_interaction(self, player: Player):
        self.potentially_collect_nuke(player)
        for movable in self.movables:
            if player.position == movable.position:
                player.position = self.calculate_destination_position(player.position, movable.vector)
                self.events.append(movable.type)
        self.potentially_collect_nuke(player)
        if POSITION_TO_BOARD_NUMBER[player.position] == 100:
            self.winner = player
            self.events.append("winner")

    def roll_dice(self, player: Player):
        if not self.player_to_move == player:
            return
        self.dice_pips = random.randint(1, 6)
        destination_number = player.board_number + self.dice_pips
        if destination_number > 100:
            destination_number = 100 - (destination_number - 100)
        player.position = BOARD_NUMBER_TO_POSITION[destination_number]
        self.check_player_interaction(player)
        self.player_to_move = next(self.player_cycle)
        self.events.append("dice_rolled")

    def nuke(self, player: Player):
        if player.nukes > 0:
            player.nukes -= 1
            self.nukes_used += 1
            self.events.append("nuke_used")
            if self.nukes_used == 7:
                self.events.append("but_nobody_came")
            elif self.nukes_used == 20:
                self.events.append("genocide")
            self.degrade()
            for player in self.players.values():
                player.position = Position(random.randint(0, 9), random.randint(0, 8))
                self.check_player_interaction(player)

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
    def toggle_debug(self):
        self.debug = not self.debug
        self.events.append("debug")

    def debug_move(self, player: Player, direction):
        if direction == "Up":
            player.position = Position(player.position.x, player.position.y + 1)
        elif direction == "Down":
            player.position = Position(player.position.x, player.position.y - 1)
        elif direction == "Right":
            player.position = Position(player.position.x + 1, player.position.y)
        elif direction == "Left":
            player.position = Position(player.position.x - 1, player.position.y)
        if player.position in POSITION_TO_BOARD_NUMBER:
            self.check_player_interaction(player)

    def reset_degredation(self):
        self.nukes_used = 0
        self.deg_board = 0
        self.deg_color = 0
        self.deg_pieces = 0
        self.deg_dice = 0
        self.deg_nuke_text = 0
        self.deg_snakes_and_ladders = 0
        self.deg_piece_shake = 0
        self.deg_music = 0
        self.events.append("papers_please")
