from datetime import UTC, datetime

import pytest
from hllrcon.admin_logs import (
    AdminLog,
    MatchEndAdminLog,
    MatchStartAdminLog,
    PlayerBanAdminLog,
    PlayerConnectAdminLog,
    PlayerDisconnectAdminLog,
    PlayerEnterAdminCameraAdminLog,
    PlayerKickAdminLog,
    PlayerKillAdminLog,
    PlayerLeaveAdminCameraAdminLog,
    PlayerReceiveMessageAdminLog,
    PlayerSendMessageAdminLog,
    PlayerTeamKillAdminLog,
    UnrecognizedAdminLog,
)


def test_admin_log_invalid_line() -> None:
    log_line = "Not a valid log!"
    with pytest.raises(ValueError, match=r"Invalid log line: Not a valid log!"):
        AdminLog.parse(log_line)


def test_admin_log_unrecognized_line() -> None:
    raw_message = "Not a recognized log!"
    log_line = f"[2024-06-01 12:00:00 (1712345678)] {raw_message}"
    log = AdminLog.parse(log_line)
    assert isinstance(log, UnrecognizedAdminLog)
    assert log.raw_message == raw_message


def test_admin_log_timestamp() -> None:
    log_line = "[2024-06-01 12:00:00 (1712345678)] Blah"
    log = AdminLog.parse(log_line)
    assert log.timestamp == datetime.fromtimestamp(1712345678, tz=UTC)


def test_admin_log_child_parse_parent() -> None:
    raw_message = (
        "KILL: Player One(Allies/12345678901234567) -> "
        "Player Two(Axis/12345678901234568) with Rifle"
    )
    log_line = f"[2024-06-01 12:00:00 (1712345678)] {raw_message}"
    log = PlayerConnectAdminLog.parse(log_line)
    assert isinstance(log, UnrecognizedAdminLog)
    assert log.raw_message == raw_message


class TestAdminLogParse:
    @pytest.mark.parametrize(
        "log_cls",
        [AdminLog, PlayerConnectAdminLog],
    )
    def test_parse_player_connect(self, log_cls: type[AdminLog]) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "CONNECTED Player One (12345678901234567)"
        )
        log = log_cls.parse(log_line)
        assert isinstance(log, PlayerConnectAdminLog)
        assert log.player_name == "Player One"
        assert log.player_id == "12345678901234567"

    @pytest.mark.parametrize(
        "log_cls",
        [AdminLog, PlayerDisconnectAdminLog],
    )
    def test_parse_player_disconnect(self, log_cls: type[AdminLog]) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "DISCONNECTED Player One (12345678901234567)"
        )
        log = log_cls.parse(log_line)
        assert isinstance(log, PlayerDisconnectAdminLog)
        assert log.player_name == "Player One"
        assert log.player_id == "12345678901234567"

    @pytest.mark.parametrize(
        "log_cls",
        [AdminLog, PlayerKillAdminLog],
    )
    def test_parse_player_kill(self, log_cls: type[AdminLog]) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "KILL: Player One(Allies/12345678901234567) -> "
            "Player Two(Axis/12345678901234568) with Rifle"
        )
        log = log_cls.parse(log_line)
        assert isinstance(log, PlayerKillAdminLog)
        assert log.instigator_name == "Player One"
        assert log.instigator_team_name == "Allies"
        assert log.instigator_id == "12345678901234567"
        assert log.victim_name == "Player Two"
        assert log.victim_team_name == "Axis"
        assert log.victim_id == "12345678901234568"
        assert log.weapon == "Rifle"

    @pytest.mark.parametrize(
        "log_cls",
        [AdminLog, PlayerTeamKillAdminLog],
    )
    def test_parse_player_team_kill(self, log_cls: type[AdminLog]) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "TEAM KILL: Player One(Allies/12345678901234567) -> "
            "Player Two(Allies/12345678901234568) with Grenade"
        )
        log = log_cls.parse(log_line)
        assert isinstance(log, PlayerTeamKillAdminLog)
        assert log.instigator_name == "Player One"
        assert log.instigator_team_name == "Allies"
        assert log.instigator_id == "12345678901234567"
        assert log.victim_name == "Player Two"
        assert log.victim_team_name == "Allies"
        assert log.victim_id == "12345678901234568"
        assert log.weapon == "Grenade"

    @pytest.mark.parametrize(
        "log_cls",
        [AdminLog, PlayerSendMessageAdminLog],
    )
    def test_parse_player_send_message(self, log_cls: type[AdminLog]) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "CHAT[Team][Player One(Allies/12345678901234567)]: Hello team!"
        )
        log = log_cls.parse(log_line)
        assert isinstance(log, PlayerSendMessageAdminLog)
        assert log.channel == "Team"
        assert log.player_name == "Player One"
        assert log.player_team_name == "Allies"
        assert log.player_id == "12345678901234567"
        assert log.message == "Hello team!"

    @pytest.mark.parametrize(
        "log_cls",
        [AdminLog, PlayerReceiveMessageAdminLog],
    )
    def test_parse_player_receive_message(self, log_cls: type[AdminLog]) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "MESSAGE: player [Player One], content [Hello!]"
        )
        log = log_cls.parse(log_line)
        assert isinstance(log, PlayerReceiveMessageAdminLog)
        assert log.player_name == "Player One"
        assert log.message == "Hello!"

    @pytest.mark.parametrize(
        "log_cls",
        [AdminLog, PlayerEnterAdminCameraAdminLog],
    )
    def test_parse_player_enter_admin_camera(self, log_cls: type[AdminLog]) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "Player [Player One (12345678901234567)] Entered Admin Camera"
        )
        log = log_cls.parse(log_line)
        assert isinstance(log, PlayerEnterAdminCameraAdminLog)
        assert log.player_name == "Player One"
        assert log.player_id == "12345678901234567"

    @pytest.mark.parametrize(
        "log_cls",
        [AdminLog, PlayerLeaveAdminCameraAdminLog],
    )
    def test_parse_player_leave_admin_camera(self, log_cls: type[AdminLog]) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "Player [Player One (12345678901234567)] Left Admin Camera"
        )
        log = log_cls.parse(log_line)
        assert isinstance(log, PlayerLeaveAdminCameraAdminLog)
        assert log.player_name == "Player One"
        assert log.player_id == "12345678901234567"

    @pytest.mark.parametrize(
        "log_cls",
        [AdminLog, PlayerKickAdminLog],
    )
    def test_parse_player_kick_admin_log(self, log_cls: type[AdminLog]) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "KICK: [Player One] has been kicked. [Reason: Spamming]"
        )
        log = log_cls.parse(log_line)
        assert isinstance(log, PlayerKickAdminLog)
        assert log.player_name == "Player One"
        assert log.reason == "Reason: Spamming"

    @pytest.mark.parametrize(
        "log_cls",
        [AdminLog, PlayerBanAdminLog],
    )
    def test_parse_player_ban_admin_log(self, log_cls: type[AdminLog]) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "BAN: [Player One] has been banned. [Reason: Cheating]"
        )
        log = log_cls.parse(log_line)
        assert isinstance(log, PlayerBanAdminLog)
        assert log.player_name == "Player One"
        assert log.reason == "Reason: Cheating"

    @pytest.mark.parametrize(
        "log_cls",
        [AdminLog, MatchStartAdminLog],
    )
    def test_parse_match_start(self, log_cls: type[AdminLog]) -> None:
        log_line = "[2024-06-01 12:00:00 (1712345678)] MATCH START Some Map"
        log = log_cls.parse(log_line)
        assert isinstance(log, MatchStartAdminLog)
        assert log.map_name == "Some Map"

    @pytest.mark.parametrize(
        "log_cls",
        [AdminLog, MatchEndAdminLog],
    )
    def test_parse_match_end(self, log_cls: type[AdminLog]) -> None:
        log_line = (
            "[2024-06-01 12:00:00 (1712345678)] "
            "MATCH ENDED `Some Map` ALLIED (3 - 2) AXIS"
        )
        log = log_cls.parse(log_line)
        assert isinstance(log, MatchEndAdminLog)
        assert log.map_name == "Some Map"
        assert log.allied_score == 3
        assert log.axis_score == 2
