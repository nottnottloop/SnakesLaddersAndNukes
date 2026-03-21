# game_serializer.py
from ..shared import game_pb2

def game_to_proto(game_obj) -> game_pb2.Game:
    """
    Convert a Python Game object into a Protobuf Game message.
    """

    proto_game = game_pb2.Game()
    # --- Simple fields ---
    proto_game.game_id = game_obj.game_id
    proto_game.debug = game_obj.debug
    proto_game.started = game_obj.started
    proto_game.game_type = game_obj.game_type

    # --- Players ---
    for i, player_obj in game_obj.players.items():
        proto_player = proto_game.players[i]
        proto_player.player_id = player_obj.player_id
        proto_player.position.x = player_obj.position.x
        proto_player.position.y = player_obj.position.y

        if player_obj.color:
            proto_player.color = player_obj.color

        proto_player.nukes = player_obj.nukes
        proto_player.ready = player_obj.ready
    # --- Player to move ---
    if game_obj.player_to_move:
        proto_game.player_to_move_id = game_obj.player_to_move.player_id
    # --- Winner ---
    if game_obj.winner:
        proto_game.winner_id = game_obj.winner.player_id
    proto_game.dice_pips = game_obj.dice_pips

    proto_game.nukes_used = game_obj.nukes_used

    # --- Events ---
    proto_game.events.extend(game_obj.events)

    # --- Movables ---
    for m in game_obj.movables:
        proto_m = proto_game.movables.add()
        proto_m.position.x = m.position.x
        proto_m.position.y = m.position.y
        proto_m.vector.x = m.vector.x
        proto_m.vector.y = m.vector.y
        proto_m.sprite = m.sprite
        proto_m.type = m.type
    # --- Nukes ---
    for n in game_obj.nukes:
        proto_n = proto_game.nukes.add()
        proto_n.position.x = n.x
        proto_n.position.y = n.y

    # --- Degredation state ---
    proto_game.deg_board = game_obj.deg_board
    proto_game.deg_color = game_obj.deg_color
    proto_game.deg_pieces = game_obj.deg_pieces
    proto_game.deg_dice = game_obj.deg_dice
    proto_game.deg_nuke_text = game_obj.deg_nuke_text
    proto_game.deg_snakes_and_ladders = game_obj.deg_snakes_and_ladders
    proto_game.deg_piece_shake = game_obj.deg_piece_shake

    # --- Computed fields ---
    proto_game.taken_colors.extend(game_obj.taken_colors)
    proto_game.players_are_ready = game_obj.players_are_ready

    return proto_game

# Optional helper to serialize directly to bytes
def serialize_game(game_obj) -> bytes:
    proto_game = game_to_proto(game_obj)
    return proto_game.SerializeToString()
