import json
from functools import partial
from typing import Any, Literal
from unittest import mock

import pytest
from hllrcon.commands import RconCommands, cast_response_to_bool, cast_response_to_model
from hllrcon.exceptions import HLLCommandError, HLLMessageError
from hllrcon.responses import (
    ForceMode,
)
from pydantic import BaseModel, ValidationError

pytestmark = pytest.mark.asyncio


class RconCommandsStub(RconCommands):
    def __init__(
        self,
        command: str,
        version: int,
        body: str | dict[str, Any] = "",
        response: str | HLLCommandError = "",
    ) -> None:
        super().__init__()
        self.command = command
        self.version = version
        self.body = body
        self.response = response

    async def execute(
        self,
        command: str,
        version: int,
        body: str | dict[str, Any] = "",
    ) -> str:
        assert command == self.command
        assert version == self.version
        assert body == self.body

        if isinstance(self.response, HLLCommandError):
            raise self.response
        return self.response


class CustomModel(BaseModel):
    x: int
    y: int


class TestCastResponseToModel:
    async def test_cast_response_to_model_success(self) -> None:
        called = {}

        @cast_response_to_model(CustomModel)
        async def dummy_func(x: int, y: int = 0) -> str:
            called["x"] = x
            called["y"] = y
            return f'{{"x": {x + 1}, "y": {y + 1}}}'

        result = await dummy_func(5, y=10)
        assert result.x == 6
        assert result.y == 11
        assert called == {"x": 5, "y": 10}

    async def test_cast_response_to_model_raises_on_invalid_json(self) -> None:
        @cast_response_to_model(CustomModel)
        async def dummy_func() -> str:
            return "not a json"

        with pytest.raises(ValidationError, match="Invalid JSON"):
            await dummy_func()

    async def test_cast_response_to_model_raises_on_non_dict(self) -> None:
        @cast_response_to_model(CustomModel)
        async def dummy_func() -> str:
            return '["not a dict"]'

        with pytest.raises(ValidationError, match="Input should be an object"):
            await dummy_func()

    async def test_cast_response_to_model_preserves_function_metadata(self) -> None:
        @cast_response_to_model(CustomModel)
        async def dummy_func() -> str:
            """Docstring here."""
            return '{"a": 1}'

        assert dummy_func.__name__ == "dummy_func"
        assert dummy_func.__doc__ == "Docstring here."


class TestCastResponseToBool:
    async def test_cast_response_to_bool_success(self) -> None:
        called = {}

        @cast_response_to_bool({400})
        async def dummy_func() -> None:
            called["called"] = True

        result = await dummy_func()
        assert result is True
        assert called == {"called": True}

    async def test_cast_response_to_bool_failure(self) -> None:
        called = {}

        @cast_response_to_bool({400})
        async def dummy_func() -> None:
            called["called"] = True
            msg = "Command failed"
            raise HLLCommandError(400, msg)

        result = await dummy_func()
        assert result is False
        assert called == {"called": True}

    async def test_cast_response_to_bool_exception(self) -> None:
        called = {}
        msg = "Internal server error"

        @cast_response_to_bool({400})
        async def dummy_func() -> None:
            called["called"] = True
            raise HLLCommandError(500, msg)

        with pytest.raises(HLLCommandError, match=msg):
            await dummy_func()
        assert called == {"called": True}


class TestCommands:
    async def test_commands_add_admin(self) -> None:
        player_id = "Player ID"
        admin_group = "Admin Group"
        comment = "Comment"

        await RconCommandsStub(
            "AddAdmin",
            2,
            {
                "PlayerId": player_id,
                "AdminGroup": admin_group,
                "Comment": comment,
            },
        ).add_admin(player_id, admin_group, comment)

    async def test_commands_remove_admin(self) -> None:
        player_id = "Player ID"

        await RconCommandsStub(
            "RemoveAdmin",
            2,
            {"PlayerId": player_id},
        ).remove_admin(player_id)

    @pytest.mark.parametrize("filter_", ["Filter", None])
    async def test_commands_admin_log(
        self,
        filter_: str | None,
    ) -> None:
        await RconCommandsStub(
            "GetAdminLog",
            2,
            {"LogBackTrackTime": 60, "Filters": filter_ or ""},
            (
                '{"entries": ['
                '{"timestamp": "2023-10-01T12:00:00Z", "message": "Log 1"},'
                '{"timestamp": "2023-10-01T12:01:00Z", "message": "Log 2"}'
                "]}"
            ),
        ).get_admin_log(60, filter_)

    async def test_commands_admin_log_seconds_span_invalid(self) -> None:
        with pytest.raises(
            ValueError,
            match="seconds_span must be a non-negative integer",
        ):
            await RconCommandsStub(
                "GetAdminLog",
                2,
                {"LogBackTrackTime": -1, "Filters": ""},
            ).get_admin_log(-1)

    async def test_commands_change_map(self) -> None:
        map_name = "Map Name"
        await RconCommandsStub(
            "ChangeMap",
            2,
            {"MapName": map_name},
        ).change_map(map_name)

    async def test_commands_get_available_sector_names(self) -> None:
        command_id = "SetSectorLayout"
        sector_names: tuple[list[str], ...] = (
            ["ROAD TO RECOGNE", "COBRU APPROACH", "ROAD TO NOVILLE"],
            ["COBRU FACTORY", "FOY", "FLAK BATTERY"],
            ["WEST BEND", "SOUTHERN EDGE", "DUGOUT BARN"],
            ["N30 HIGHWAY", "BIZORY-FOY ROAD", "EASTERN OURTHE"],
            ["ROAD TO BASTOGNE", "BOIS JACQUES", "FOREST OUTSKIRTS"],
        )
        response = await RconCommandsStub(
            "GetClientReferenceData",
            2,
            command_id,
            json.dumps(
                {
                    "name": "SetSectorLayout",
                    "text": "Set Sector Layout",
                    "description": "Configure the active sector layout",
                    "dialogueParameters": [
                        {
                            "type": "Combo",
                            "name": f"Sector {i + 1}",
                            "iD": f"Sector_{i + 1}",
                            "displayMember": ",".join(sector_names[i]),
                            "valueMember": ",".join(sector_names[i]),
                        }
                        for i in range(5)
                    ],
                },
            ),
        ).get_available_sector_names()
        assert response == sector_names

    async def test_commands_get_available_sector_names_invalid_message(self) -> None:
        command_id = "SetSectorLayout"
        stub = RconCommandsStub(
            "GetClientReferenceData",
            2,
            command_id,
            json.dumps(
                {
                    "name": "SetSectorLayout",
                    "text": "Set Sector Layout",
                    "description": "Configure the active sector layout",
                    "dialogueParameters": [
                        {
                            "type": "Combo",
                            "name": "Sector 1",
                            "iD": "Some incorrect ID",
                            "displayMember": "blib,blab,blob",
                            "valueMember": "blib,blab,blob",
                        },
                    ],
                },
            ),
        )

        with pytest.raises(HLLMessageError):
            await stub.get_available_sector_names()

    async def test_commands_change_sector_layout(self) -> None:
        sector1 = "Sector 1"
        sector2 = "Sector 2"
        sector3 = "Sector 3"
        sector4 = "Sector 4"
        sector5 = "Sector 5"

        await RconCommandsStub(
            "SetSectorLayout",
            2,
            {
                "Sector_1": sector1,
                "Sector_2": sector2,
                "Sector_3": sector3,
                "Sector_4": sector4,
                "Sector_5": sector5,
            },
        ).set_sector_layout(sector1, sector2, sector3, sector4, sector5)

    async def test_commands_add_map_to_rotation(self) -> None:
        map_name = "Map1"
        index = 3
        await RconCommandsStub(
            "AddMapToRotation",
            2,
            {"MapName": map_name, "Index": index},
        ).add_map_to_rotation(map_name, index)

    async def test_commands_remove_map_from_rotation(self) -> None:
        index = 2
        await RconCommandsStub(
            "RemoveMapFromRotation",
            2,
            {"Index": index},
        ).remove_map_from_rotation(index)

    async def test_commands_add_map_to_sequence(self) -> None:
        map_name = "Map2"
        index = 1
        await RconCommandsStub(
            "AddMapToSequence",
            2,
            {"MapName": map_name, "Index": index},
        ).add_map_to_sequence(map_name, index)

    async def test_commands_remove_map_from_sequence(self) -> None:
        index = 4
        await RconCommandsStub(
            "RemoveMapFromSequence",
            2,
            {"Index": index},
        ).remove_map_from_sequence(index)

    async def test_commands_set_map_shuffle_enabled(self) -> None:
        await RconCommandsStub(
            "SetMapShuffleEnabled",
            2,
            {"Enable": True},
        ).set_map_shuffle_enabled(enabled=True)

    async def test_commands_move_map_from_sequence(self) -> None:
        old_index = 1
        new_index = 2
        await RconCommandsStub(
            "MoveMapInSequence",
            2,
            {"CurrentIndex": old_index, "NewIndex": new_index},
        ).move_map_in_sequence(old_index, new_index)

    async def test_commands_get_available_maps(self) -> None:
        command_id = "AddMapToRotation"
        maps = ["foy_warfare", "stmariedumont_warfare", "hurtgenforest_warfare_V2"]
        response = await RconCommandsStub(
            "GetClientReferenceData",
            2,
            command_id,
            json.dumps(
                {
                    "name": command_id,
                    "text": "Add Map to Rotation",
                    "description": "Add a new map to the map rotation at an index.",
                    "dialogueParameters": [
                        {
                            "type": "Combo",
                            "name": "Map Name",
                            "iD": "MapName",
                            "displayMember": ",".join(maps),
                            "valueMember": ",".join(maps),
                        },
                        {
                            "type": "Number",
                            "name": "At Index",
                            "iD": "Index",
                            "displayMember": "",
                            "valueMember": "",
                        },
                    ],
                },
            ),
        ).get_available_maps()
        assert response == maps

    async def test_commands_get_available_maps_invalid_message(self) -> None:
        command_id = "AddMapToRotation"
        maps = ["foy_warfare", "stmariedumont_warfare", "hurtgenforest_warfare_V2"]
        stub = RconCommandsStub(
            "GetClientReferenceData",
            2,
            command_id,
            json.dumps(
                {
                    "name": command_id,
                    "text": "Add Map to Rotation",
                    "description": "Add a new map to the map rotation at an index.",
                    "dialogueParameters": [
                        {
                            "type": "Combo",
                            "name": "Map Name",
                            "iD": "NotMapName",  # Changed "MapName" to "NotMapName"
                            "displayMember": ",".join(maps),
                            "valueMember": ",".join(maps),
                        },
                        {
                            "type": "Number",
                            "name": "At Index",
                            "iD": "Index",
                            "displayMember": "",
                            "valueMember": "",
                        },
                    ],
                },
            ),
        )

        with pytest.raises(HLLMessageError):
            await stub.get_available_maps()

    async def test_commands_get_commands(self) -> None:
        await RconCommandsStub(
            "GetDisplayableCommands",
            2,
            response=json.dumps(
                {
                    "entries": [
                        {
                            "iD": "cmd1",
                            "friendlyName": "Command 1",
                            "isClientSupported": True,
                        },
                        {
                            "iD": "cmd2",
                            "friendlyName": "Command 2",
                            "isClientSupported": False,
                        },
                    ],
                },
            ),
        ).get_commands()

    async def test_commands_get_admin_groups(self) -> None:
        await RconCommandsStub(
            "GetAdminGroups",
            2,
            response=json.dumps(
                {
                    "groupNames": [
                        "owner",
                        "senior",
                        "junior",
                        "spectator",
                    ],
                },
            ),
        ).get_admin_groups()

    async def test_commands_get_admin_users(self) -> None:
        await RconCommandsStub(
            "GetAdminUsers",
            2,
            response=json.dumps(
                {
                    "adminUsers": [
                        {
                            "userId": "user1",
                            "group": "owner",
                            "comment": "Owner of the server",
                        },
                        {
                            "userId": "user2",
                            "group": "senior",
                            "comment": "Senior admin",
                        },
                    ],
                },
            ),
        ).get_admin_users()

    async def test_commands_get_permanent_bans(self) -> None:
        await RconCommandsStub(
            "GetPermanentBans",
            2,
            response=json.dumps(
                {
                    "banList": [
                        {
                            "userId": "player1",
                            "userName": "Player One",
                            "timeOfBanning": "2023-10-01T12:00:00Z",
                            "durationHours": 0,
                            "banReason": "Cheating",
                            "adminName": "Admin1",
                        },
                        {
                            "userId": "player2",
                            "userName": "Player Two",
                            "timeOfBanning": "2023-10-02T12:00:00Z",
                            "durationHours": 0,
                            "banReason": "Toxic behavior",
                            "adminName": "Admin2",
                        },
                    ],
                },
            ),
        ).get_permanent_bans()

    async def test_commands_get_temporary_bans(self) -> None:
        await RconCommandsStub(
            "GetTemporaryBans",
            2,
            response=json.dumps(
                {
                    "banList": [
                        {
                            "userId": "player3",
                            "userName": "Player Three",
                            "timeOfBanning": "2023-10-03T12:00:00Z",
                            "durationHours": 24,
                            "banReason": "AFK farming",
                            "adminName": "Admin3",
                        },
                        {
                            "userId": "player4",
                            "userName": "Player Four",
                            "timeOfBanning": "2023-10-04T12:00:00Z",
                            "durationHours": 48,
                            "banReason": "Inappropriate language",
                            "adminName": "Admin4",
                        },
                    ],
                },
            ),
        ).get_temporary_bans()

    async def test_commands_disband_squad(self) -> None:
        team_id = 1
        squad_id = 2
        reason = "Disbanding for testing"
        await RconCommandsStub(
            "DisbandPlatoon",
            2,
            {
                "TeamIndex": team_id,
                "SquadIndex": squad_id,
                "Reason": reason,
            },
        ).disband_squad(team_id, squad_id, reason)

    async def test_commands_force_team_switch(self) -> None:
        player_id = "player123"
        force_mode = ForceMode.IMMEDIATE
        response = await RconCommandsStub(
            "ForceTeamSwitch",
            2,
            {
                "PlayerId": player_id,
                "ForceMode": force_mode,
            },
        ).force_team_switch(player_id, force_mode)
        assert response is True

    async def test_commands_set_team_switch_cooldown(self) -> None:
        minutes = 10
        await RconCommandsStub(
            "SetTeamSwitchCooldown",
            2,
            {"TeamSwitchTimer": minutes},
        ).set_team_switch_cooldown(minutes)

    async def test_commands_set_max_queued_players(self) -> None:
        num = 20
        await RconCommandsStub(
            "SetMaxQueuedPlayers",
            2,
            {"MaxQueuedPlayers": num},
        ).set_max_queued_players(num)

    async def test_commands_set_idle_kick_duration(self) -> None:
        minutes = 15
        await RconCommandsStub(
            "SetIdleKickDuration",
            2,
            {"IdleTimeoutMinutes": minutes},
        ).set_idle_kick_duration(minutes)

    async def test_commands_message_all_players(self) -> None:
        message = "Hello all!"
        await RconCommandsStub(
            "SetWelcomeMessage",
            2,
            {"Message": message},
        ).set_welcome_message(message)

    async def test_commands_get_player(self) -> None:
        player_id = "player123"

        await RconCommandsStub(
            "GetServerInformation",
            2,
            {"Name": "player", "Value": player_id},
            json.dumps(
                {
                    "name": "Player1",
                    "clanTag": "ClanA",
                    "iD": player_id,
                    "platform": "steam",
                    "eosId": "1234567890",
                    "level": 25,
                    "team": 1,
                    "role": 1,
                    "platoon": "ABLE",
                    "loadout": "Combat Medic",
                    "kills": 150,
                    "deaths": 50,
                    "scoreData": {
                        "cOMBAT": 100,
                        "offense": 50,
                        "defense": 30,
                        "support": 20,
                    },
                    "worldPosition": {
                        "x": 1000,
                        "y": 2000,
                        "z": 300,
                    },
                },
            ),
        ).get_player(player_id)

    async def test_commands_get_players(self) -> None:
        await RconCommandsStub(
            "GetServerInformation",
            2,
            {"Name": "players", "Value": ""},
            json.dumps(
                {
                    "players": [
                        {
                            "name": "Player1",
                            "clanTag": "ClanA",
                            "iD": "123",
                            "platform": "steam",
                            "eosId": "1234567890",
                            "level": 25,
                            "team": 1,
                            "role": 1,
                            "platoon": "ABLE",
                            "loadout": "Combat Medic",
                            "kills": 150,
                            "deaths": 50,
                            "scoreData": {
                                "cOMBAT": 100,
                                "offense": 50,
                                "defense": 30,
                                "support": 20,
                            },
                            "worldPosition": {
                                "x": 1000,
                                "y": 2000,
                                "z": 300,
                            },
                        },
                    ],
                },
            ),
        ).get_players()

    async def test_commands_get_map_rotation(self) -> None:
        await RconCommandsStub(
            "GetServerInformation",
            2,
            {"Name": "maprotation", "Value": ""},
            json.dumps(
                {
                    "mAPS": [
                        {
                            "name": "Map1",
                            "gameMode": "Warfare",
                            "timeOfDay": "Day",
                            "iD": "map1",
                            "position": 0,
                        },
                        {
                            "name": "Map2",
                            "gameMode": "Offensive",
                            "timeOfDay": "Day",
                            "iD": "map2",
                            "position": 1,
                        },
                    ],
                },
            ),
        ).get_map_rotation()

    async def test_commands_get_map_sequence(self) -> None:
        await RconCommandsStub(
            "GetServerInformation",
            2,
            {"Name": "mapsequence", "Value": ""},
            json.dumps(
                {
                    "mAPS": [
                        {
                            "name": "Map1",
                            "gameMode": "Warfare",
                            "timeOfDay": "Day",
                            "iD": "map1",
                            "position": 0,
                        },
                        {
                            "name": "Map2",
                            "gameMode": "Offensive",
                            "timeOfDay": "Day",
                            "iD": "map2",
                            "position": 1,
                        },
                    ],
                },
            ),
        ).get_map_sequence()

    async def test_commands_get_server_session(self) -> None:
        await RconCommandsStub(
            "GetServerInformation",
            2,
            {"Name": "session", "Value": ""},
            json.dumps(
                {
                    "serverName": "My Server",
                    "mapName": "Map1",
                    "gameMode": "Warfare",
                    "remainingMatchTime": 0,
                    "matchTime": 6000,
                    "alliedScore": 2,
                    "axisScore": 2,
                    "playerCount": 98,
                    "alliedPlayerCount": 0,
                    "axisPlayerCount": 0,
                    "maxPlayerCount": 100,
                    "queueCount": 5,
                    "maxQueueCount": 6,
                    "vipQueueCount": 1,
                    "maxVipQueueCount": 2,
                },
            ),
        ).get_server_session()

    async def test_commands_get_server_config(self) -> None:
        await RconCommandsStub(
            "GetServerInformation",
            2,
            {"Name": "serverconfig", "Value": ""},
            json.dumps(
                {
                    "serverName": "My Server",
                    "buildNumber": "12345",
                    "buildRevision": "67890",
                    "supportedPlatforms": ["Steam", "WinGDK", "eos"],
                    "passwordProtected": False,
                },
            ),
        ).get_server_config()

    async def test_commands_get_banned_words(self) -> None:
        await RconCommandsStub(
            "GetServerInformation",
            2,
            {"Name": "bannedwords", "Value": ""},
            json.dumps(
                {
                    "bannedWords": ["garry", "blueberry"],
                },
            ),
        ).get_banned_words()

    async def test_commands_get_vips(self) -> None:
        await RconCommandsStub(
            "GetServerInformation",
            2,
            {"Name": "vipplayers", "Value": ""},
            json.dumps(
                {
                    "vipPlayerIds": ["123", "456"],
                },
            ),
        ).get_vips()

    async def test_commands_broadcast(self) -> None:
        message = "Broadcast message"
        await RconCommandsStub(
            "ServerBroadcast",
            2,
            {"Message": message},
        ).broadcast(message)

    async def test_commands_set_high_ping_threshold(self) -> None:
        ms = 150
        await RconCommandsStub(
            "SetHighPingThreshold",
            2,
            {"HighPingThresholdMs": ms},
        ).set_high_ping_threshold(ms)

    async def test_commands_get_command_details(self) -> None:
        command_id = "cmd1"
        await RconCommandsStub(
            "GetClientReferenceData",
            2,
            command_id,
            json.dumps(
                {
                    "name": command_id,
                    "text": "Command 1",
                    "description": "This is a test command.",
                    "dialogueParameters": [
                        {
                            "type": "Text",
                            "name": "param1",
                            "iD": "p1",
                            "displayMember": "",
                            "valueMember": "",
                        },
                        {
                            "type": "Number",
                            "name": "param2",
                            "iD": "p2",
                            "displayMember": "",
                            "valueMember": "",
                        },
                        {
                            "type": "Combo",
                            "name": "param3",
                            "iD": "p3",
                            "displayMember": "Option1,Option2",
                            "valueMember": "1,2",
                        },
                    ],
                },
            ),
        ).get_command_details(command_id)

    async def test_commands_message_player(self) -> None:
        player_id = "pid"
        message = "Private message"
        await RconCommandsStub(
            "MessagePlayer",
            2,
            {"Message": message, "PlayerId": player_id},
        ).message_player(player_id, message)

    async def test_commands_kill_player(self) -> None:
        player_id = "pid"
        reason = "Misconduct"
        result = await RconCommandsStub(
            "PunishPlayer",
            2,
            {"PlayerId": player_id, "Reason": reason},
        ).kill_player(player_id, reason)
        assert result is True

    async def test_commands_kill_player_already_dead(self) -> None:
        player_id = "pid"
        reason = "Already dead"
        stub = RconCommandsStub(
            "PunishPlayer",
            2,
            {"PlayerId": player_id, "Reason": reason},
            response=HLLCommandError(500, "Unable to perform request."),
        )

        result = await stub.kill_player(player_id, reason)
        assert result is False

    async def test_commands_kick_player(self) -> None:
        player_id = "pid"
        reason = "AFK"
        await RconCommandsStub(
            "KickPlayer",
            2,
            {"PlayerId": player_id, "Reason": reason},
        ).kick_player(player_id, reason)

    async def test_commands_ban_player_permanent(self) -> None:
        player_id = "pid"
        reason = "Cheating"
        admin_name = "admin"
        await RconCommandsStub(
            "PermanentBanPlayer",
            2,
            {"PlayerId": player_id, "Reason": reason, "AdminName": admin_name},
        ).ban_player(player_id, reason, admin_name)

    async def test_commands_ban_player_temporary(self) -> None:
        player_id = "pid"
        reason = "Toxic"
        admin_name = "admin"
        duration_hours = 12
        await RconCommandsStub(
            "TemporaryBanPlayer",
            2,
            {
                "PlayerId": player_id,
                "Duration": duration_hours,
                "Reason": reason,
                "AdminName": admin_name,
            },
        ).ban_player(player_id, reason, admin_name, duration_hours=duration_hours)

    async def test_commands_remove_temp_ban(self) -> None:
        player_id = "pid"
        await RconCommandsStub(
            "RemoveTemporaryBan",
            2,
            {"PlayerId": player_id},
        ).remove_temporary_ban(player_id)

    async def test_commands_remove_permanent_ban(self) -> None:
        player_id = "pid"
        await RconCommandsStub(
            "RemovePermanentBan",
            2,
            {"PlayerId": player_id},
        ).remove_permanent_ban(player_id)

    async def test_commands_remove_ban(self) -> None:
        commands = mock.Mock(spec=RconCommands)
        commands.remove_ban = partial(RconCommands.unban_player, commands)
        await commands.remove_ban("pid")
        commands.remove_temporary_ban.assert_called_once_with("pid")
        commands.remove_permanent_ban.assert_called_once_with("pid")

    async def test_commands_remove_player_from_squad(self) -> None:
        player_id = "pid"
        reason = "Squad disbanded"
        await RconCommandsStub(
            "RemovePlayerFromPlatoon",
            2,
            {
                "PlayerId": player_id,
                "Reason": reason,
            },
        ).remove_player_from_squad(player_id, reason)

    async def test_commands_set_auto_balance_enabled(self) -> None:
        await RconCommandsStub(
            "SetAutoBalanceEnabled",
            2,
            {"Enable": True},
        ).set_auto_balance_enabled(enabled=True)

    async def test_commands_set_auto_balance_threshold(self) -> None:
        threshold = 5
        await RconCommandsStub(
            "SetAutoBalanceThreshold",
            2,
            {"AutoBalanceThreshold": threshold},
        ).set_auto_balance_threshold(threshold)

    async def test_commands_set_vote_kick_enabled(self) -> None:
        await RconCommandsStub(
            "SetVoteKickEnabled",
            2,
            {"Enable": True},
        ).set_vote_kick_enabled(enabled=True)

    async def test_commands_reset_vote_kick_thresholds(self) -> None:
        await RconCommandsStub(
            "ResetVoteKickThreshold",
            2,
        ).reset_vote_kick_thresholds()

    async def test_commands_set_vote_kick_thresholds(self) -> None:
        thresholds = [(10, 2), (20, 3)]
        await RconCommandsStub(
            "SetVoteKickThreshold",
            2,
            {"ThresholdValue": "10,2,20,3"},
        ).set_vote_kick_thresholds(thresholds)

    async def test_commands_add_banned_words(self) -> None:
        words = ["badword1", "badword2"]
        await RconCommandsStub(
            "AddBannedWords",
            2,
            {"Words": ",".join(words)},
        ).add_banned_words(words)

    async def test_commands_remove_banned_words(self) -> None:
        words = ["badword1", "badword2"]
        await RconCommandsStub(
            "RemoveBannedWords",
            2,
            {"Words": ",".join(words)},
        ).remove_banned_words(words)

    async def test_commands_add_vip(self) -> None:
        player_id = "vip123"
        description = "desc"
        await RconCommandsStub(
            "AddVip",
            2,
            {"PlayerId": player_id, "Description": description},
        ).add_vip(player_id, description)

    async def test_commands_remove_vip(self) -> None:
        player_id = "vip123"
        await RconCommandsStub(
            "RemoveVip",
            2,
            {"PlayerId": player_id},
        ).remove_vip(player_id)

    async def test_commands_set_num_vip_slots(self) -> None:
        num_slots = 5
        await RconCommandsStub(
            "SetVipSlotCount",
            2,
            {"VipSlotCount": num_slots},
        ).set_num_vip_slots(num_slots)

    async def test_commands_set_match_timer(self) -> None:
        game_mode: Literal["Warfare"] = "Warfare"
        minutes = 30
        await RconCommandsStub(
            "SetMatchTimer",
            2,
            {"GameMode": game_mode, "MatchLength": minutes},
        ).set_match_timer(game_mode, minutes)

    async def test_commands_remove_match_timer(self) -> None:
        game_mode: Literal["Warfare"] = "Warfare"
        await RconCommandsStub(
            "RemoveMatchTimer",
            2,
            {"GameMode": game_mode},
        ).reset_match_timer(game_mode)

    async def test_commands_set_warmup_timer(self) -> None:
        game_mode: Literal["Warfare"] = "Warfare"
        minutes = 5
        await RconCommandsStub(
            "SetWarmupTimer",
            2,
            {"GameMode": game_mode, "WarmupLength": minutes},
        ).set_warmup_timer(game_mode, minutes)

    async def test_commands_remove_warmup_timer(self) -> None:
        game_mode: Literal["Warfare"] = "Warfare"
        await RconCommandsStub(
            "RemoveWarmupTimer",
            2,
            {"GameMode": game_mode},
        ).remove_warmup_timer(game_mode)

    async def test_commands_set_dynamic_weather_enabled(self) -> None:
        map_id = "map123"
        enabled = True
        await RconCommandsStub(
            "SetDynamicWeatherEnabled",
            2,
            {"MapId": map_id, "Enable": enabled},
        ).set_dynamic_weather_enabled(map_id, enabled=enabled)
