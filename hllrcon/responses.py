from enum import IntEnum, StrEnum
from typing import Literal, TypeAlias, TypedDict


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
    HeavyMachineGunner = 6
    AntiTank = 7
    Engineer = 8
    Officer = 9
    Sniper = 10
    Crewman = 11
    TankCommander = 12
    ArmyCommander = 13


class ForceMode(IntEnum):
    IMMEDIATE = 0
    """Force the player to be switched immediately, killing them if currently alive."""

    # TODO: Verify behavior when player is already dead
    AFTER_DEATH = 1
    """Force the player to be switched upon death."""


class AdminLogResponseEntry(TypedDict):
    timestamp: str
    message: str


class AdminLogResponse(TypedDict):
    entries: list[AdminLogResponseEntry]


class GetCommandsResponseEntry(TypedDict):
    iD: str
    friendlyName: str
    isClientSupported: bool


class GetCommandsResponse(TypedDict):
    entries: list[GetCommandsResponseEntry]


class GetAdminGroupsResponse(TypedDict):
    groupNames: list[str]


class GetAdminUsersResponseEntry(TypedDict):
    userId: str
    group: str
    comment: str


class GetAdminUsersResponse(TypedDict):
    adminUsers: list[GetAdminUsersResponseEntry]


class GetBansResponseEntry(TypedDict):
    userId: str
    userName: str
    timeOfBanning: str
    durationHours: int
    banReason: str
    adminName: str


class GetBansResponse(TypedDict):
    banList: list[GetBansResponseEntry]


class GetPlayerResponseScoreData(TypedDict):
    cOMBAT: int
    offense: int
    defense: int
    support: int


class GetPlayerResponseWorldPosition(TypedDict):
    x: float
    """The east-west horizontal axis. Between -100000 and 100000."""

    y: float
    """The north-south horizontal axis. Between -100000 and 100000."""

    z: float
    """The vertical axis."""


class GetPlayerResponse(TypedDict):
    name: str
    """The player's name"""

    clanTag: str
    """The player's clan tag. Empty string if none."""

    iD: str
    """The player's ID"""

    platform: PlayerPlatform
    """The player's platform"""

    eosId: str
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

    scoreData: GetPlayerResponseScoreData
    """The player's score"""

    worldPosition: GetPlayerResponseWorldPosition
    """The player's position in centimeters"""


class GetPlayersResponse(TypedDict):
    players: list[GetPlayerResponse]


class GetMapRotationResponseEntry(TypedDict):
    name: str
    gameMode: str
    timeOfDay: str
    iD: str
    position: int


class GetMapRotationResponse(TypedDict):
    mAPS: list[GetMapRotationResponseEntry]


class GetServerSessionResponse(TypedDict):
    serverName: str
    mapName: str
    gameMode: str
    remainingMatchTime: int
    matchTime: int
    alliedScore: int
    axisScore: int
    playerCount: int
    maxPlayerCount: int
    queueCount: int
    maxQueueCount: int
    vipQueueCount: int
    maxVipQueueCount: int


class GetServerConfigResponse(TypedDict):
    serverName: str
    buildNumber: str
    buildRevision: str
    supportedPlatforms: list[SupportedPlatform]
    passwordProtected: bool


class GetBannedWordsResponse(TypedDict):
    bannedWords: list[str]


class GetCommandDetailsResponseComboParameter(TypedDict):
    type: Literal["Combo"]
    """The type of parameter"""

    name: str
    """The user-friendly name of the parameter"""

    iD: str
    """The name of the parameter"""

    displayMember: str
    """A comma-separated list of user-friendly values for this parameter. An empty
    string if `type` is not \"Combo\""""

    valueMember: str
    """A comma-separated list of values for this parameter. An empty string if `type` is
    not \"Combo\""""


class GetCommandDetailsResponseTextParameter(TypedDict):
    type: Literal["Text", "Number"]
    """The type of parameter"""

    name: str
    """The user-friendly name of the parameter"""

    iD: str
    """The name of the parameter"""

    displayMember: Literal[""]
    """A comma-separated list of user-friendly values for this parameter. An empty
    string if `type` is not \"Combo\""""

    valueMember: Literal[""]
    """A comma-separated list of values for this parameter. An empty string if `type` is
    not \"Combo\""""


GetCommandDetailsResponseParameter: TypeAlias = (
    GetCommandDetailsResponseComboParameter | GetCommandDetailsResponseTextParameter
)


class GetCommandDetailsResponse(TypedDict):
    name: str
    """Name of the command"""

    text: str
    """User-friendly name of the command"""

    description: str
    """Description of the command"""

    dialogueParameters: list[GetCommandDetailsResponseParameter]
    """A list of parameters for this command"""
