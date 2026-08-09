import logging
import re
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, ClassVar, Self, TypeAlias, TypeVar, cast

from pydantic import BaseModel, Field, PlainValidator, ValidationError

from hllrcon.data.game_modes import AnyGameMode, HLLGameMode, HLLVGameMode
from hllrcon.data.maps import AnyMap, HLLMap, HLLVMap
from hllrcon.data.teams import AnyTeam, HLLTeam, HLLVTeam
from hllrcon.data.weapons import AnyWeapon, HLLVWeapon, HLLWeapon

RE_ADMIN_LOG = re.compile(
    r"^\[.+? \((?P<timestamp>\d+)\)\] (?P<message>[\w\W]+)$",
    flags=re.MULTILINE,
)


__all__ = (
    "AnyAdminLog",
    "AnyMatchEndAdminLog",
    "AnyMatchStartAdminLog",
    "AnyPlayerBanAdminLog",
    "AnyPlayerConnectAdminLog",
    "AnyPlayerDisconnectAdminLog",
    "AnyPlayerEnterAdminCameraAdminLog",
    "AnyPlayerKickAdminLog",
    "AnyPlayerKillAdminLog",
    "AnyPlayerLeaveAdminCameraAdminLog",
    "AnyPlayerReceiveMessageAdminLog",
    "AnyPlayerSendMessageAdminLog",
    "AnyPlayerTeamKillAdminLog",
    "AnyPlayerTeamSwitchAdminLog",
    "AnyVoteKickCompleteAdminLog",
    "AnyVoteKickExpireAdminLog",
    "AnyVoteKickPassAdminLog",
    "AnyVoteKickStartAdminLog",
    "AnyVoteKickVoteAdminLog",
    "HLLAdminLog",
    "HLLMatchEndAdminLog",
    "HLLMatchStartAdminLog",
    "HLLPlayerBanAdminLog",
    "HLLPlayerConnectAdminLog",
    "HLLPlayerDisconnectAdminLog",
    "HLLPlayerEnterAdminCameraAdminLog",
    "HLLPlayerKickAdminLog",
    "HLLPlayerKillAdminLog",
    "HLLPlayerLeaveAdminCameraAdminLog",
    "HLLPlayerReceiveMessageAdminLog",
    "HLLPlayerSendMessageAdminLog",
    "HLLPlayerTeamKillAdminLog",
    "HLLPlayerTeamSwitchAdminLog",
    "HLLVAdminLog",
    "HLLVMatchEndAdminLog",
    "HLLVMatchStartAdminLog",
    "HLLVPlayerBanAdminLog",
    "HLLVPlayerConnectAdminLog",
    "HLLVPlayerDisconnectAdminLog",
    "HLLVPlayerEnterAdminCameraAdminLog",
    "HLLVPlayerKickAdminLog",
    "HLLVPlayerKillAdminLog",
    "HLLVPlayerLeaveAdminCameraAdminLog",
    "HLLVPlayerReceiveMessageAdminLog",
    "HLLVPlayerSendMessageAdminLog",
    "HLLVPlayerTeamKillAdminLog",
    "HLLVPlayerTeamSwitchAdminLog",
    "HLLVVoteKickCompleteAdminLog",
    "HLLVVoteKickExpireAdminLog",
    "HLLVVoteKickPassAdminLog",
    "HLLVVoteKickStartAdminLog",
    "HLLVVoteKickVoteAdminLog",
    "HLLVoteKickCompleteAdminLog",
    "HLLVoteKickExpireAdminLog",
    "HLLVoteKickPassAdminLog",
    "HLLVoteKickStartAdminLog",
    "HLLVoteKickVoteAdminLog",
    "UnrecognizedAdminLog",
    "VoteKickReason",
    "VoteKickResult",
    "VoteKickVoteType",
)

TeamT = TypeVar("TeamT", bound=AnyTeam)
MapT = TypeVar("MapT", bound=AnyMap)


def _team_from_name(team_cls: type[TeamT], team_name: str) -> TeamT:
    if team_name == "Allies":
        return cast("TeamT", team_cls.ALLIES)
    if team_name == "Axis":
        return cast("TeamT", team_cls.AXIS)
    msg = f"Unrecognized team name: {team_name}"
    raise ValueError(msg)


def _map_from_name(map_cls: type[MapT], map_name: str) -> MapT:
    for map_ in map_cls.all():
        if map_.name == map_name:
            return cast("MapT", map_)
    msg = f"Unrecognized map name: {map_name}"
    raise ValueError(msg)


class _AdminLog(BaseModel, frozen=True):
    _log_types: ClassVar[list[type["Self"]]] = []

    pattern: ClassVar[re.Pattern | None] = None

    timestamp: datetime
    raw_message: Annotated[str, Field(exclude=True)]

    @classmethod
    def __init_subclass__(cls: type[Self], pattern: str | None = "") -> None:
        super().__init_subclass__()

        if pattern is None:
            cls.pattern = None
        elif pattern == "":
            pass  # Inherit pattern
        else:
            cls.pattern = re.compile(pattern or r"^[\w\W]*$", flags=re.MULTILINE)

        # Register all subclasses
        cls._log_types = []
        if pattern is not None:
            for base_cls in cls.__mro__:
                if issubclass(base_cls, _AdminLog):
                    base_cls._log_types.append(cls)  # noqa: SLF001

    @classmethod
    def parse(cls, log: str) -> Self:
        match = RE_ADMIN_LOG.match(log)
        if not match:
            msg = f"Invalid log line: {log}"
            raise ValueError(msg)

        timestamp = datetime.fromtimestamp(int(match.group("timestamp")), UTC)
        message = str(match.group("message"))

        for log_type in cls._log_types:
            if log_type.pattern is None:  # pragma: no cover
                continue

            match = log_type.pattern.match(message)
            if match:
                try:
                    return log_type(
                        timestamp=timestamp,
                        raw_message=message,
                        **match.groupdict(),
                    )
                except ValidationError:
                    logging.getLogger(__name__).error(  # noqa: TRY400
                        "Failed to parse log line as %s: %s",
                        log_type.__name__,
                        message,
                    )

        return cast(
            "Self",
            UnrecognizedAdminLog(
                timestamp=timestamp,
                raw_message=message,
            ),
        )


class HLLAdminLog(_AdminLog, frozen=True):
    pass


class HLLVAdminLog(_AdminLog, frozen=True):
    pass


AnyAdminLog: TypeAlias = HLLAdminLog | HLLVAdminLog


class UnrecognizedAdminLog(_AdminLog, pattern=None, frozen=True):
    pass


class _PlayerConnectAdminLog(
    _AdminLog,
    pattern=r"CONNECTED (?P<player_name>.*) \((?P<player_id>\d+|[\da-f]{32})\)$",
    frozen=True,
):
    player_name: str
    player_id: str


class HLLPlayerConnectAdminLog(_PlayerConnectAdminLog, HLLAdminLog, frozen=True):
    pass


class HLLVPlayerConnectAdminLog(_PlayerConnectAdminLog, HLLVAdminLog, frozen=True):
    pass


AnyPlayerConnectAdminLog: TypeAlias = (
    HLLPlayerConnectAdminLog | HLLVPlayerConnectAdminLog
)


class _PlayerDisconnectAdminLog(
    _AdminLog,
    pattern=r"DISCONNECTED (?P<player_name>.*) \((?P<player_id>\d+|[\da-f]{32})\)$",
    frozen=True,
):
    player_name: str
    player_id: str


class HLLPlayerDisconnectAdminLog(_PlayerDisconnectAdminLog, HLLAdminLog, frozen=True):
    pass


class HLLVPlayerDisconnectAdminLog(
    _PlayerDisconnectAdminLog,
    HLLVAdminLog,
    frozen=True,
):
    pass


AnyPlayerDisconnectAdminLog: TypeAlias = (
    HLLPlayerDisconnectAdminLog | HLLVPlayerDisconnectAdminLog
)


class _PlayerKillAdminLog(
    _AdminLog,
    pattern=(
        r"^KILL: "
        r"(?P<instigator_name>.+)\((?P<instigator_team_name>Allies|Axis)\/(?P<instigator_id>\d{17}|[\da-f]{32})\)"
        r" -> "
        r"(?P<victim_name>.+)\((?P<victim_team_name>Allies|Axis)\/(?P<victim_id>\d{17}|[\da-f]{32})\)"
        r" with (?P<weapon_id>.+)"
    ),
    frozen=True,
):
    instigator_name: str
    instigator_team_name: str
    instigator_id: str
    victim_name: str
    victim_team_name: str
    victim_id: str
    weapon_id: str

    def get_weapon(self) -> AnyWeapon:
        raise NotImplementedError

    def get_instigator_team(self) -> AnyTeam:
        raise NotImplementedError

    def get_victim_team(self) -> AnyTeam:
        raise NotImplementedError


class HLLPlayerKillAdminLog(_PlayerKillAdminLog, HLLAdminLog, frozen=True):
    def get_weapon(self) -> HLLWeapon:
        return HLLWeapon.by_id(self.weapon_id)

    def get_instigator_team(self) -> HLLTeam:
        return _team_from_name(HLLTeam, self.instigator_team_name)

    def get_victim_team(self) -> HLLTeam:
        return _team_from_name(HLLTeam, self.victim_team_name)


class HLLVPlayerKillAdminLog(_PlayerKillAdminLog, HLLVAdminLog, frozen=True):
    def get_weapon(self) -> HLLVWeapon:
        return HLLVWeapon.by_id(self.weapon_id)

    def get_instigator_team(self) -> HLLVTeam:
        return _team_from_name(HLLVTeam, self.instigator_team_name)

    def get_victim_team(self) -> HLLVTeam:
        return _team_from_name(HLLVTeam, self.victim_team_name)


AnyPlayerKillAdminLog: TypeAlias = HLLPlayerKillAdminLog | HLLVPlayerKillAdminLog


class _PlayerTeamKillAdminLog(
    _AdminLog,
    pattern=(
        r"^TEAM KILL: "
        r"(?P<instigator_name>.+)\((?P<instigator_team_name>Allies|Axis)\/(?P<instigator_id>\d{17}|[\da-f]{32})\)"
        r" -> "
        r"(?P<victim_name>.+)\((?P<victim_team_name>Allies|Axis)\/(?P<victim_id>\d{17}|[\da-f]{32})\)"
        r" with (?P<weapon_id>.+)"
    ),
    frozen=True,
):
    instigator_name: str
    instigator_team_name: str
    instigator_id: str
    victim_name: str
    victim_team_name: str
    victim_id: str
    weapon_id: str

    def get_weapon(self) -> AnyWeapon:
        raise NotImplementedError

    def get_instigator_team(self) -> AnyTeam:
        raise NotImplementedError

    def get_victim_team(self) -> AnyTeam:
        raise NotImplementedError


class HLLPlayerTeamKillAdminLog(_PlayerTeamKillAdminLog, HLLAdminLog, frozen=True):
    def get_weapon(self) -> HLLWeapon:
        return HLLWeapon.by_id(self.weapon_id)

    def get_instigator_team(self) -> HLLTeam:
        return _team_from_name(HLLTeam, self.instigator_team_name)

    def get_victim_team(self) -> HLLTeam:
        return _team_from_name(HLLTeam, self.victim_team_name)


class HLLVPlayerTeamKillAdminLog(_PlayerTeamKillAdminLog, HLLVAdminLog, frozen=True):
    def get_weapon(self) -> HLLVWeapon:
        return HLLVWeapon.by_id(self.weapon_id)

    def get_instigator_team(self) -> HLLVTeam:
        return _team_from_name(HLLVTeam, self.instigator_team_name)

    def get_victim_team(self) -> HLLVTeam:
        return _team_from_name(HLLVTeam, self.victim_team_name)


AnyPlayerTeamKillAdminLog: TypeAlias = (
    HLLPlayerTeamKillAdminLog | HLLVPlayerTeamKillAdminLog
)


class PlayerMessageChannel(StrEnum):
    TEAM = "Team"
    UNIT = "Unit"


class _PlayerSendMessageAdminLog(
    _AdminLog,
    pattern=(
        r"CHAT\[(?P<channel>Team|Unit)\]"
        r"\[(?P<player_name>.+)\((?P<player_team_name>Allies|Axis)\/(?P<player_id>\d{17}|[\da-f]{32})\)\]:"
        r" (?P<message>.+)"
    ),
    frozen=True,
):
    channel: PlayerMessageChannel
    player_name: str
    player_team_name: str
    player_id: str
    message: str

    def get_player_team(self) -> AnyTeam:
        raise NotImplementedError


class HLLPlayerSendMessageAdminLog(
    _PlayerSendMessageAdminLog,
    HLLAdminLog,
    frozen=True,
):
    def get_player_team(self) -> HLLTeam:
        return _team_from_name(HLLTeam, self.player_team_name)


class HLLVPlayerSendMessageAdminLog(
    _PlayerSendMessageAdminLog,
    HLLVAdminLog,
    frozen=True,
):
    def get_player_team(self) -> HLLVTeam:
        return _team_from_name(HLLVTeam, self.player_team_name)


AnyPlayerSendMessageAdminLog: TypeAlias = (
    HLLPlayerSendMessageAdminLog | HLLVPlayerSendMessageAdminLog
)


class _PlayerReceiveMessageAdminLog(
    _AdminLog,
    pattern=(
        r"MESSAGE: player \[(?P<player_name>.*)\], content \[(?P<message>[\w\W]*)\]$"
    ),
    frozen=True,
):
    player_name: str
    message: str


class HLLPlayerReceiveMessageAdminLog(
    _PlayerReceiveMessageAdminLog,
    HLLAdminLog,
    frozen=True,
):
    pass


class HLLVPlayerReceiveMessageAdminLog(
    _PlayerReceiveMessageAdminLog,
    HLLVAdminLog,
    frozen=True,
):
    pass


AnyPlayerReceiveMessageAdminLog: TypeAlias = (
    HLLPlayerReceiveMessageAdminLog | HLLVPlayerReceiveMessageAdminLog
)


class _PlayerEnterAdminCameraAdminLog(
    _AdminLog,
    pattern=(
        r"Player \[(?P<player_name>.+) \((?P<player_id>\d{17}|[\da-f]{32})\)\]"
        r" Entered Admin Camera"
    ),
    frozen=True,
):
    player_name: str
    player_id: str


class HLLPlayerEnterAdminCameraAdminLog(
    _PlayerEnterAdminCameraAdminLog,
    HLLAdminLog,
    frozen=True,
):
    pass


class HLLVPlayerEnterAdminCameraAdminLog(
    _PlayerEnterAdminCameraAdminLog,
    HLLVAdminLog,
    frozen=True,
):
    pass


AnyPlayerEnterAdminCameraAdminLog: TypeAlias = (
    HLLPlayerEnterAdminCameraAdminLog | HLLVPlayerEnterAdminCameraAdminLog
)


class _PlayerLeaveAdminCameraAdminLog(
    _AdminLog,
    pattern=(
        r"Player \[(?P<player_name>.+) \((?P<player_id>\d{17}|[\da-f]{32})\)\]"
        r" Left Admin Camera"
    ),
    frozen=True,
):
    player_name: str
    player_id: str


class HLLPlayerLeaveAdminCameraAdminLog(
    _PlayerLeaveAdminCameraAdminLog,
    HLLAdminLog,
    frozen=True,
):
    pass


class HLLVPlayerLeaveAdminCameraAdminLog(
    _PlayerLeaveAdminCameraAdminLog,
    HLLVAdminLog,
    frozen=True,
):
    pass


AnyPlayerLeaveAdminCameraAdminLog: TypeAlias = (
    HLLPlayerLeaveAdminCameraAdminLog | HLLVPlayerLeaveAdminCameraAdminLog
)


class _PlayerKickAdminLog(
    _AdminLog,
    pattern=r"KICK: \[(?P<player_name>.*)\] has been kicked\. \[(?P<reason>[\w\W]*)\]$",
    frozen=True,
):
    player_name: str
    reason: str


class HLLPlayerKickAdminLog(_PlayerKickAdminLog, HLLAdminLog, frozen=True):
    pass


class HLLVPlayerKickAdminLog(_PlayerKickAdminLog, HLLVAdminLog, frozen=True):
    pass


AnyPlayerKickAdminLog: TypeAlias = HLLPlayerKickAdminLog | HLLVPlayerKickAdminLog


class _PlayerBanAdminLog(
    _AdminLog,
    pattern=r"BAN: \[(?P<player_name>.*)\] has been banned\. \[(?P<reason>[\w\W]*)\]$",
    frozen=True,
):
    player_name: str
    reason: str


class HLLPlayerBanAdminLog(_PlayerBanAdminLog, HLLAdminLog, frozen=True):
    pass


class HLLVPlayerBanAdminLog(_PlayerBanAdminLog, HLLVAdminLog, frozen=True):
    pass


AnyPlayerBanAdminLog: TypeAlias = HLLPlayerBanAdminLog | HLLVPlayerBanAdminLog


class _PlayerTeamSwitchAdminLog(
    _AdminLog,
    pattern=(
        r"^TEAMSWITCH (?P<player_name>.+) \((?P<old_team_name>None|Allies|Axis)"
        r" > (?P<new_team_name>None|Allies|Axis)\)$"
    ),
    frozen=True,
):
    player_name: str
    old_team_name: str
    new_team_name: str

    def get_old_team(self) -> AnyTeam | None:
        raise NotImplementedError

    def get_new_team(self) -> AnyTeam | None:
        raise NotImplementedError


class HLLPlayerTeamSwitchAdminLog(_PlayerTeamSwitchAdminLog, HLLAdminLog, frozen=True):
    def get_old_team(self) -> HLLTeam | None:
        if self.old_team_name == "None":
            return None
        return _team_from_name(HLLTeam, self.old_team_name)

    def get_new_team(self) -> HLLTeam | None:
        if self.new_team_name == "None":
            return None
        return _team_from_name(HLLTeam, self.new_team_name)


class HLLVPlayerTeamSwitchAdminLog(
    _PlayerTeamSwitchAdminLog,
    HLLVAdminLog,
    frozen=True,
):
    def get_old_team(self) -> HLLVTeam | None:
        if self.old_team_name == "None":
            return None
        return _team_from_name(HLLVTeam, self.old_team_name)

    def get_new_team(self) -> HLLVTeam | None:
        if self.new_team_name == "None":
            return None
        return _team_from_name(HLLVTeam, self.new_team_name)


AnyPlayerTeamSwitchAdminLog: TypeAlias = (
    HLLPlayerTeamSwitchAdminLog | HLLVPlayerTeamSwitchAdminLog
)


class _MatchStartAdminLog(
    _AdminLog,
    pattern=r"MATCH START (?P<map_name>.+) (?P<game_mode_id>.+)$",
    frozen=True,
):
    map_name: str
    game_mode_id: str

    def get_map(self) -> AnyMap:
        raise NotImplementedError

    def get_game_mode(self) -> AnyGameMode:
        raise NotImplementedError


class HLLMatchStartAdminLog(_MatchStartAdminLog, HLLAdminLog, frozen=True):
    def get_map(self) -> HLLMap:
        return _map_from_name(HLLMap, self.map_name)

    def get_game_mode(self) -> HLLGameMode:
        return HLLGameMode.by_id(self.game_mode_id)


class HLLVMatchStartAdminLog(_MatchStartAdminLog, HLLVAdminLog, frozen=True):
    def get_map(self) -> HLLVMap:
        return _map_from_name(HLLVMap, self.map_name)

    def get_game_mode(self) -> HLLVGameMode:
        return HLLVGameMode.by_id(self.game_mode_id)


AnyMatchStartAdminLog: TypeAlias = HLLMatchStartAdminLog | HLLVMatchStartAdminLog


class _MatchEndAdminLog(
    _AdminLog,
    pattern=(
        r"MATCH ENDED `(?P<map_name>.+) (?P<game_mode_id>.+)`"
        r" ALLIED \((?P<allied_score>\d) - (?P<axis_score>\d)\) AXIS"
    ),
    frozen=True,
):
    map_name: str
    game_mode_id: str
    allied_score: int
    axis_score: int

    def get_map(self) -> AnyMap:
        raise NotImplementedError

    def get_game_mode(self) -> AnyGameMode:
        raise NotImplementedError


class HLLMatchEndAdminLog(_MatchEndAdminLog, HLLAdminLog, frozen=True):
    def get_map(self) -> HLLMap:
        return _map_from_name(HLLMap, self.map_name)

    def get_game_mode(self) -> HLLGameMode:
        return HLLGameMode.by_id(self.game_mode_id)


class HLLVMatchEndAdminLog(_MatchEndAdminLog, HLLVAdminLog, frozen=True):
    def get_map(self) -> HLLVMap:
        return _map_from_name(HLLVMap, self.map_name)

    def get_game_mode(self) -> HLLVGameMode:
        return HLLVGameMode.by_id(self.game_mode_id)


AnyMatchEndAdminLog: TypeAlias = HLLMatchEndAdminLog | HLLVMatchEndAdminLog


class VoteKickReason(StrEnum):
    ABUSE = "PVR_Kick_Abuse"
    CHEATING = "PVR_Kick_Cheating"


class VoteKickVoteType(StrEnum):
    IN_FAVOUR = "PV_Favour"
    AGAINST = "PV_Against"
    IGNORED = "PV_Ignored"


class VoteKickResult(StrEnum):
    PASSED = "PVR_Passed"
    FAILED = "PVR_Failed"
    EXPIRED_OR_CANCELLED = "PVR_ExpiredOrCancelled"


# VoteKickStart
# VOTESYS: Player [Player name] Started a vote of type (PVR_Kick_Abuse) against
#   [Player name]. VoteID: [2]
class _VoteKickStartAdminLog(
    _AdminLog,
    pattern=(
        r"VOTESYS: Player \[(?P<initiator_name>.+)\] Started a vote"
        r" of type \((?P<reason>.+)\) against \[(?P<target_name>.+)\]\."
        r" VoteID: \[(?P<vote_id>\d+)\]"
    ),
    frozen=True,
):
    initiator_name: str
    target_name: str
    reason: VoteKickReason
    vote_id: int


class HLLVoteKickStartAdminLog(_VoteKickStartAdminLog, HLLAdminLog, frozen=True):
    pass


class HLLVVoteKickStartAdminLog(_VoteKickStartAdminLog, HLLVAdminLog, frozen=True):
    pass


AnyVoteKickStartAdminLog: TypeAlias = (
    HLLVoteKickStartAdminLog | HLLVVoteKickStartAdminLog
)


# VoteKickVote
# VOTESYS: Player [Player name] voted [PV_Favour] for VoteID[2]
class _VoteKickVoteAdminLog(
    _AdminLog,
    pattern=(
        r"VOTESYS: Player \[(?P<player_name>.+)\] voted \[(?P<vote_type>.+)\]"
        r" for VoteID\[(?P<vote_id>\d+)\]"
    ),
    frozen=True,
):
    player_name: str
    vote_type: VoteKickVoteType
    vote_id: int


class HLLVoteKickVoteAdminLog(_VoteKickVoteAdminLog, HLLAdminLog, frozen=True):
    pass


class HLLVVoteKickVoteAdminLog(_VoteKickVoteAdminLog, HLLVAdminLog, frozen=True):
    pass


AnyVoteKickVoteAdminLog: TypeAlias = HLLVoteKickVoteAdminLog | HLLVVoteKickVoteAdminLog


# VoteKickComplete
# VOTESYS: Vote [2] completed. Result: PVR_Passed
class _VoteKickCompleteAdminLog(
    _AdminLog,
    pattern=(r"VOTESYS: Vote \[(?P<vote_id>\d+)\] completed\. Result: (?P<result>.+)"),
    frozen=True,
):
    vote_id: int
    result: VoteKickResult


class HLLVoteKickCompleteAdminLog(_VoteKickCompleteAdminLog, HLLAdminLog, frozen=True):
    pass


class HLLVVoteKickCompleteAdminLog(
    _VoteKickCompleteAdminLog,
    HLLVAdminLog,
    frozen=True,
):
    pass


AnyVoteKickCompleteAdminLog: TypeAlias = (
    HLLVoteKickCompleteAdminLog | HLLVVoteKickCompleteAdminLog
)


# VoteKickExpire
# VOTESYS: Vote [1] expired before completion.
# VOTESYS: Vote [1] prematurely expired.
class _VoteKickExpireAdminLog(
    _AdminLog,
    pattern=(
        r"VOTESYS: Vote \[(?P<vote_id>\d+)\] (?P<prematurely>prematurely )?"
        r"expired(?: before completion)?\."
    ),
    frozen=True,
):
    vote_id: int
    prematurely: Annotated[bool, PlainValidator(bool)]


class HLLVoteKickExpireAdminLog(_VoteKickExpireAdminLog, HLLAdminLog, frozen=True):
    pass


class HLLVVoteKickExpireAdminLog(_VoteKickExpireAdminLog, HLLVAdminLog, frozen=True):
    pass


AnyVoteKickExpireAdminLog: TypeAlias = (
    HLLVoteKickExpireAdminLog | HLLVVoteKickExpireAdminLog
)


# VoteKickPass
# VOTESYS: Vote Kick {Player name} successfully passed. [For: 2/1 - Against: 0]
class _VoteKickPassAdminLog(
    _AdminLog,
    pattern=(
        r"VOTESYS: Vote Kick \{(?P<target_name>.+)\} successfully passed\."
        r" \[For: (?P<num_votes_in_favour>\d+)\/(?P<num_votes_required>\d+)"
        r" - Against: (?P<num_votes_against>\d+)\]"
    ),
    frozen=True,
):
    target_name: str
    num_votes_in_favour: int
    num_votes_required: int
    num_votes_against: int


class HLLVoteKickPassAdminLog(_VoteKickPassAdminLog, HLLAdminLog, frozen=True):
    pass


class HLLVVoteKickPassAdminLog(_VoteKickPassAdminLog, HLLVAdminLog, frozen=True):
    pass


AnyVoteKickPassAdminLog: TypeAlias = HLLVoteKickPassAdminLog | HLLVVoteKickPassAdminLog
