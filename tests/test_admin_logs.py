from datetime import UTC, datetime
from typing import ClassVar, cast

import pytest
from hllrcon.admin_logs import (
    AnyAdminLog,
    AnyMatchEndAdminLog,
    AnyMatchStartAdminLog,
    AnyPlayerBanAdminLog,
    AnyPlayerConnectAdminLog,
    AnyPlayerDisconnectAdminLog,
    AnyPlayerEnterAdminCameraAdminLog,
    AnyPlayerKickAdminLog,
    AnyPlayerKillAdminLog,
    AnyPlayerLeaveAdminCameraAdminLog,
    AnyPlayerReceiveMessageAdminLog,
    AnyPlayerSendMessageAdminLog,
    AnyPlayerTeamKillAdminLog,
    AnyPlayerTeamSwitchAdminLog,
    AnyVoteKickCompleteAdminLog,
    AnyVoteKickExpireAdminLog,
    AnyVoteKickPassAdminLog,
    AnyVoteKickStartAdminLog,
    AnyVoteKickVoteAdminLog,
    HLLAdminLog,
    HLLMatchEndAdminLog,
    HLLMatchStartAdminLog,
    HLLPlayerBanAdminLog,
    HLLPlayerConnectAdminLog,
    HLLPlayerDisconnectAdminLog,
    HLLPlayerEnterAdminCameraAdminLog,
    HLLPlayerKickAdminLog,
    HLLPlayerKillAdminLog,
    HLLPlayerLeaveAdminCameraAdminLog,
    HLLPlayerReceiveMessageAdminLog,
    HLLPlayerSendMessageAdminLog,
    HLLPlayerTeamKillAdminLog,
    HLLPlayerTeamSwitchAdminLog,
    HLLVAdminLog,
    HLLVMatchEndAdminLog,
    HLLVMatchStartAdminLog,
    HLLVoteKickCompleteAdminLog,
    HLLVoteKickExpireAdminLog,
    HLLVoteKickPassAdminLog,
    HLLVoteKickStartAdminLog,
    HLLVoteKickVoteAdminLog,
    HLLVPlayerBanAdminLog,
    HLLVPlayerConnectAdminLog,
    HLLVPlayerDisconnectAdminLog,
    HLLVPlayerEnterAdminCameraAdminLog,
    HLLVPlayerKickAdminLog,
    HLLVPlayerKillAdminLog,
    HLLVPlayerLeaveAdminCameraAdminLog,
    HLLVPlayerReceiveMessageAdminLog,
    HLLVPlayerSendMessageAdminLog,
    HLLVPlayerTeamKillAdminLog,
    HLLVPlayerTeamSwitchAdminLog,
    HLLVVoteKickCompleteAdminLog,
    HLLVVoteKickExpireAdminLog,
    HLLVVoteKickPassAdminLog,
    HLLVVoteKickStartAdminLog,
    HLLVVoteKickVoteAdminLog,
    UnrecognizedAdminLog,
    VoteKickResult,
    VoteKickVoteType,
    _AdminLog,
    _map_from_name,
    _team_from_name,
)
from hllrcon.data.game_modes import AnyGameMode, HLLGameMode, HLLVGameMode
from hllrcon.data.maps import AnyMap, HLLMap, HLLVMap
from hllrcon.data.teams import AnyTeam, HLLTeam, HLLVTeam
from hllrcon.data.weapons import AnyWeapon, HLLVWeapon, HLLWeapon
from pydantic import BaseModel


def test_admin_log_invalid_line() -> None:
    log_line = "Not a valid log!"
    with pytest.raises(ValueError, match=r"Invalid log line: Not a valid log!"):
        _AdminLog.parse(log_line)


def test_admin_log_unrecognized_line() -> None:
    raw_message = "Not a recognized log!"
    log_line = f"[2024-06-01 12:00:00 (1712345678)] {raw_message}"
    log = _AdminLog.parse(log_line)
    assert isinstance(log, UnrecognizedAdminLog)
    assert log.raw_message == raw_message


def test_admin_log_validation_error_line() -> None:
    # "Blah" is not a valid instance of "VoteKickResult"
    raw_message = "VOTESYS: Vote [1] completed. Result: Blah"
    log_line = f"[2024-06-01 12:00:00 (1712345678)] {raw_message}"
    log = _AdminLog.parse(log_line)
    assert isinstance(log, UnrecognizedAdminLog)
    assert log.raw_message == raw_message


def test_admin_log_timestamp() -> None:
    log_line = "[2024-06-01 12:00:00 (1712345678)] Blah"
    log = _AdminLog.parse(log_line)
    assert log.timestamp == datetime.fromtimestamp(1712345678, tz=UTC)


def test_admin_log_child_parse_parent() -> None:
    raw_message = (
        "KILL: Player One(Allies/12345678901234567) -> "
        "Player Two(Axis/12345678901234568) with Rifle"
    )
    log_line = f"[2024-06-01 12:00:00 (1712345678)] {raw_message}"
    log = HLLPlayerConnectAdminLog.parse(log_line)
    assert isinstance(log, UnrecognizedAdminLog)
    assert log.raw_message == raw_message


class AdminLogTypes(BaseModel, frozen=True):
    base: type[AnyAdminLog]
    player_connect: type[AnyPlayerConnectAdminLog]
    player_disconnect: type[AnyPlayerDisconnectAdminLog]
    player_kill: type[AnyPlayerKillAdminLog]
    player_team_kill: type[AnyPlayerTeamKillAdminLog]
    player_send_message: type[AnyPlayerSendMessageAdminLog]
    player_receive_message: type[AnyPlayerReceiveMessageAdminLog]
    player_enter_admin_camera: type[AnyPlayerEnterAdminCameraAdminLog]
    player_leave_admin_camera: type[AnyPlayerLeaveAdminCameraAdminLog]
    player_kick: type[AnyPlayerKickAdminLog]
    player_ban: type[AnyPlayerBanAdminLog]
    player_team_switch: type[AnyPlayerTeamSwitchAdminLog]
    match_start: type[AnyMatchStartAdminLog]
    match_end: type[AnyMatchEndAdminLog]
    vote_kick_start: type[AnyVoteKickStartAdminLog]
    vote_kick_vote: type[AnyVoteKickVoteAdminLog]
    vote_kick_complete: type[AnyVoteKickCompleteAdminLog]
    vote_kick_expire: type[AnyVoteKickExpireAdminLog]
    vote_kick_pass: type[AnyVoteKickPassAdminLog]


class DataModelTypes(BaseModel, frozen=True):
    weapon: type[AnyWeapon]
    team: type[AnyTeam]
    map: type[AnyMap]
    game_mode: type[AnyGameMode]


class _TestAdminLogParse:
    log_types: ClassVar[AdminLogTypes]
    model_types: ClassVar[DataModelTypes]

    def test_parse_player_connect(self) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "CONNECTED Player One (12345678901234567)"
        )
        log = cast("AnyPlayerConnectAdminLog", self.log_types.base.parse(log_line))
        assert isinstance(log, self.log_types.player_connect)
        assert log.player_name == "Player One"
        assert log.player_id == "12345678901234567"

    def test_parse_player_disconnect(self) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "DISCONNECTED Player One (12345678901234567)"
        )
        log = cast("AnyPlayerDisconnectAdminLog", self.log_types.base.parse(log_line))
        assert isinstance(log, self.log_types.player_disconnect)
        assert log.player_name == "Player One"
        assert log.player_id == "12345678901234567"

    def test_parse_player_kill(self) -> None:
        weapon = self.model_types.weapon.all()[0]
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "KILL: Player One(Allies/12345678901234567) -> "
            f"Player Two(Axis/12345678901234568) with {weapon.id}"
        )
        log = cast("AnyPlayerKillAdminLog", self.log_types.base.parse(log_line))
        assert isinstance(log, self.log_types.player_kill)
        assert log.instigator_name == "Player One"
        assert log.instigator_team_name == "Allies"
        assert log.instigator_id == "12345678901234567"
        assert log.victim_name == "Player Two"
        assert log.victim_team_name == "Axis"
        assert log.victim_id == "12345678901234568"
        assert log.weapon_id == weapon.id
        assert log.get_weapon() == weapon
        assert log.get_instigator_team() == self.model_types.team.ALLIES
        assert log.get_victim_team() == self.model_types.team.AXIS

    def test_parse_player_team_kill(self) -> None:
        weapon = self.model_types.weapon.all()[0]
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "TEAM KILL: Player One(Allies/12345678901234567) -> "
            f"Player Two(Allies/12345678901234568) with {weapon.id}"
        )
        log = cast("AnyPlayerTeamKillAdminLog", self.log_types.base.parse(log_line))
        assert isinstance(log, self.log_types.player_team_kill)
        assert log.instigator_name == "Player One"
        assert log.instigator_team_name == "Allies"
        assert log.instigator_id == "12345678901234567"
        assert log.victim_name == "Player Two"
        assert log.victim_team_name == "Allies"
        assert log.victim_id == "12345678901234568"
        assert log.weapon_id == weapon.id
        assert log.get_weapon() == weapon
        assert log.get_instigator_team() == self.model_types.team.ALLIES
        assert log.get_victim_team() == self.model_types.team.ALLIES

    def test_parse_player_send_message(self) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "CHAT[Team][Player One(Allies/12345678901234567)]: Hello team!"
        )
        log = cast("AnyPlayerSendMessageAdminLog", self.log_types.base.parse(log_line))
        assert isinstance(log, self.log_types.player_send_message)
        assert log.channel == "Team"
        assert log.player_name == "Player One"
        assert log.player_team_name == "Allies"
        assert log.player_id == "12345678901234567"
        assert log.message == "Hello team!"
        assert log.get_player_team() == self.model_types.team.ALLIES

    def test_parse_player_receive_message(self) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "MESSAGE: player [Player One], content [Hello!]"
        )
        log = cast(
            "AnyPlayerReceiveMessageAdminLog",
            self.log_types.base.parse(log_line),
        )
        assert isinstance(log, self.log_types.player_receive_message)
        assert log.player_name == "Player One"
        assert log.message == "Hello!"

    def test_parse_player_enter_admin_camera(self) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "Player [Player One (12345678901234567)] Entered Admin Camera"
        )
        log = cast(
            "AnyPlayerEnterAdminCameraAdminLog",
            self.log_types.base.parse(log_line),
        )
        assert isinstance(log, self.log_types.player_enter_admin_camera)
        assert log.player_name == "Player One"
        assert log.player_id == "12345678901234567"

    def test_parse_player_leave_admin_camera(self) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "Player [Player One (12345678901234567)] Left Admin Camera"
        )
        log = cast(
            "AnyPlayerLeaveAdminCameraAdminLog",
            self.log_types.base.parse(log_line),
        )
        assert isinstance(log, self.log_types.player_leave_admin_camera)
        assert log.player_name == "Player One"
        assert log.player_id == "12345678901234567"

    def test_parse_player_kick_admin_log(self) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "KICK: [Player One] has been kicked. [Reason: Spamming]"
        )
        log = cast("AnyPlayerKickAdminLog", self.log_types.base.parse(log_line))
        assert isinstance(log, self.log_types.player_kick)
        assert log.player_name == "Player One"
        assert log.reason == "Reason: Spamming"

    def test_parse_player_ban_admin_log(self) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "BAN: [Player One] has been banned. [Reason: Cheating]"
        )
        log = cast("AnyPlayerBanAdminLog", self.log_types.base.parse(log_line))
        assert isinstance(log, self.log_types.player_ban)
        assert log.player_name == "Player One"
        assert log.reason == "Reason: Cheating"

    def test_parse_player_team_switch(self) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] TEAMSWITCH Player One (Allies > Axis)"
        )
        log = cast("AnyPlayerTeamSwitchAdminLog", self.log_types.base.parse(log_line))
        assert isinstance(log, self.log_types.player_team_switch)
        assert log.player_name == "Player One"
        assert log.old_team_name == "Allies"
        assert log.new_team_name == "Axis"
        assert log.get_old_team() == self.model_types.team.ALLIES
        assert log.get_new_team() == self.model_types.team.AXIS

    def test_parse_player_team_switch_no_team(self) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] TEAMSWITCH Player One (None > None)"
        )
        log = cast("AnyPlayerTeamSwitchAdminLog", self.log_types.base.parse(log_line))
        assert isinstance(log, self.log_types.player_team_switch)
        assert log.player_name == "Player One"
        assert log.old_team_name == "None"
        assert log.new_team_name == "None"
        assert log.get_old_team() is None
        assert log.get_new_team() is None

    def test_parse_match_start(self) -> None:
        map_ = self.model_types.map.all()[0]
        log_line = f"[2024-06-01 12:00:00 (1712345678)] MATCH START {map_.name} Warfare"
        log = cast("AnyMatchStartAdminLog", self.log_types.base.parse(log_line))
        assert isinstance(log, self.log_types.match_start)
        assert log.map_name == map_.name
        assert log.game_mode_id == "Warfare"
        assert log.get_map() == map_
        assert log.get_game_mode() == self.model_types.game_mode.WARFARE

    def test_parse_match_end(self) -> None:
        map_ = self.model_types.map.all()[0]
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            f"MATCH ENDED `{map_.name} Warfare` ALLIED (3 - 2) AXIS"
        )
        log = cast("AnyMatchEndAdminLog", self.log_types.base.parse(log_line))
        assert isinstance(log, self.log_types.match_end)
        assert log.map_name == map_.name
        assert log.game_mode_id == "Warfare"
        assert log.allied_score == 3
        assert log.axis_score == 2
        assert log.get_map() == map_
        assert log.get_game_mode() == self.model_types.game_mode.WARFARE

    def test_parse_vote_kick_start(self) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "VOTESYS: Player [Player One] Started a vote of type (PVR_Kick_Abuse) "
            "against [Player Two]. VoteID: [2]"
        )
        log = cast("AnyVoteKickStartAdminLog", self.log_types.base.parse(log_line))
        assert isinstance(log, self.log_types.vote_kick_start)
        assert log.initiator_name == "Player One"
        assert log.target_name == "Player Two"
        assert log.vote_id == 2

    def test_parse_vote_kick_vote(self) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "VOTESYS: Player [Player One] voted [PV_Favour] for VoteID[2]"
        )
        log = cast("AnyVoteKickVoteAdminLog", self.log_types.base.parse(log_line))
        assert isinstance(log, self.log_types.vote_kick_vote)
        assert log.player_name == "Player One"
        assert log.vote_id == 2
        assert log.vote_type == VoteKickVoteType.IN_FAVOUR

    def test_parse_vote_kick_complete(self) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "VOTESYS: Vote [2] completed. Result: PVR_Passed"
        )
        log = cast("AnyVoteKickCompleteAdminLog", self.log_types.base.parse(log_line))
        assert isinstance(log, self.log_types.vote_kick_complete)
        assert log.vote_id == 2
        assert log.result == VoteKickResult.PASSED

    def test_parse_vote_kick_expire(self) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "VOTESYS: Vote [1] expired before completion."
        )
        log = cast("AnyVoteKickExpireAdminLog", self.log_types.base.parse(log_line))
        assert isinstance(log, self.log_types.vote_kick_expire)
        assert log.vote_id == 1
        assert log.prematurely is False

    def test_parse_vote_kick_expire_prematurely(self) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] VOTESYS: Vote [1] prematurely expired."
        )
        log = cast("AnyVoteKickExpireAdminLog", self.log_types.base.parse(log_line))
        assert isinstance(log, self.log_types.vote_kick_expire)
        assert log.vote_id == 1
        assert log.prematurely is True

    def test_parse_vote_kick_pass(self) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "VOTESYS: Vote Kick {Player One} successfully passed."
            " [For: 2/1 - Against: 0]"
        )
        log = cast("AnyVoteKickPassAdminLog", self.log_types.base.parse(log_line))
        assert isinstance(log, self.log_types.vote_kick_pass)
        assert log.target_name == "Player One"
        assert log.num_votes_in_favour == 2
        assert log.num_votes_required == 1
        assert log.num_votes_against == 0


class TestHLLAdminLogParse(_TestAdminLogParse):
    log_types = AdminLogTypes(
        base=HLLAdminLog,
        player_connect=HLLPlayerConnectAdminLog,
        player_disconnect=HLLPlayerDisconnectAdminLog,
        player_kill=HLLPlayerKillAdminLog,
        player_team_kill=HLLPlayerTeamKillAdminLog,
        player_send_message=HLLPlayerSendMessageAdminLog,
        player_receive_message=HLLPlayerReceiveMessageAdminLog,
        player_enter_admin_camera=HLLPlayerEnterAdminCameraAdminLog,
        player_leave_admin_camera=HLLPlayerLeaveAdminCameraAdminLog,
        player_kick=HLLPlayerKickAdminLog,
        player_ban=HLLPlayerBanAdminLog,
        player_team_switch=HLLPlayerTeamSwitchAdminLog,
        match_start=HLLMatchStartAdminLog,
        match_end=HLLMatchEndAdminLog,
        vote_kick_start=HLLVoteKickStartAdminLog,
        vote_kick_vote=HLLVoteKickVoteAdminLog,
        vote_kick_complete=HLLVoteKickCompleteAdminLog,
        vote_kick_expire=HLLVoteKickExpireAdminLog,
        vote_kick_pass=HLLVoteKickPassAdminLog,
    )
    model_types = DataModelTypes(
        weapon=HLLWeapon,
        team=HLLTeam,
        map=HLLMap,
        game_mode=HLLGameMode,
    )


class TestHLLVAdminLogParse(_TestAdminLogParse):
    log_types = AdminLogTypes(
        base=HLLVAdminLog,
        player_connect=HLLVPlayerConnectAdminLog,
        player_disconnect=HLLVPlayerDisconnectAdminLog,
        player_kill=HLLVPlayerKillAdminLog,
        player_team_kill=HLLVPlayerTeamKillAdminLog,
        player_send_message=HLLVPlayerSendMessageAdminLog,
        player_receive_message=HLLVPlayerReceiveMessageAdminLog,
        player_enter_admin_camera=HLLVPlayerEnterAdminCameraAdminLog,
        player_leave_admin_camera=HLLVPlayerLeaveAdminCameraAdminLog,
        player_kick=HLLVPlayerKickAdminLog,
        player_ban=HLLVPlayerBanAdminLog,
        player_team_switch=HLLVPlayerTeamSwitchAdminLog,
        match_start=HLLVMatchStartAdminLog,
        match_end=HLLVMatchEndAdminLog,
        vote_kick_start=HLLVVoteKickStartAdminLog,
        vote_kick_vote=HLLVVoteKickVoteAdminLog,
        vote_kick_complete=HLLVVoteKickCompleteAdminLog,
        vote_kick_expire=HLLVVoteKickExpireAdminLog,
        vote_kick_pass=HLLVVoteKickPassAdminLog,
    )
    model_types = DataModelTypes(
        weapon=HLLVWeapon,
        team=HLLVTeam,
        map=HLLVMap,
        game_mode=HLLVGameMode,
    )


def test_helper_map_from_name() -> None:
    assert _map_from_name(HLLMap, "HÜRTGEN FOREST") == HLLMap.HURTGEN_FOREST
    with pytest.raises(ValueError, match=r"Unrecognized map name: NotAMap"):
        _map_from_name(HLLMap, "NotAMap")


def test_helper_team_from_name() -> None:
    assert _team_from_name(HLLTeam, "Allies") == HLLTeam.ALLIES
    assert _team_from_name(HLLTeam, "Axis") == HLLTeam.AXIS
    with pytest.raises(ValueError, match=r"Unrecognized team name: NotATeam"):
        _team_from_name(HLLTeam, "NotATeam")
