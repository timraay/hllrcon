from enum import IntEnum, StrEnum
from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class Response(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
    )


# TODO: Add console platforms
class PlayerPlatform(StrEnum):
    STEAM = "steam"
    EPIC = "epic"
    XBOX = "xbl"


# TODO: Add console platforms
class SupportedPlatform(StrEnum):
    STEAM = "Steam"
    PC_XBOX = "WinGDK"
    EPIC = "eos"


class PlayerTeam(IntEnum):
    GER = 0
    US = 1
    RUS = 2
    GB = 3
    DAK = 4
    B8A = 5
    UNASSIGNED = 6


class PlayerRole(IntEnum):
    Rifleman = 0
    Assault = 1
    AutomaticRifleman = 2
    Medic = 3
    Spotter = 4
    Support = 5
    MachineGunner = 6
    HeavyMachineGunner = 6
    AntiTank = 7
    Engineer = 8
    Officer = 9
    Sniper = 10
    Crewman = 11
    TankCommander = 12
    ArmyCommander = 13


class GetAdminLogResponseEntry(Response):
    timestamp: str
    message: str


class GetAdminLogResponse(Response):
    entries: list[GetAdminLogResponseEntry]


class GetCommandsResponseEntry(Response):
    id: str = Field(validation_alias="iD")
    friendly_name: str
    is_client_supported: bool


class GetCommandsResponse(Response):
    entries: list[GetCommandsResponseEntry]


class GetPlayerResponseScoreData(Response):
    combat: int = Field(validation_alias="cOMBAT")
    offense: int
    defense: int
    support: int


class GetPlayerResponseWorldPosition(Response):
    x: float
    """The east-west horizontal axis. Between -100000 and 100000."""

    y: float
    """The north-south horizontal axis. Between -100000 and 100000."""

    z: float
    """The vertical axis."""


class GetPlayerResponse(Response):
    name: str
    """The player's name"""

    clan_tag: str
    """The player's clan tag. Empty string if none."""

    id: str = Field(validation_alias="iD")
    """The player's ID"""

    platform: PlayerPlatform
    """The player's platform"""

    eos_id: str = Field(validation_alias="eosId")
    """The player's Epic Online Services ID"""

    level: int
    """The player's level"""

    team: PlayerTeam
    """The player's team"""

    role: PlayerRole
    """The player's role."""

    platoon: str
    """The name of the player's squad. Empty string if not in a squad."""

    loadout: str
    """The player's current loadout. Might not be accurate if not spawned in."""

    kills: int
    """The player's kills"""

    deaths: int
    """The player's deaths"""

    score_data: GetPlayerResponseScoreData
    """The player's score"""

    world_position: GetPlayerResponseWorldPosition
    """The player's position in centimeters"""


class GetPlayersResponse(Response):
    players: list[GetPlayerResponse]


class GetMapRotationResponseEntry(Response):
    name: str
    game_mode: str
    time_of_day: str
    id: str = Field(validation_alias="iD")
    position: int


class GetMapRotationResponse(Response):
    maps: list[GetMapRotationResponseEntry] = Field(validation_alias="mAPS")


class GetServerSessionResponse(Response):
    server_name: str
    map_name: str
    game_mode: str
    player_count: int
    max_player_count: int
    queue_count: int
    max_queue_count: int
    vip_queue_count: int
    max_vip_queue_count: int


class GetServerConfigResponse(Response):
    server_name: str
    build_number: str
    build_revision: str
    supported_platforms: list[SupportedPlatform]
    password_protected: bool


class GetBannedWordsResponse(Response):
    banned_words: list[str]


class GetCommandDetailsResponseComboParameter(Response):
    type: Literal["Combo"]
    """The type of parameter"""

    name: str
    """The user-friendly name of the parameter"""

    id: str = Field(validation_alias="iD")
    """The name of the parameter"""

    display_member: str
    """A comma-separated list of user-friendly values for this parameter. An empty
    string if `type` is not \"Combo\""""

    value_member: str
    """A comma-separated list of values for this parameter. An empty string if `type` is
    not \"Combo\""""


class GetCommandDetailsResponseTextParameter(Response):
    type: Literal["Text", "Number"]
    """The type of parameter"""

    name: str
    """The user-friendly name of the parameter"""

    id: str = Field(validation_alias="iD")
    """The name of the parameter"""

    display_member: Literal[""]
    """A comma-separated list of user-friendly values for this parameter. An empty
    string if `type` is not \"Combo\""""

    value_member: Literal[""]
    """A comma-separated list of values for this parameter. An empty string if `type` is
    not \"Combo\""""


GetCommandDetailsResponseParameter: TypeAlias = (
    GetCommandDetailsResponseComboParameter | GetCommandDetailsResponseTextParameter
)


class GetCommandDetailsResponse(Response):
    name: str
    """Name of the command"""

    text: str
    """User-friendly name of the command"""

    description: str
    """Description of the command"""

    dialogue_parameters: list[GetCommandDetailsResponseParameter]
    """A list of parameters for this command"""
