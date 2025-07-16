from datetime import datetime
from enum import IntEnum, StrEnum
from typing import Annotated, Literal, TypeAlias

from pydantic import AfterValidator, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

EmptyStringToNoneValidator = AfterValidator(lambda v: v or None)


class Response(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
    )


# TODO: Add console platforms
class PlayerPlatform(StrEnum):
    STEAM = "steam"
    """Steam"""

    EPIC = "epic"
    """Epic Games Store"""

    XBL = "xbl"
    """Xbox Game Pass"""

    PSN = "psn"
    """PlayStation Network"""

    PS5 = "ps5"
    """PlayStation 5"""

    XSX = "xsx"
    """Xbox Series X|S"""


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

    def is_allied(self) -> bool:
        """Check if the team is an allied team.

        Allied factions are:
        - United States (`US`)
        - Soviet Union (`RUS`)
        - Great Britain (`GB`)
        - British 8th Army (`B8A`)

        Returns
        -------
        bool
            `True` if the team is an allied team, `False` otherwise.

        """
        return self in {
            PlayerTeam.US,
            PlayerTeam.RUS,
            PlayerTeam.GB,
            PlayerTeam.B8A,
        }

    def is_axis(self) -> bool:
        """Check if the team is an axis team.

        Axis factions are:
        - Germany (`GER`)
        - Deutsche Afrika Korps (`DAK`)

        Returns
        -------
        bool
            `True` if the team is an axis team, `False` otherwise.

        """
        return self in {
            PlayerTeam.GER,
            PlayerTeam.DAK,
        }


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

    def is_infantry(self) -> bool:
        """Check if the role is associated with infantry units.

        Roles included are:
        - Officer
        - Rifleman
        - Assault
        - Automatic Rifleman
        - Medic
        - Support
        - Machine Gunner
        - Anti-Tank
        - Engineer

        Returns
        -------
        bool
            `True` if the role is an infantry role, `False` otherwise.

        """
        return self in {
            PlayerRole.Rifleman,
            PlayerRole.Assault,
            PlayerRole.AutomaticRifleman,
            PlayerRole.Medic,
            PlayerRole.Support,
            PlayerRole.MachineGunner,
            PlayerRole.AntiTank,
            PlayerRole.Engineer,
            PlayerRole.Officer,
        }

    def is_tanker(self) -> bool:
        """Check if the role is associated with armor units.

        Roles included are:
        - Tank Commander
        - Crewman

        Returns
        -------
        bool
            `True` if the role is a tanker role, `False` otherwise.

        """
        return self in {
            PlayerRole.Crewman,
            PlayerRole.TankCommander,
        }

    def is_recon(self) -> bool:
        """Check if the role is associated with recon units.

        Roles included are:
        - Spotter
        - Sniper

        Returns
        -------
        bool
            `True` if the role is a recon role, `False` otherwise.

        """
        return self in {
            PlayerRole.Spotter,
            PlayerRole.Sniper,
        }

    def is_squad_leader(self) -> bool:
        """Check if the role is that of a squad leader.

        Roles included are:
        - Commander
        - Officer
        - Tank Commander
        - Spotter

        Returns
        -------
        bool
            `True` if the role is a squad leader role, `False` otherwise.

        """
        return self in {
            PlayerRole.ArmyCommander,
            PlayerRole.Officer,
            PlayerRole.TankCommander,
            PlayerRole.Spotter,
        }


class ForceMode(IntEnum):
    IMMEDIATE = 0
    """Force the player to be switched immediately, killing them if currently alive."""

    # TODO: Verify behavior when player is already dead
    AFTER_DEATH = 1
    """Force the player to be switched upon death."""


class GetAdminLogResponseEntry(Response):
    timestamp: datetime
    message: str


class GetAdminLogResponse(Response):
    entries: list[GetAdminLogResponseEntry]


class GetCommandsResponseEntry(Response):
    id: str = Field(validation_alias="iD")
    friendly_name: str
    is_client_supported: bool


class GetCommandsResponse(Response):
    entries: list[GetCommandsResponseEntry]


class GetAdminGroupsResponse(Response):
    group_names: list[str]


class GetAdminUsersResponseEntry(Response):
    user_id: str
    group: str
    comment: str


class GetAdminUsersResponse(Response):
    admin_users: list[GetAdminUsersResponseEntry]


class GetBansResponseEntry(Response):
    user_id: str
    user_name: str
    time_of_banning: str
    duration_hours: int
    ban_reason: str
    admin_name: str


class GetBansResponse(Response):
    ban_list: list[GetBansResponseEntry]


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

    clan_tag: Annotated[str | None, EmptyStringToNoneValidator]
    """The player's clan tag. Empty string if none."""

    id: str = Field(validation_alias="iD")
    """The player's ID"""

    platform: PlayerPlatform
    """The player's platform"""

    eos_id: str = Field(validation_alias="eosId")
    """The player's Epic Online Services ID"""

    level: int
    """The player's level"""

    team: Annotated[
        PlayerTeam | None,
        AfterValidator(lambda v: None if v == PlayerTeam.UNASSIGNED else v),
    ]
    """The player's team"""

    role: PlayerRole
    """The player's role."""

    platoon: Annotated[str | None, EmptyStringToNoneValidator]
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
    remaining_match_time: int
    match_time: int
    allied_score: int
    axis_score: int
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
