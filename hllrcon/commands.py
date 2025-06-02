import asyncio
import json
from abc import ABC, abstractmethod
from collections.abc import Callable, Coroutine, Mapping
from functools import wraps
from typing import Any, ParamSpec, TypeVar

from hllrcon.responses import (
    AdminLogResponse,
    GetAllCommandsResponse,
    GetCommandDetailsResponse,
    GetMapRotationResponse,
    GetPlayerResponse,
    GetPlayersResponse,
    GetServerConfigResponse,
    GetServerSessionResponse,
)

P = ParamSpec("P")
DictT = TypeVar("DictT", bound=Mapping[str, Any])


def cast_response_to_dict(
    dict_type: type[DictT],
) -> Callable[
    [Callable[P, Coroutine[Any, Any, str]]],
    Callable[P, Coroutine[Any, Any, DictT]],
]:
    def decorator(
        func: Callable[P, Coroutine[Any, Any, str]],
    ) -> Callable[P, Coroutine[Any, Any, DictT]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> DictT:
            result = await func(*args, **kwargs)
            parsed_result = json.loads(result)
            if not isinstance(parsed_result, dict):
                msg = f"Expected JSON content to be a dict, got {type(parsed_result)}"
                raise TypeError(msg)
            return dict_type(**parsed_result)

        return wrapper

    return decorator


class RconCommands(ABC):
    @abstractmethod
    async def execute(
        self,
        command: str,
        version: int,
        body: str | dict[str, Any] = "",
    ) -> str:
        """Execute a command on the RCON server."""

    async def add_admin(self, player_id: str, admin_group: str, comment: str) -> None:
        await self.execute(
            "AddAdmin",
            2,
            {"PlayerId": player_id, "AdminGroup": admin_group, "Comment": comment},
        )

    async def remove_admin(self, player_id: str) -> None:
        await self.execute(
            "RemoveAdmin",
            2,
            {
                "PlayerId": player_id,
            },
        )

    @cast_response_to_dict(AdminLogResponse)
    async def admin_log(self, seconds_span: int, filter_: str | None = None) -> str:
        if seconds_span < 0:
            msg = "seconds_span must be a non-negative integer"
            raise ValueError(msg)

        return await self.execute(
            "AdminLog",
            2,
            {
                "LogBackTrackTime": seconds_span,
                "Filters": filter_ or "",
            },
        )

    async def change_map(self, map_name: str) -> None:
        await self.execute(
            "ChangeMap",
            2,
            {
                "MapName": map_name,
            },
        )

    async def change_sector_layout(
        self,
        sector1: str,
        sector2: str,
        sector3: str,
        sector4: str,
        sector5: str,
    ) -> None:
        await self.execute(
            "ChangeSectorLayout",
            2,
            {
                "Sector_1": sector1,
                "Sector_2": sector2,
                "Sector_3": sector3,
                "Sector_4": sector4,
                "Sector_5": sector5,
            },
        )

    async def add_map_to_rotation(self, map_name: str, index: int) -> None:
        await self.execute(
            "AddMapToRotation",
            2,
            {
                "MapName": map_name,
                "Index": index,
            },
        )

    async def remove_map_from_rotation(self, index: int) -> None:
        await self.execute(
            "RemoveMapFromRotation",
            2,
            {
                "Index": index,
            },
        )

    async def add_map_to_sequence(self, map_name: str, index: int) -> None:
        await self.execute(
            "AddMapToSequence",
            2,
            {
                "MapName": map_name,
                "Index": index,
            },
        )

    async def remove_map_from_sequence(self, index: int) -> None:
        await self.execute(
            "RemoveMapFromSequence",
            2,
            {
                "Index": index,
            },
        )

    async def set_map_shuffle_enabled(self, *, enabled: bool) -> None:
        await self.execute(
            "ShuffleMapSequence",
            2,
            {
                "Enable": enabled,
            },
        )

    async def move_map_from_sequence(self, old_index: int, new_index: int) -> None:
        await self.execute(
            "MoveMapFromSequence",
            2,
            {
                "CurrentIndex": old_index,
                "NewIndex": new_index,
            },
        )

    @cast_response_to_dict(GetAllCommandsResponse)
    async def get_all_commands(self) -> str:
        return await self.execute("DisplayableCommands", 2)

    async def set_team_switch_cooldown(self, minutes: int) -> None:
        await self.execute(
            "SetTeamSwitchCooldown",
            2,
            {
                "TeamSwitchTimer": minutes,
            },
        )

    async def set_max_queued_players(self, num: int) -> None:
        await self.execute(
            "SetMaxQueuedPlayers",
            2,
            {
                "MaxQueuedPlayers": num,
            },
        )

    async def set_idle_kick_duration(self, minutes: int) -> None:
        await self.execute(
            "SetIdleKickDuration",
            2,
            {
                "IdleTimeoutMinutes": minutes,
            },
        )

    async def message_all_players(self, message: str) -> None:
        await self.execute(
            "SendServerMessage",
            2,
            {
                "Message": message,
            },
        )

    @cast_response_to_dict(GetPlayerResponse)
    async def get_player(self, player_id: str) -> str:
        return await self.execute(
            "ServerInformation",
            2,
            {"Name": "player", "Value": player_id},
        )

    @cast_response_to_dict(GetPlayersResponse)
    async def get_players(self) -> str:
        return await self.execute(
            "ServerInformation",
            2,
            {"Name": "players", "Value": ""},
        )

    @cast_response_to_dict(GetMapRotationResponse)
    async def get_map_rotation(self) -> str:
        return await self.execute(
            "ServerInformation",
            2,
            {"Name": "maprotation", "Value": ""},
        )

    @cast_response_to_dict(GetMapRotationResponse)
    async def get_map_sequence(self) -> str:
        return await self.execute(
            "ServerInformation",
            2,
            {"Name": "mapsequence", "Value": ""},
        )

    @cast_response_to_dict(GetServerSessionResponse)
    async def get_server_session(self) -> str:
        return await self.execute(
            "ServerInformation",
            2,
            {"Name": "session", "Value": ""},
        )

    @cast_response_to_dict(GetServerConfigResponse)
    async def get_server_config(self) -> str:
        return await self.execute(
            "ServerInformation",
            2,
            {"Name": "serverconfig", "Value": ""},
        )

    async def broadcast(self, message: str) -> None:
        await self.execute(
            "ServerBroadcast",
            2,
            {
                "Message": message,
            },
        )

    async def set_high_ping_threshold(self, ms: int) -> None:
        await self.execute(
            "SetHighPingThreshold",
            2,
            {
                "HighPingThresholdMs": ms,
            },
        )

    @cast_response_to_dict(GetCommandDetailsResponse)
    async def get_command_details(self, command: str) -> str:
        return await self.execute("ClientReferenceData", 2, command)

    async def message_player(self, player_id: str, message: str) -> None:
        await self.execute(
            "SendServerMessage",
            2,
            {
                "Message": message,
                "PlayerId": player_id,
            },
        )

    async def kill_player(self, player_id: str, message: str) -> None:
        await self.execute(
            "PunishPlayer",
            2,
            {
                "PlayerId": player_id,
                "Reason": message,
            },
        )

    async def kick_player(self, player_id: str, message: str) -> None:
        await self.execute(
            "Kick",
            2,
            {
                "PlayerId": player_id,
                "Reason": message,
            },
        )

    async def ban_player(
        self,
        player_id: str,
        reason: str,
        admin_name: str,
        duration_hours: int | None = None,
    ) -> None:
        if duration_hours:
            await self.execute(
                "TemporaryBan",
                2,
                {
                    "PlayerId": player_id,
                    "Duration": duration_hours,
                    "Reason": reason,
                    "AdminName": admin_name,
                },
            )
        else:
            await self.execute(
                "PermanentBan",
                2,
                {
                    "PlayerId": player_id,
                    "Reason": reason,
                    "AdminName": admin_name,
                },
            )

    async def remove_temp_ban(self, player_id: str) -> None:
        await self.execute(
            "RemoveTempBan",
            2,
            {
                "PlayerId": player_id,
            },
        )

    async def remove_permanent_ban(self, player_id: str) -> None:
        await self.execute(
            "RemovePermanentBan",
            2,
            {
                "PlayerId": player_id,
            },
        )

    async def remove_ban(self, player_id: str) -> None:
        await asyncio.gather(
            self.remove_temp_ban(player_id),
            self.remove_permanent_ban(player_id),
        )

    async def set_auto_balance_enabled(self, *, enabled: bool) -> None:
        await self.execute(
            "SetAutoBalance",
            2,
            {
                "EnableAutoBalance": enabled,
            },
        )

    async def set_auto_balance_threshold(self, player_threshold: int) -> None:
        await self.execute(
            "AutoBalanceThreshold",
            2,
            {
                "AutoBalanceThreshold": player_threshold,
            },
        )

    async def set_vote_kick_enabled(self, *, enabled: bool) -> None:
        await self.execute(
            "EnableVoteToKick",
            2,
            {
                "Enabled": enabled,
            },
        )

    async def reset_vote_kick_thresholds(self) -> None:
        await self.execute("ResetVoteToKickThreshold", 2)

    async def set_vote_kick_thresholds(self, thresholds: list[tuple[int, int]]) -> None:
        await self.execute(
            "SetVoteToKickThreshold",
            2,
            {
                "ThresholdValue": ",".join([f"{p},{v}" for p, v in thresholds]),
            },
        )
