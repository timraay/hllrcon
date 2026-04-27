from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any, cast

import pytest
from hllrcon.data import HLLGameMode, HLLLayer, HLLRole
from hllrcon.data.game_modes import HLLVGameMode
from hllrcon.responses import (
    EmptyStringToNoneValidator,
    HLLGetAdminLogResponseEntry,
    HLLGetMapRotationResponseEntry,
    HLLGetPlayerResponse,
    HLLGetServerSessionResponse,
    HLLPlayerFactionId,
    HLLPlayerPlatform,
    HLLPlayerRoleId,
    HLLVGetMapRotationResponseEntry,
)

if TYPE_CHECKING:
    from collections.abc import Callable


def test_empty_string_to_none_validator() -> None:
    validator_func = cast("Callable[[Any], Any]", EmptyStringToNoneValidator.func)

    # Test with an empty string
    assert validator_func("") is None

    # Test with a non-empty string
    assert validator_func("Test") == "Test"

    # Test with None
    assert validator_func(None) is None


def test_get_admin_log_response_convert_isoformat_to_datetime() -> None:
    entry = HLLGetAdminLogResponseEntry.model_validate(
        {
            "timestamp": "2023-03-15T12:34:56.789Z",
            "message": "Test log entry",
        },
    )
    assert entry.timestamp == datetime(2023, 3, 15, 12, 34, 56, 789000, tzinfo=UTC)


def test_get_player_response_team_unassigned() -> None:
    response = HLLGetPlayerResponse.model_validate(
        {
            "name": "TestPlayer",
            "clanTag": "",
            "iD": "12345",
            "platform": HLLPlayerPlatform.STEAM.value,
            "eosId": "eos-12345",
            "level": 10,
            "team": HLLPlayerFactionId.UNASSIGNED.value,
            "role": HLLPlayerRoleId.RIFLEMAN.value,
            "platoon": "",
            "loadout": "Standard Issue",
            "stats": {
                "deaths": 50,
                "infantryKills": 150,
                "vehicleKills": 20,
                "teamKills": 5,
                "vehiclesDestroyed": 3,
            },
            "scoreData": {
                "cOMBAT": 100,
                "offense": 50,
                "defense": 30,
                "support": 20,
            },
            "worldPosition": {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
            },
        },
    )

    assert response.faction is None
    assert response.role is HLLRole.RIFLEMAN

    # Test other validators just for the sake of it
    assert response.clan_tag is None
    assert response.platoon is None


def test_get_server_session_game_mode_and_layer() -> None:
    response = HLLGetServerSessionResponse(
        server_name="Test Server",
        map_name="FOY",
        map_id="foy_warfare",
        game_mode_id="Warfare",
        remaining_match_time=timedelta(seconds=300),
        match_time=600,
        allied_score=2,
        axis_score=3,
        player_count=64,
        allied_player_count=32,
        axis_player_count=32,
        max_player_count=100,
        queue_count=0,
        max_queue_count=6,
        vip_queue_count=0,
        max_vip_queue_count=6,
    )
    assert response.game_mode == HLLGameMode.WARFARE
    assert response.find_layer() == HLLLayer.FOY_WARFARE_DAY


def test_map_rotation_entry_find_layer() -> None:
    entry = HLLGetMapRotationResponseEntry(
        name="FOY",
        game_mode_name="Warfare",
        time_of_day="DAY",
        id="foy_warfare",
        position=0,
    )
    assert entry.game_mode == HLLGameMode.WARFARE
    assert entry.find_layer() == HLLLayer.FOY_WARFARE_DAY

    entry.game_mode_name = "Control Skirmish - La Petite Chapelle"
    assert entry.game_mode == HLLGameMode.SKIRMISH

    entry.game_mode_name = "U.S. Offensive"
    assert entry.game_mode == HLLGameMode.OFFENSIVE

    hllv_entry = HLLVGetMapRotationResponseEntry(
        name="FOY",
        game_mode_name="Warfare",
        time_of_day="DAY",
        id="foy_warfare",
        position=0,
    )
    assert hllv_entry.game_mode == HLLVGameMode.WARFARE

    hllv_entry.game_mode_name = "Control Skirmish - La Petite Chapelle"
    assert hllv_entry.game_mode == HLLVGameMode.SKIRMISH

    hllv_entry.game_mode_name = "U.S. Offensive"
    assert hllv_entry.game_mode == HLLVGameMode.OFFENSIVE

    unknown_entry = HLLGetMapRotationResponseEntry(
        name="SOY",
        game_mode_name="Offensive",
        time_of_day="DAY",
        id="not_foy_warfare",
        position=1,
    )
    assert unknown_entry.game_mode == HLLGameMode.OFFENSIVE
    with pytest.raises(ValueError, match="not found"):
        unknown_entry.find_layer()
