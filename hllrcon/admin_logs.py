import re
from datetime import UTC, datetime
from typing import Annotated, ClassVar, Self, cast

from pydantic import BaseModel, Field

RE_ADMIN_LOG = re.compile(
    r"^\[.+? \((?P<timestamp>\d+)\)\] (?P<message>[\w\W]+)$",
    flags=re.MULTILINE,
)


__all__ = (
    "AdminLog",
    "MatchEndAdminLog",
    "MatchStartAdminLog",
    "PlayerBanAdminLog",
    "PlayerConnectAdminLog",
    "PlayerDisconnectAdminLog",
    "PlayerEnterAdminCameraAdminLog",
    "PlayerKickAdminLog",
    "PlayerKillAdminLog",
    "PlayerLeaveAdminCameraAdminLog",
    "PlayerReceiveMessageAdminLog",
    "PlayerSendMessageAdminLog",
    "PlayerTeamKillAdminLog",
    "UnrecognizedAdminLog",
)


class AdminLog(BaseModel):
    _log_types: ClassVar[list[type["Self"]]] = []

    pattern: ClassVar[re.Pattern]

    timestamp: datetime
    raw_message: Annotated[str, Field(exclude=True)]

    @classmethod
    def __init_subclass__(cls: type[Self], pattern: str | None) -> None:
        super().__init_subclass__()

        cls.pattern = re.compile(pattern or r"^[\w\W]*$", flags=re.MULTILINE)

        # AdminLog holds a list of all log types, whereas the subclass only holds itself
        if pattern:
            cls._log_types = [cls]
            AdminLog._log_types.append(cls)
        else:
            cls._log_types = []

    @classmethod
    def parse(cls, log: str) -> Self:
        match = RE_ADMIN_LOG.match(log)
        if not match:
            msg = f"Invalid log line: {log}"
            raise ValueError(msg)

        timestamp = datetime.fromtimestamp(int(match.group("timestamp")), UTC)
        message = str(match.group("message"))

        for log_type in cls._log_types:
            match = log_type.pattern.match(message)
            if match:
                return log_type(
                    timestamp=timestamp,
                    raw_message=message,
                    **match.groupdict(),
                )

        return cast(
            "Self",
            UnrecognizedAdminLog(
                timestamp=timestamp,
                raw_message=message,
            ),
        )


class UnrecognizedAdminLog(AdminLog, pattern=None):
    pass


class PlayerConnectAdminLog(
    AdminLog,
    pattern=r"CONNECTED (?P<player_name>.*) \((?P<player_id>\d+|[\da-f]{32})\)$",
):
    player_name: str
    player_id: str


class PlayerDisconnectAdminLog(
    AdminLog,
    pattern=r"DISCONNECTED (?P<player_name>.*) \((?P<player_id>\d+|[\da-f]{32})\)$",
):
    player_name: str
    player_id: str


class PlayerKillAdminLog(
    AdminLog,
    pattern=(
        r"^KILL: "
        r"(?P<instigator_name>.+)\((?P<instigator_team_name>Allies|Axis)\/(?P<instigator_id>\d{17}|[\da-f]{32})\)"
        r" -> "
        r"(?P<victim_name>.+)\((?P<victim_team_name>Allies|Axis)\/(?P<victim_id>\d{17}|[\da-f]{32})\)"
        r" with (?P<weapon>.+)"
    ),
):
    instigator_name: str
    instigator_team_name: str
    instigator_id: str
    victim_name: str
    victim_team_name: str
    victim_id: str
    weapon: str


class PlayerTeamKillAdminLog(
    AdminLog,
    pattern=(
        r"^TEAM KILL: "
        r"(?P<instigator_name>.+)\((?P<instigator_team_name>Allies|Axis)\/(?P<instigator_id>\d{17}|[\da-f]{32})\)"
        r" -> "
        r"(?P<victim_name>.+)\((?P<victim_team_name>Allies|Axis)\/(?P<victim_id>\d{17}|[\da-f]{32})\)"
        r" with (?P<weapon>.+)"
    ),
):
    instigator_name: str
    instigator_team_name: str
    instigator_id: str
    victim_name: str
    victim_team_name: str
    victim_id: str
    weapon: str


class PlayerSendMessageAdminLog(
    AdminLog,
    pattern=(
        r"CHAT\[(?P<channel>Team|Unit)\]"
        r"\[(?P<player_name>.+)\((?P<player_team_name>Allies|Axis)\/(?P<player_id>\d{17}|[\da-f]{32})\)\]:"
        r" (?P<message>.+)"
    ),
):
    channel: str
    player_name: str
    player_team_name: str
    player_id: str
    message: str


class PlayerReceiveMessageAdminLog(
    AdminLog,
    pattern=(
        r"MESSAGE: player \[(?P<player_name>.*)\], content \[(?P<message>[\w\W]*)\]$"
    ),
):
    player_name: str
    message: str


class PlayerEnterAdminCameraAdminLog(
    AdminLog,
    pattern=(
        r"Player \[(?P<player_name>.+) \((?P<player_id>\d{17}|[\da-f]{32})\)\]"
        r" Entered Admin Camera"
    ),
):
    player_name: str
    player_id: str


class PlayerLeaveAdminCameraAdminLog(
    AdminLog,
    pattern=(
        r"Player \[(?P<player_name>.+) \((?P<player_id>\d{17}|[\da-f]{32})\)\]"
        r" Left Admin Camera"
    ),
):
    player_name: str
    player_id: str


class PlayerKickAdminLog(
    AdminLog,
    pattern=r"KICK: \[(?P<player_name>.*)\] has been kicked\. \[(?P<reason>[\w\W]*)\]$",
):
    player_name: str
    reason: str


class PlayerBanAdminLog(
    AdminLog,
    pattern=r"BAN: \[(?P<player_name>.*)\] has been banned\. \[(?P<reason>[\w\W]*)\]$",
):
    player_name: str
    reason: str


class MatchStartAdminLog(
    AdminLog,
    pattern=r"MATCH START (?P<map_name>.+)",
):
    map_name: str


class MatchEndAdminLog(
    AdminLog,
    pattern=(
        r"MATCH ENDED `(?P<map_name>.+)` ALLIED \((?P<allied_score>\d)"
        r" - (?P<axis_score>\d)\) AXIS"
    ),
):
    map_name: str
    allied_score: int
    axis_score: int


# TODO: Vote kick log lines
