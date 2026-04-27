from collections.abc import Sequence
from datetime import datetime, timedelta
from enum import IntEnum, StrEnum
from typing import Annotated, ClassVar, Generic, Literal, NamedTuple, TypeAlias, TypeVar

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PlainValidator,
)
from pydantic.alias_generators import to_camel

from hllrcon.data import Faction, GameMode, Layer, Role, TimeOfDay
from hllrcon.data.factions import HLLFaction, HLLVFaction, _Faction
from hllrcon.data.game_modes import HLLGameMode, HLLVGameMode
from hllrcon.data.layers import HLLLayer, HLLVLayer
from hllrcon.data.roles import HLLRole, HLLVRole, _Role

RoleT = TypeVar("RoleT", bound=Role)
FactionT = TypeVar("FactionT", bound=Faction)
GameModeT = TypeVar("GameModeT", bound=GameMode)
LayerT = TypeVar("LayerT", bound=Layer)

EmptyStringToNoneValidator = AfterValidator(lambda v: v or None)
SplitStringValidator = BeforeValidator(lambda x: str(x).split(",") if x else [])

__all__ = (
    "ForceMode",
    "GetAdminGroupsResponse",
    "GetAdminLogResponse",
    "GetAdminLogResponseEntry",
    "GetAdminUsersResponse",
    "GetAdminUsersResponseEntry",
    "GetAutoBalanceEnabledResponse",
    "GetAutoBalanceThresholdResponse",
    "GetBannedWordsResponse",
    "GetBansResponse",
    "GetBansResponseEntry",
    "GetCommandDetailsResponse",
    "GetCommandDetailsResponseParameter",
    "GetCommandsResponse",
    "GetCommandsResponseEntry",
    "GetHighPingThresholdResponse",
    "GetIdleKickDurationResponse",
    "GetMapRotationResponse",
    "GetMapRotationResponseEntry",
    "GetMapShuffleEnabledResponse",
    "GetPlayerResponse",
    "GetPlayerResponseScoreData",
    "GetPlayerResponseStats",
    "GetPlayerResponseWorldPosition",
    "GetPlayersResponse",
    "GetServerConfigResponse",
    "GetServerSessionResponse",
    "GetTeamSwitchCooldownResponse",
    "GetVipsResponse",
    "GetVipsResponseEntry",
    "GetVoteKickEnabledResponse",
    "GetVoteKickThresholdsResponse",
    "GetVoteKickThresholdsResponseEntry",
    "HLLGetAdminGroupsResponse",
    "HLLGetAdminLogResponse",
    "HLLGetAdminLogResponseEntry",
    "HLLGetAdminUsersResponse",
    "HLLGetAdminUsersResponseEntry",
    "HLLGetAutoBalanceEnabledResponse",
    "HLLGetAutoBalanceThresholdResponse",
    "HLLGetBannedWordsResponse",
    "HLLGetBansResponse",
    "HLLGetBansResponseEntry",
    "HLLGetCommandDetailsResponse",
    "HLLGetCommandDetailsResponseParameter",
    "HLLGetCommandsResponse",
    "HLLGetCommandsResponseEntry",
    "HLLGetHighPingThresholdResponse",
    "HLLGetIdleKickDurationResponse",
    "HLLGetMapRotationResponse",
    "HLLGetMapRotationResponseEntry",
    "HLLGetMapShuffleEnabledResponse",
    "HLLGetPlayerResponse",
    "HLLGetPlayerResponseScoreData",
    "HLLGetPlayerResponseStats",
    "HLLGetPlayerResponseWorldPosition",
    "HLLGetPlayersResponse",
    "HLLGetServerConfigResponse",
    "HLLGetServerSessionResponse",
    "HLLGetTeamSwitchCooldownResponse",
    "HLLGetVipsResponse",
    "HLLGetVipsResponseEntry",
    "HLLGetVoteKickEnabledResponse",
    "HLLGetVoteKickThresholdsResponse",
    "HLLGetVoteKickThresholdsResponseEntry",
    "HLLPlayerFactionId",
    "HLLPlayerPlatform",
    "HLLPlayerRoleId",
    "HLLSupportedPlatform",
    "HLLVGetAdminGroupsResponse",
    "HLLVGetAdminLogResponse",
    "HLLVGetAdminLogResponseEntry",
    "HLLVGetAdminUsersResponse",
    "HLLVGetAdminUsersResponseEntry",
    "HLLVGetAutoBalanceEnabledResponse",
    "HLLVGetAutoBalanceThresholdResponse",
    "HLLVGetBannedWordsResponse",
    "HLLVGetBansResponse",
    "HLLVGetBansResponseEntry",
    "HLLVGetCommandDetailsResponse",
    "HLLVGetCommandDetailsResponseParameter",
    "HLLVGetCommandsResponse",
    "HLLVGetCommandsResponseEntry",
    "HLLVGetHighPingThresholdResponse",
    "HLLVGetIdleKickDurationResponse",
    "HLLVGetMapRotationResponse",
    "HLLVGetMapRotationResponseEntry",
    "HLLVGetMapShuffleEnabledResponse",
    "HLLVGetPlayerResponse",
    "HLLVGetPlayerResponseScoreData",
    "HLLVGetPlayerResponseStats",
    "HLLVGetPlayerResponseWorldPosition",
    "HLLVGetPlayersResponse",
    "HLLVGetServerConfigResponse",
    "HLLVGetServerSessionResponse",
    "HLLVGetTeamSwitchCooldownResponse",
    "HLLVGetVipsResponse",
    "HLLVGetVipsResponseEntry",
    "HLLVGetVoteKickEnabledResponse",
    "HLLVGetVoteKickThresholdsResponse",
    "HLLVGetVoteKickThresholdsResponseEntry",
    "HLLVPlayerFactionId",
    "HLLVPlayerPlatform",
    "HLLVPlayerRoleId",
    "HLLVSupportedPlatform",
    "PlayerFactionId",
    "PlayerPlatform",
    "PlayerRoleId",
    "Response",
    "SupportedPlatform",
)


class Response(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
    )


class HLLPlayerPlatform(StrEnum):
    # TODO: Verify console platforms
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


class HLLVPlayerPlatform(StrEnum):
    # TODO: Add more
    STEAM = "EPlatformFamily::Steam"


PlayerPlatform: TypeAlias = HLLPlayerPlatform | HLLVPlayerPlatform


class HLLSupportedPlatform(StrEnum):
    # TODO: Add console platforms
    STEAM = "Steam"
    PC_XBOX = "WinGDK"
    EPIC = "eos"


class HLLVSupportedPlatform(StrEnum):
    PC_STEAM = "EPlatform::PC_Steam"
    PC_WINGDK = "EPlatform::PC_WinGDK"
    PC_EGS = "EPlatform::PC_EGS"
    XBOX_SERIESX = "EPlatform::Xbox_SeriesX"
    XBOX_SERIESS = "EPlatform::Xbox_SeriesS"
    PS5 = "EPlatform::PS5"
    PS5_PRO = "EPlatform::PS5_Pro"


SupportedPlatform: TypeAlias = HLLSupportedPlatform | HLLVSupportedPlatform


class HLLPlayerFactionId(IntEnum):
    GER = 0
    US = 1
    SOV = 2
    CW = 3
    DAK = 4
    B8A = 5
    UNASSIGNED = 6


class HLLVPlayerFactionId(IntEnum):
    US = 1
    NVA = 6
    UNASSIGNED = 8


PlayerFactionId: TypeAlias = HLLPlayerFactionId | HLLVPlayerFactionId


class HLLPlayerRoleId(IntEnum):
    RIFLEMAN = 0
    ASSAULT = 1
    AUTOMATIC_RIFLEMAN = 2
    MEDIC = 3
    SPOTTER = 4
    SUPPORT = 5
    MACHINE_GUNNER = 6
    ANTI_TANK = 7
    ENGINEER = 8
    OFFICER = 9
    SNIPER = 10
    CREWMAN = 11
    TANK_COMMANDER = 12
    COMMANDER = 13
    ARTILLERY_OBSERVER = 14
    OPERATOR = 15
    GUNNER = 16


class HLLVPlayerRoleId(IntEnum):
    RIFLEMAN = 0
    # ASSAULT
    # AUTOMATIC_RIFLEMAN
    MEDIC = 3
    SPOTTER = 4
    SPECIALIST = 5
    MACHINE_GUNNER = 6
    GRENADER = 7
    ENGINEER = 8
    SQUAD_LEADER = 9
    SNIPER = 10
    CREWMAN = 11
    TANK_COMMANDER = 12
    SUPPORT = 13
    OBSERVER = 14
    GUNNER = 15
    PILOT = 16
    LOGISTICS_OFFICER = 17
    # FLIGHT_ENGINEER
    # HELI_MEDIC
    COMMANDER = 20


PlayerRoleId: TypeAlias = HLLPlayerRoleId | HLLVPlayerRoleId


class ForceMode(StrEnum):
    IMMEDIATE = "0"
    """Force the player to be switched immediately, killing them if currently alive."""

    # TODO: Verify behavior when player is already dead
    AFTER_DEATH = "1"
    """Force the player to be switched upon death."""


class _GetAdminLogResponseEntry(Response):
    timestamp: datetime
    message: str


class HLLGetAdminLogResponseEntry(_GetAdminLogResponseEntry):
    pass


class HLLVGetAdminLogResponseEntry(_GetAdminLogResponseEntry):
    pass


GetAdminLogResponseEntry: TypeAlias = (
    HLLGetAdminLogResponseEntry | HLLVGetAdminLogResponseEntry
)


class _GetAdminLogResponse(Response):
    entries: Sequence[_GetAdminLogResponseEntry]
    """A list of log entries, oldest entries first."""


class HLLGetAdminLogResponse(_GetAdminLogResponse):
    entries: list[HLLGetAdminLogResponseEntry]


class HLLVGetAdminLogResponse(_GetAdminLogResponse):
    entries: list[HLLVGetAdminLogResponseEntry]


GetAdminLogResponse: TypeAlias = HLLGetAdminLogResponse | HLLVGetAdminLogResponse


class _GetCommandsResponseEntry(Response):
    id: str = Field(validation_alias="iD")
    friendly_name: str
    is_client_supported: bool


class HLLGetCommandsResponseEntry(_GetCommandsResponseEntry):
    pass


class HLLVGetCommandsResponseEntry(_GetCommandsResponseEntry):
    pass


GetCommandsResponseEntry: TypeAlias = (
    HLLGetCommandsResponseEntry | HLLVGetCommandsResponseEntry
)


class _GetCommandsResponse(Response):
    entries: Sequence[_GetCommandsResponseEntry]


class HLLGetCommandsResponse(_GetCommandsResponse):
    entries: list[HLLGetCommandsResponseEntry]


class HLLVGetCommandsResponse(_GetCommandsResponse):
    entries: list[HLLVGetCommandsResponseEntry]


GetCommandsResponse: TypeAlias = HLLGetCommandsResponse | HLLVGetCommandsResponse


class _GetAdminGroupsResponse(Response):
    group_names: list[str]


class HLLGetAdminGroupsResponse(_GetAdminGroupsResponse):
    pass


class HLLVGetAdminGroupsResponse(_GetAdminGroupsResponse):
    pass


GetAdminGroupsResponse: TypeAlias = (
    HLLGetAdminGroupsResponse | HLLVGetAdminGroupsResponse
)


class _GetAdminUsersResponseEntry(Response):
    user_id: str
    group: str
    comment: str


class HLLGetAdminUsersResponseEntry(_GetAdminUsersResponseEntry):
    pass


class HLLVGetAdminUsersResponseEntry(_GetAdminUsersResponseEntry):
    pass


GetAdminUsersResponseEntry: TypeAlias = (
    HLLGetAdminUsersResponseEntry | HLLVGetAdminUsersResponseEntry
)


class _GetAdminUsersResponse(Response):
    admin_users: list[GetAdminUsersResponseEntry]


class HLLGetAdminUsersResponse(_GetAdminUsersResponse):
    pass


class HLLVGetAdminUsersResponse(_GetAdminUsersResponse):
    pass


GetAdminUsersResponse: TypeAlias = HLLGetAdminUsersResponse | HLLVGetAdminUsersResponse


class _GetAutoBalanceEnabledResponse(Response):
    enabled: bool = Field(validation_alias="enable")


class HLLGetAutoBalanceEnabledResponse(_GetAutoBalanceEnabledResponse):
    pass


class HLLVGetAutoBalanceEnabledResponse(_GetAutoBalanceEnabledResponse):
    pass


GetAutoBalanceEnabledResponse: TypeAlias = (
    HLLGetAutoBalanceEnabledResponse | HLLVGetAutoBalanceEnabledResponse
)


class _GetAutoBalanceThresholdResponse(Response):
    threshold: int = Field(validation_alias="autoBalanceThreshold")


class HLLGetAutoBalanceThresholdResponse(_GetAutoBalanceThresholdResponse):
    pass


class HLLVGetAutoBalanceThresholdResponse(_GetAutoBalanceThresholdResponse):
    pass


GetAutoBalanceThresholdResponse: TypeAlias = (
    HLLGetAutoBalanceThresholdResponse | HLLVGetAutoBalanceThresholdResponse
)


class _GetTeamSwitchCooldownResponse(Response):
    minutes: int = Field(validation_alias="teamSwitchCooldown")


class HLLGetTeamSwitchCooldownResponse(_GetTeamSwitchCooldownResponse):
    pass


class HLLVGetTeamSwitchCooldownResponse(_GetTeamSwitchCooldownResponse):
    pass


GetTeamSwitchCooldownResponse: TypeAlias = (
    HLLGetTeamSwitchCooldownResponse | HLLVGetTeamSwitchCooldownResponse
)


class _GetIdleKickDurationResponse(Response):
    minutes: int = Field(validation_alias="idleTimeoutMinutes")


class HLLGetIdleKickDurationResponse(_GetIdleKickDurationResponse):
    pass


class HLLVGetIdleKickDurationResponse(_GetIdleKickDurationResponse):
    pass


GetIdleKickDurationResponse: TypeAlias = (
    HLLGetIdleKickDurationResponse | HLLVGetIdleKickDurationResponse
)


class _GetHighPingThresholdResponse(Response):
    threshold: int = Field(validation_alias="highPingThresholdMs")


class HLLGetHighPingThresholdResponse(_GetHighPingThresholdResponse):
    pass


class HLLVGetHighPingThresholdResponse(_GetHighPingThresholdResponse):
    pass


GetHighPingThresholdResponse: TypeAlias = (
    HLLGetHighPingThresholdResponse | HLLVGetHighPingThresholdResponse
)


class _GetVoteKickEnabledResponse(Response):
    enabled: bool = Field(validation_alias="enable")


class HLLGetVoteKickEnabledResponse(_GetVoteKickEnabledResponse):
    pass


class HLLVGetVoteKickEnabledResponse(_GetVoteKickEnabledResponse):
    pass


GetVoteKickEnabledResponse: TypeAlias = (
    HLLGetVoteKickEnabledResponse | HLLVGetVoteKickEnabledResponse
)


class _GetVoteKickThresholdsResponseEntry(Response):
    player_count: int
    vote_threshold: int


class HLLGetVoteKickThresholdsResponseEntry(_GetVoteKickThresholdsResponseEntry):
    pass


class HLLVGetVoteKickThresholdsResponseEntry(_GetVoteKickThresholdsResponseEntry):
    pass


GetVoteKickThresholdsResponseEntry: TypeAlias = (
    HLLGetVoteKickThresholdsResponseEntry | HLLVGetVoteKickThresholdsResponseEntry
)


class _GetVoteKickThresholdsResponse(Response):
    entries: Sequence[_GetVoteKickThresholdsResponseEntry]


class HLLGetVoteKickThresholdsResponse(_GetVoteKickThresholdsResponse):
    entries: list[HLLGetVoteKickThresholdsResponseEntry]


class HLLVGetVoteKickThresholdsResponse(_GetVoteKickThresholdsResponse):
    entries: list[HLLVGetVoteKickThresholdsResponseEntry]


GetVoteKickThresholdsResponse: TypeAlias = (
    HLLGetVoteKickThresholdsResponse | HLLVGetVoteKickThresholdsResponse
)


class _GetBansResponseEntry(Response):
    user_id: str
    user_name: str
    time_of_banning: datetime
    duration_hours: int
    ban_reason: str
    admin_name: str


class HLLGetBansResponseEntry(_GetBansResponseEntry):
    pass


class HLLVGetBansResponseEntry(_GetBansResponseEntry):
    pass


GetBansResponseEntry: TypeAlias = HLLGetBansResponseEntry | HLLVGetBansResponseEntry


class _GetBansResponse(Response):
    ban_list: Sequence[_GetBansResponseEntry]


class HLLGetBansResponse(_GetBansResponse):
    ban_list: list[HLLGetBansResponseEntry]


class HLLVGetBansResponse(_GetBansResponse):
    ban_list: list[HLLVGetBansResponseEntry]


GetBansResponse: TypeAlias = HLLGetBansResponse | HLLVGetBansResponse


class _GetPlayerResponseScoreData(Response):
    combat: int = Field(validation_alias="cOMBAT")
    offense: int
    defense: int
    support: int


class HLLGetPlayerResponseScoreData(_GetPlayerResponseScoreData):
    pass


class HLLVGetPlayerResponseScoreData(_GetPlayerResponseScoreData):
    pass


GetPlayerResponseScoreData: TypeAlias = (
    HLLGetPlayerResponseScoreData | HLLVGetPlayerResponseScoreData
)


class _GetPlayerResponseStats(Response):
    deaths: int
    infantry_kills: int
    vehicle_kills: int
    team_kills: int
    vehicles_destroyed: int


class HLLGetPlayerResponseStats(_GetPlayerResponseStats):
    pass


class HLLVGetPlayerResponseStats(_GetPlayerResponseStats):
    pass


GetPlayerResponseStats: TypeAlias = (
    HLLGetPlayerResponseStats | HLLVGetPlayerResponseStats
)


class _GetPlayerResponseWorldPosition(NamedTuple):
    x: float
    """The east-west horizontal axis. Between -100000 and 100000."""

    y: float
    """The north-south horizontal axis. Between -100000 and 100000."""

    z: float
    """The vertical axis."""


class HLLGetPlayerResponseWorldPosition(_GetPlayerResponseWorldPosition):
    pass


class HLLVGetPlayerResponseWorldPosition(_GetPlayerResponseWorldPosition):
    pass


GetPlayerResponseWorldPosition: TypeAlias = (
    HLLGetPlayerResponseWorldPosition | HLLVGetPlayerResponseWorldPosition
)


class _GetPlayerResponse(Response, Generic[FactionT, RoleT]):
    _FACTION_CLS: ClassVar[type[_Faction]]
    _ROLE_CLS: ClassVar[type[_Role]]

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

    faction_id: PlayerFactionId = Field(
        validation_alias="team",
    )
    """The ID of the player's faction."""

    role_id: PlayerRoleId = Field(validation_alias="role")
    """The ID of the player's role."""

    platoon: Annotated[str | None, EmptyStringToNoneValidator]
    """The name of the player's squad."""

    loadout: str
    """The player's current loadout. Might not be accurate if not spawned in."""

    stats: _GetPlayerResponseStats
    """The player's current game statistics"""

    score_data: _GetPlayerResponseScoreData
    """The player's score"""

    world_position: _GetPlayerResponseWorldPosition
    """The player's position in centimeters"""

    @property
    def faction(self) -> FactionT | None:
        return self._FACTION_CLS.by_id(self.faction_id)  # type: ignore[return-value]

    @property
    def role(self) -> RoleT:
        return self._ROLE_CLS.by_id(self.role_id)  # type: ignore[return-value]


class HLLGetPlayerResponse(_GetPlayerResponse[HLLFaction, HLLRole]):
    _FACTION_CLS = HLLFaction
    _ROLE_CLS = HLLRole

    platform: HLLPlayerPlatform
    faction_id: HLLPlayerFactionId = Field(validation_alias="team")
    role_id: HLLPlayerRoleId = Field(validation_alias="role")
    stats: HLLGetPlayerResponseStats
    score_data: HLLGetPlayerResponseScoreData
    world_position: HLLGetPlayerResponseWorldPosition


class HLLVGetPlayerResponse(_GetPlayerResponse[HLLVFaction, HLLVRole]):
    _FACTION_CLS = HLLVFaction
    _ROLE_CLS = HLLVRole

    platform: HLLVPlayerPlatform
    faction_id: HLLVPlayerFactionId = Field(validation_alias="team")
    role_id: HLLVPlayerRoleId = Field(validation_alias="role")
    stats: HLLVGetPlayerResponseStats
    score_data: HLLVGetPlayerResponseScoreData
    world_position: HLLVGetPlayerResponseWorldPosition


GetPlayerResponse: TypeAlias = HLLGetPlayerResponse | HLLVGetPlayerResponse


class _GetPlayersResponse(Response):
    players: Sequence[_GetPlayerResponse]


class HLLGetPlayersResponse(_GetPlayersResponse):
    players: list[HLLGetPlayerResponse]


class HLLVGetPlayersResponse(_GetPlayersResponse):
    players: list[HLLVGetPlayerResponse]


GetPlayersResponse: TypeAlias = HLLGetPlayersResponse | HLLVGetPlayersResponse


class _GetMapRotationResponseEntry(Response, Generic[GameModeT, LayerT]):
    _GAME_MODE_CLS: ClassVar[type[GameMode]]
    _LAYER_CLS: ClassVar[type[Layer]]

    name: str
    game_mode_name: str = Field(validation_alias="gameMode")
    time_of_day: TimeOfDay | str
    id: Annotated[str, PlainValidator(lambda x: x.rsplit("/", 1)[-1])] = Field(
        validation_alias="iD",
    )
    position: int

    def _get_game_mode(self) -> GameModeT:
        return self._GAME_MODE_CLS.by_id(self.game_mode_name)  # type: ignore[return-value]

    @property
    def game_mode(self) -> GameModeT:
        return self._get_game_mode()

    def find_layer(self, *, strict: bool = True) -> LayerT:
        """Attempt to find the layer associated with this map rotation entry.

        Parameters
        ----------
        strict : bool, optional
            Whether to raise an exception if no such layer is known. If set to `False`,
            will attempt to generate a fallback value based on the ID. By default
            `True`.

        Returns
        -------
        Layer
            The layer associated with this map rotation entry.

        Raises
        ------
        ValueError
            No layer information is known about this entry.

        """
        return self._LAYER_CLS.by_id(self.id, strict=strict)  # type: ignore[return-value]


class HLLGetMapRotationResponseEntry(
    _GetMapRotationResponseEntry[HLLGameMode, HLLLayer],
):
    _GAME_MODE_CLS = HLLGameMode
    _LAYER_CLS = HLLLayer

    def _get_game_mode(self) -> HLLGameMode:
        if self.game_mode_name.startswith("Control Skirmish"):
            return HLLGameMode.SKIRMISH
        if self.game_mode_name.endswith("Offensive"):
            return HLLGameMode.OFFENSIVE
        return super()._get_game_mode()


class HLLVGetMapRotationResponseEntry(
    _GetMapRotationResponseEntry[HLLVGameMode, HLLVLayer],
):
    _GAME_MODE_CLS = HLLVGameMode
    _LAYER_CLS = HLLVLayer

    def _get_game_mode(self) -> HLLVGameMode:
        if self.game_mode_name.startswith("Control Skirmish"):
            return HLLVGameMode.SKIRMISH
        if self.game_mode_name.endswith("Offensive"):
            return HLLVGameMode.OFFENSIVE
        return super()._get_game_mode()


GetMapRotationResponseEntry: TypeAlias = (
    HLLGetMapRotationResponseEntry | HLLVGetMapRotationResponseEntry
)


class _GetMapRotationResponse(Response):
    current_index: int
    maps: Sequence[_GetMapRotationResponseEntry] = Field(validation_alias="mAPS")


class HLLGetMapRotationResponse(_GetMapRotationResponse):
    maps: list[HLLGetMapRotationResponseEntry] = Field(validation_alias="mAPS")


class HLLVGetMapRotationResponse(_GetMapRotationResponse):
    maps: list[HLLVGetMapRotationResponseEntry] = Field(validation_alias="mAPS")


GetMapRotationResponse: TypeAlias = (
    HLLGetMapRotationResponse | HLLVGetMapRotationResponse
)


class _GetServerSessionResponse(Response, Generic[GameModeT, LayerT]):
    _GAME_MODE_CLS: ClassVar[type[GameMode]]
    _LAYER_CLS: ClassVar[type[Layer]]

    server_name: str
    map_name: str
    map_id: str
    game_mode_id: str = Field(validation_alias="gameMode")
    remaining_match_time: Annotated[
        timedelta,
        PlainValidator(
            lambda x: x if isinstance(x, timedelta) else timedelta(seconds=int(x)),
        ),
    ]
    match_time: int
    allied_score: int
    axis_score: int
    player_count: int
    allied_player_count: int
    axis_player_count: int
    max_player_count: int
    queue_count: int
    max_queue_count: int
    vip_queue_count: int
    max_vip_queue_count: int

    @property
    def game_mode(self) -> GameModeT:
        return self._GAME_MODE_CLS.by_id(self.game_mode_id)  # type: ignore[return-value]

    def find_layer(self, *, strict: bool = True) -> LayerT:
        """Attempt to find the layer associated with this map rotation entry.

        Parameters
        ----------
        strict : bool, optional
            Whether to raise an exception if no such layer is known. If set to `False`,
            will attempt to generate a fallback value based on the ID. By default
            `True`.

        Returns
        -------
        Layer
            The layer associated with this map rotation entry.

        Raises
        ------
        ValueError
            No layer information is known about this entry.

        """
        return self._LAYER_CLS.by_id(self.map_id, strict=strict)  # type: ignore[return-value]


class HLLGetServerSessionResponse(_GetServerSessionResponse[HLLGameMode, HLLLayer]):
    _GAME_MODE_CLS = HLLGameMode
    _LAYER_CLS = HLLLayer


class HLLVGetServerSessionResponse(_GetServerSessionResponse[HLLVGameMode, HLLVLayer]):
    _GAME_MODE_CLS = HLLVGameMode
    _LAYER_CLS = HLLVLayer


GetServerSessionResponse: TypeAlias = (
    HLLGetServerSessionResponse | HLLVGetServerSessionResponse
)


class _GetServerConfigResponse(Response):
    server_name: str
    build_number: int
    build_revision: int
    supported_platforms: Sequence[SupportedPlatform]
    password_protected: bool


class HLLGetServerConfigResponse(_GetServerConfigResponse):
    supported_platforms: list[HLLSupportedPlatform]


class HLLVGetServerConfigResponse(_GetServerConfigResponse):
    supported_platforms: list[HLLVSupportedPlatform]


GetServerConfigResponse: TypeAlias = (
    HLLGetServerConfigResponse | HLLVGetServerConfigResponse
)


class _GetBannedWordsResponse(Response):
    banned_words: list[str]


class HLLGetBannedWordsResponse(_GetBannedWordsResponse):
    pass


class HLLVGetBannedWordsResponse(_GetBannedWordsResponse):
    pass


GetBannedWordsResponse: TypeAlias = (
    HLLGetBannedWordsResponse | HLLVGetBannedWordsResponse
)


class _GetVipsResponseEntry(Response):
    id: str = Field(validation_alias="iD")
    comment: str


class HLLGetVipsResponseEntry(_GetVipsResponseEntry):
    pass


class HLLVGetVipsResponseEntry(_GetVipsResponseEntry):
    pass


GetVipsResponseEntry: TypeAlias = HLLGetVipsResponseEntry | HLLVGetVipsResponseEntry


class _GetVipsResponse(Response):
    vips: Sequence[_GetVipsResponseEntry] = Field(validation_alias="vipPlayers")


class HLLGetVipsResponse(_GetVipsResponse):
    vips: list[HLLGetVipsResponseEntry] = Field(validation_alias="vipPlayers")


class HLLVGetVipsResponse(_GetVipsResponse):
    vips: list[HLLVGetVipsResponseEntry] = Field(validation_alias="vipPlayers")


GetVipsResponse: TypeAlias = HLLGetVipsResponse | HLLVGetVipsResponse


class _GetCommandDetailsResponseParameter(Response):
    type: Literal["Combo", "Text", "Number"]
    """The type of parameter"""

    name: str
    """The user-friendly name of the parameter"""

    id: str = Field(validation_alias="iD")
    """The name of the parameter"""

    display_member: Annotated[list[str], SplitStringValidator]
    """A list of user-friendly values for this parameter. Empty if `type` is not
    \"Combo\""""

    value_member: Annotated[list[str], SplitStringValidator]
    """A list of values for this parameter. An empty list if `type` is not \"Combo\""""


class HLLGetCommandDetailsResponseParameter(_GetCommandDetailsResponseParameter):
    pass


class HLLVGetCommandDetailsResponseParameter(_GetCommandDetailsResponseParameter):
    pass


GetCommandDetailsResponseParameter: TypeAlias = (
    HLLGetCommandDetailsResponseParameter | HLLVGetCommandDetailsResponseParameter
)


class _GetCommandDetailsResponse(Response):
    name: str
    """Name of the command"""

    text: str
    """User-friendly name of the command"""

    description: str
    """Description of the command"""

    dialogue_parameters: Sequence[_GetCommandDetailsResponseParameter]
    """A list of parameters for this command"""


class HLLGetCommandDetailsResponse(_GetCommandDetailsResponse):
    dialogue_parameters: list[HLLGetCommandDetailsResponseParameter]


class HLLVGetCommandDetailsResponse(_GetCommandDetailsResponse):
    dialogue_parameters: list[HLLVGetCommandDetailsResponseParameter]


GetCommandDetailsResponse: TypeAlias = (
    HLLGetCommandDetailsResponse | HLLVGetCommandDetailsResponse
)


class _GetMapShuffleEnabledResponse(Response):
    enabled: bool = Field(validation_alias="enable")


class HLLGetMapShuffleEnabledResponse(_GetMapShuffleEnabledResponse):
    pass


class HLLVGetMapShuffleEnabledResponse(_GetMapShuffleEnabledResponse):
    pass


GetMapShuffleEnabledResponse: TypeAlias = (
    HLLGetMapShuffleEnabledResponse | HLLVGetMapShuffleEnabledResponse
)
