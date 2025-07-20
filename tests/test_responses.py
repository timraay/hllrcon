from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, NamedTuple, cast

import pytest
from hllrcon.data import layers
from hllrcon.responses import (
    EmptyStringToNoneValidator,
    GetAdminLogResponseEntry,
    GetMapRotationResponseEntry,
    GetPlayerResponse,
    PlayerPlatform,
    PlayerRole,
    PlayerTeam,
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
    entry = GetAdminLogResponseEntry.model_validate(
        {
            "timestamp": "2023-03-15T12:34:56.789Z",
            "message": "Test log entry",
        },
    )
    assert entry.timestamp == datetime(2023, 3, 15, 12, 34, 56, 789000, tzinfo=UTC)


def test_get_player_response_team_unassigned() -> None:
    response = GetPlayerResponse.model_validate(
        {
            "name": "TestPlayer",
            "clanTag": "",
            "iD": "12345",
            "platform": PlayerPlatform.STEAM.value,
            "eosId": "eos-12345",
            "level": 10,
            "team": PlayerTeam.UNASSIGNED.value,
            "role": PlayerRole.Rifleman.value,
            "platoon": "",
            "loadout": "Standard Issue",
            "kills": 5,
            "deaths": 2,
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

    assert response.team is None

    # Test other validators just for the sake of it
    assert response.clan_tag is None
    assert response.platoon is None


class PlayerRoleProperties(NamedTuple):
    role: PlayerRole
    is_infantry: bool
    is_tanker: bool
    is_recon: bool
    is_squad_leader: bool


@pytest.mark.parametrize(
    "properties",
    [
        PlayerRoleProperties(PlayerRole.Rifleman, True, False, False, False),
        PlayerRoleProperties(PlayerRole.Assault, True, False, False, False),
        PlayerRoleProperties(PlayerRole.AutomaticRifleman, True, False, False, False),
        PlayerRoleProperties(PlayerRole.Medic, True, False, False, False),
        PlayerRoleProperties(PlayerRole.Spotter, False, False, True, True),
        PlayerRoleProperties(PlayerRole.Support, True, False, False, False),
        PlayerRoleProperties(PlayerRole.MachineGunner, True, False, False, False),
        PlayerRoleProperties(PlayerRole.AntiTank, True, False, False, False),
        PlayerRoleProperties(PlayerRole.Engineer, True, False, False, False),
        PlayerRoleProperties(PlayerRole.Officer, True, False, False, True),
        PlayerRoleProperties(PlayerRole.Sniper, False, False, True, False),
        PlayerRoleProperties(PlayerRole.Crewman, False, True, False, False),
        PlayerRoleProperties(PlayerRole.TankCommander, False, True, False, True),
        PlayerRoleProperties(PlayerRole.ArmyCommander, False, False, False, True),
    ],
)
def test_player_role_types(properties: PlayerRoleProperties) -> None:
    assert properties.role.is_infantry() is properties.is_infantry
    assert properties.role.is_tanker() is properties.is_tanker
    assert properties.role.is_recon() is properties.is_recon
    assert properties.role.is_squad_leader() is properties.is_squad_leader


class PlayerTeamTypes(NamedTuple):
    team: PlayerTeam
    is_allied: bool
    is_axis: bool


@pytest.mark.parametrize(
    "properties",
    [
        PlayerTeamTypes(PlayerTeam.GER, False, True),
        PlayerTeamTypes(PlayerTeam.US, True, False),
        PlayerTeamTypes(PlayerTeam.SOV, True, False),
        PlayerTeamTypes(PlayerTeam.CW, True, False),
        PlayerTeamTypes(PlayerTeam.DAK, False, True),
        PlayerTeamTypes(PlayerTeam.B8A, True, False),
        PlayerTeamTypes(PlayerTeam.UNASSIGNED, False, False),
    ],
)
def test_player_team_types(properties: PlayerTeamTypes) -> None:
    assert properties.team.is_allied() is properties.is_allied
    assert properties.team.is_axis() is properties.is_axis


def test_map_rotation_entry_find_layer() -> None:
    entry = GetMapRotationResponseEntry(
        name="FOY",
        game_mode="Warfare",
        time_of_day="DAY",
        id="foy_warfare",
        position=0,
    )
    assert entry.find_layer() == layers.FOY_WARFARE_DAY

    unknown_entry = GetMapRotationResponseEntry(
        name="SOY",
        game_mode="Warfare",
        time_of_day="DAY",
        id="not_foy_warfare",
        position=1,
    )
    with pytest.raises(ValueError, match="not found"):
        unknown_entry.find_layer()
