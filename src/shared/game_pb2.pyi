from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ColorEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BLACK: _ClassVar[ColorEnum]
    WHITE: _ClassVar[ColorEnum]
    RED: _ClassVar[ColorEnum]
    BLUE: _ClassVar[ColorEnum]
    GREEN: _ClassVar[ColorEnum]
    YELLOW: _ClassVar[ColorEnum]
BLACK: ColorEnum
WHITE: ColorEnum
RED: ColorEnum
BLUE: ColorEnum
GREEN: ColorEnum
YELLOW: ColorEnum

class Position(_message.Message):
    __slots__ = ("x", "y")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    x: int
    y: int
    def __init__(self, x: _Optional[int] = ..., y: _Optional[int] = ...) -> None: ...

class Player(_message.Message):
    __slots__ = ("player_id", "position", "color", "nukes", "ready")
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    NUKES_FIELD_NUMBER: _ClassVar[int]
    READY_FIELD_NUMBER: _ClassVar[int]
    player_id: int
    position: Position
    color: ColorEnum
    nukes: int
    ready: bool
    def __init__(self, player_id: _Optional[int] = ..., position: _Optional[_Union[Position, _Mapping]] = ..., color: _Optional[_Union[ColorEnum, str]] = ..., nukes: _Optional[int] = ..., ready: _Optional[bool] = ...) -> None: ...

class Movable(_message.Message):
    __slots__ = ("position", "vector", "sprite", "type")
    POSITION_FIELD_NUMBER: _ClassVar[int]
    VECTOR_FIELD_NUMBER: _ClassVar[int]
    SPRITE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    position: Position
    vector: Position
    sprite: str
    type: str
    def __init__(self, position: _Optional[_Union[Position, _Mapping]] = ..., vector: _Optional[_Union[Position, _Mapping]] = ..., sprite: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class Nuke(_message.Message):
    __slots__ = ("position",)
    POSITION_FIELD_NUMBER: _ClassVar[int]
    position: Position
    def __init__(self, position: _Optional[_Union[Position, _Mapping]] = ...) -> None: ...

class Game(_message.Message):
    __slots__ = ("game_id", "debug", "started", "players", "player_to_move_id", "winner_id", "dice_pips", "movables", "nukes", "events", "nukes_used", "nukes_to_generate_min", "nukes_to_generate_max", "taken_colors", "players_are_ready", "deg_board", "deg_color", "deg_pieces", "deg_dice", "deg_nuke_text", "deg_snakes_and_ladders", "deg_piece_shake", "deg_music")
    class PlayersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: Player
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[Player, _Mapping]] = ...) -> None: ...
    GAME_ID_FIELD_NUMBER: _ClassVar[int]
    DEBUG_FIELD_NUMBER: _ClassVar[int]
    STARTED_FIELD_NUMBER: _ClassVar[int]
    PLAYERS_FIELD_NUMBER: _ClassVar[int]
    PLAYER_TO_MOVE_ID_FIELD_NUMBER: _ClassVar[int]
    WINNER_ID_FIELD_NUMBER: _ClassVar[int]
    DICE_PIPS_FIELD_NUMBER: _ClassVar[int]
    MOVABLES_FIELD_NUMBER: _ClassVar[int]
    NUKES_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    NUKES_USED_FIELD_NUMBER: _ClassVar[int]
    NUKES_TO_GENERATE_MIN_FIELD_NUMBER: _ClassVar[int]
    NUKES_TO_GENERATE_MAX_FIELD_NUMBER: _ClassVar[int]
    TAKEN_COLORS_FIELD_NUMBER: _ClassVar[int]
    PLAYERS_ARE_READY_FIELD_NUMBER: _ClassVar[int]
    DEG_BOARD_FIELD_NUMBER: _ClassVar[int]
    DEG_COLOR_FIELD_NUMBER: _ClassVar[int]
    DEG_PIECES_FIELD_NUMBER: _ClassVar[int]
    DEG_DICE_FIELD_NUMBER: _ClassVar[int]
    DEG_NUKE_TEXT_FIELD_NUMBER: _ClassVar[int]
    DEG_SNAKES_AND_LADDERS_FIELD_NUMBER: _ClassVar[int]
    DEG_PIECE_SHAKE_FIELD_NUMBER: _ClassVar[int]
    DEG_MUSIC_FIELD_NUMBER: _ClassVar[int]
    game_id: int
    debug: bool
    started: bool
    players: _containers.MessageMap[int, Player]
    player_to_move_id: int
    winner_id: int
    dice_pips: int
    movables: _containers.RepeatedCompositeFieldContainer[Movable]
    nukes: _containers.RepeatedCompositeFieldContainer[Nuke]
    events: _containers.RepeatedScalarFieldContainer[str]
    nukes_used: int
    nukes_to_generate_min: int
    nukes_to_generate_max: int
    taken_colors: _containers.RepeatedScalarFieldContainer[ColorEnum]
    players_are_ready: bool
    deg_board: int
    deg_color: int
    deg_pieces: int
    deg_dice: int
    deg_nuke_text: int
    deg_snakes_and_ladders: int
    deg_piece_shake: int
    deg_music: int
    def __init__(self, game_id: _Optional[int] = ..., debug: _Optional[bool] = ..., started: _Optional[bool] = ..., players: _Optional[_Mapping[int, Player]] = ..., player_to_move_id: _Optional[int] = ..., winner_id: _Optional[int] = ..., dice_pips: _Optional[int] = ..., movables: _Optional[_Iterable[_Union[Movable, _Mapping]]] = ..., nukes: _Optional[_Iterable[_Union[Nuke, _Mapping]]] = ..., events: _Optional[_Iterable[str]] = ..., nukes_used: _Optional[int] = ..., nukes_to_generate_min: _Optional[int] = ..., nukes_to_generate_max: _Optional[int] = ..., taken_colors: _Optional[_Iterable[_Union[ColorEnum, str]]] = ..., players_are_ready: _Optional[bool] = ..., deg_board: _Optional[int] = ..., deg_color: _Optional[int] = ..., deg_pieces: _Optional[int] = ..., deg_dice: _Optional[int] = ..., deg_nuke_text: _Optional[int] = ..., deg_snakes_and_ladders: _Optional[int] = ..., deg_piece_shake: _Optional[int] = ..., deg_music: _Optional[int] = ...) -> None: ...
