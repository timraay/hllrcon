from collections.abc import Generator

import pytest
from hllrcon.data import (
    Faction,
    GameMode,
    GameModeScale,
    Layer,
    Map,
    Role,
    RoleType,
    Team,
    TimeOfDay,
    Weapon,
    Weather,
)
from hllrcon.data._utils import IndexedBaseModel, class_cached_property
from hllrcon.data.vehicles import Vehicle
from pydantic import BaseModel


@pytest.fixture(autouse=True)
def reset_lookup_maps() -> Generator[None]:
    layer_lookup_map = Layer._lookup_map.copy()
    map_lookup_map = Map._lookup_map.copy()

    yield

    Layer._lookup_map = layer_lookup_map
    Map._lookup_map = map_lookup_map


class TestDataUtils:
    def test_indexed_model(self) -> None:
        class MyModel(IndexedBaseModel[int]):
            name: str

        foo = MyModel(id=1, name="Foo")
        bar = MyModel(id=2, name="Bar")

        with pytest.raises(ValueError, match="already exists"):
            MyModel(id=2, name="Baz")

        assert MyModel.by_id(1) == foo
        assert MyModel.by_id(2) == bar

        with pytest.raises(ValueError, match="not found"):
            MyModel.by_id(3)

        assert MyModel.all() == [foo, bar]

    def test_indexed_model_resolves_properties(self) -> None:
        class MyModel(IndexedBaseModel[int]):
            @class_cached_property
            @classmethod
            def bar(cls) -> "MyModel":
                return cls(id=2)

        assert MyModel.bar.all() == [MyModel.bar]

    def test_resolve_class_cache_property(self) -> None:
        class MyModel(BaseModel, ignored_types=(class_cached_property,)):
            id: int

            @class_cached_property
            @classmethod
            def foo(cls) -> "MyModel":
                return cls(id=3)

        assert MyModel.foo is MyModel.foo
        assert MyModel.foo.id == 3


class TestDataFactions:
    def test_faction_by_id(self) -> None:
        assert Faction.by_id(0) == Faction.GER
        assert Faction.by_id(1) == Faction.US
        assert Faction.by_id(2) == Faction.SOV
        assert Faction.by_id(3) == Faction.CW
        assert Faction.by_id(4) == Faction.DAK
        assert Faction.by_id(5) == Faction.B8A
        assert Faction.by_id(6) is None

        with pytest.raises(ValueError, match="not found"):
            Faction.by_id(7)

        assert None not in Faction.all()


class TestDataGameModes:
    def test_game_mode_by_id(self) -> None:
        assert GameMode.by_id("warfare") == GameMode.WARFARE
        assert GameMode.by_id("offensive") == GameMode.OFFENSIVE
        assert GameMode.by_id("skirmish") == GameMode.SKIRMISH

        assert GameMode.by_id("wArFaRe") == GameMode.WARFARE

        with pytest.raises(ValueError, match="not found"):
            GameMode.by_id("invalid_mode")

    def test_game_mode_scale(self) -> None:
        large = GameMode(id="large", scale=GameModeScale.LARGE)
        small = GameMode(id="small", scale=GameModeScale.SMALL)

        assert large.is_large()
        assert not large.is_small()

        assert not small.is_large()
        assert small.is_small()


class TestDataLayers:
    def test_layer_by_id(self) -> None:
        assert Layer.by_id("KHA_S_1944_P_Skirmish") == Layer.KHARKOV_SKIRMISH_DAY
        assert Layer.by_id("kha_s_1944_P_SKIRMISH") == Layer.KHARKOV_SKIRMISH_DAY

        with pytest.raises(ValueError, match="not parse"):
            Layer.by_id("Not a layer", strict=False)

        with pytest.raises(ValueError, match="not found"):
            Layer.by_id("Not a layer", strict=True)

    def test_layer_str(self) -> None:
        layer = Layer.KHARKOV_SKIRMISH_DAY
        assert str(layer) == layer.id

    def test_layer_repr(self) -> None:
        layer = Layer.KHARKOV_SKIRMISH_DAY
        expected_repr = (
            f"Layer(id='KHA_S_1944_P_Skirmish', map={layer.map!r}, "
            f"attackers={layer.attacking_team!r}, time_of_day={layer.time_of_day!r}, "
            f"weather={layer.weather!r})"
        )
        assert repr(layer) == expected_repr

    def test_layer_equality(self) -> None:
        layer = Layer.KHARKOV_SKIRMISH_DAY
        assert layer == layer  # noqa: PLR0124
        assert layer == layer.id.lower()
        assert layer != Layer.KHARKOV_SKIRMISH_NIGHT
        assert layer != "Some other layer"
        assert layer != 12345

    def test_layer_hash(self) -> None:
        layer = Layer.KHARKOV_SKIRMISH_DAY
        assert hash(layer) == hash(layer.id.lower())
        assert hash(layer) != hash(Layer.KHARKOV_SKIRMISH_NIGHT)

    @pytest.mark.parametrize(
        ("layer", "name"),
        [
            (Layer.KHARKOV_SKIRMISH_DAY, "Kharkov Skirmish"),
            (Layer.DRIEL_OFFENSIVE_CW_DAY, "Driel Off. CW"),
            (Layer.MORTAIN_OFFENSIVE_GER_OVERCAST, "Mortain Off. GER (Overcast)"),
            (Layer.SMDM_SKIRMISH_RAIN, "St. Marie Du Mont Skirmish (Rain)"),
            (Layer.ALAMEIN_WARFARE_DUSK, "El Alamein Warfare (Dusk)"),
            (
                Layer.ELSENBORN_OFFENSIVE_US_DAWN,
                "Elsenborn Ridge Off. US (Dawn, Snow)",
            ),
        ],
    )
    def test_layer_pretty_name(self, layer: Layer, name: str) -> None:
        assert layer.pretty_name == name

    def test_layer_pretty_name_missing_attacking_team(self) -> None:
        layer = Layer(
            id="test_layer",
            map=Map.KHARKOV,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.OVERCAST,
            attacking_team=None,
        )
        assert layer.pretty_name == "Kharkov Off. (Overcast)"

    def test_layer_attackers(self) -> None:
        layer1 = Layer.KURSK_OFFENSIVE_SOV_DAY
        assert layer1.attacking_team == Team.ALLIES
        assert layer1.defending_team == Team.AXIS
        assert layer1.attacking_faction == Faction.SOV
        assert layer1.defending_faction == Faction.GER

        layer2 = Layer.KURSK_OFFENSIVE_GER_DAY
        assert layer2.attacking_team == Team.AXIS
        assert layer2.defending_team == Team.ALLIES
        assert layer2.attacking_faction == Faction.GER
        assert layer2.defending_faction == Faction.SOV

        layer3 = Layer.KURSK_WARFARE_DAY
        assert layer3.attacking_team is None
        assert layer3.defending_team is None
        assert layer3.attacking_faction is None
        assert layer3.defending_faction is None

    def test_layer_parse_id_small(self) -> None:
        layer = Layer.by_id("FOO_S_1942_Rain_P_Skirmish", strict=False)
        assert layer.map.id == "FOO"
        assert layer.map.tag == "FOO"
        assert layer.map.name == "Foo"
        assert layer.game_mode == GameMode.SKIRMISH
        assert layer.time_of_day == TimeOfDay.DAY
        assert layer.weather == Weather.RAIN
        assert layer.attacking_faction is None

    def test_layer_parse_id_large(self) -> None:
        layer = Layer.by_id("FOO_L_1942_OffensiveCW_Morning", strict=False)
        assert layer.map.id == "FOO"
        assert layer.map.tag == "FOO"
        assert layer.map.name == "Foo"
        assert layer.game_mode == GameMode.OFFENSIVE
        assert layer.time_of_day == TimeOfDay.DAWN
        assert layer.weather == Weather.CLEAR
        assert layer.attacking_faction == Faction.CW

    def test_layer_parse_id_legacy(self) -> None:
        layer = Layer.by_id("foo_warfare_night", strict=False)
        assert layer.map.id == "foo"
        assert layer.map.tag == "FOO"
        assert layer.map.name == "Foo"
        assert layer.game_mode == GameMode.WARFARE
        assert layer.time_of_day == TimeOfDay.NIGHT
        assert layer.weather == Weather.CLEAR
        assert layer.attacking_faction is None

    def test_layer_parse_id_legacy_offensive(self) -> None:
        layer = Layer.by_id("foo_offensive_ger", strict=False)
        assert layer.map.id == "foo"
        assert layer.map.tag == "FOO"
        assert layer.map.name == "Foo"
        assert layer.game_mode == GameMode.OFFENSIVE
        assert layer.time_of_day == TimeOfDay.DAY
        assert layer.weather == Weather.CLEAR
        assert layer.attacking_faction == Faction.GER

    def test_layer_parse_id_unknown_game_mode(self) -> None:
        with pytest.raises(ValueError, match="not parse"):
            Layer.by_id("foy_notamode", strict=False)

    def test_layer_can_parse_known_layers(self) -> None:
        all_layers = Layer.all()
        Layer._lookup_map.clear()

        for layer in all_layers:
            Map._lookup_map.clear()
            Layer._parse_id(layer.id)


class TestDataMaps:
    def test_map_by_id(self) -> None:
        assert Map.by_id("kharkov") == Map.KHARKOV
        assert Map.by_id("driel") == Map.DRIEL
        assert Map.by_id("elalamein") == Map.EL_ALAMEIN
        assert Map.by_id("mortain") == Map.MORTAIN
        assert Map.by_id("elsenbornridge") == Map.ELSENBORN_RIDGE

        assert Map.by_id("kHaRkOv") == Map.KHARKOV

        with pytest.raises(ValueError, match="not found"):
            Map.by_id("invalid_map")

    def test_map_str(self) -> None:
        map_ = Map.KHARKOV
        assert str(map_) == map_.id

    def test_map_repr(self) -> None:
        map_ = Map.KHARKOV
        expected_repr = (
            f"Map(id='kharkov', name='Kharkov', tag='KHA', "
            f"pretty_name='Kharkov', short_name='Kharkov', "
            f"allies={map_.allies!r}, axis={map_.axis!r}, "
            f"orientation={map_.orientation!r}, mirrored={map_.mirrored!r})"
        )
        assert repr(map_) == expected_repr

    def test_map_equality(self) -> None:
        map_ = Map.KHARKOV
        assert map_ == map_  # noqa: PLR0124
        assert map_ == map_.id.lower()
        assert map_ != Map.DRIEL
        assert map_ != "Some other map"
        assert map_ != 12345

    def test_map_hash(self) -> None:
        map_ = Map.KHARKOV
        assert hash(map_) == hash(map_.id.lower())
        assert hash(map_) != hash(Map.DRIEL)


class TestDataTeams:
    def test_team_by_id(self) -> None:
        assert Team.by_id(1) == Team.ALLIES
        assert Team.by_id(2) == Team.AXIS

        with pytest.raises(ValueError, match="not found"):
            Team.by_id(3)


class TestDataRoles:
    def test_role_by_id(self) -> None:
        assert Role.by_id(0) == Role.RIFLEMAN
        assert Role.by_id(1) == Role.ASSAULT
        assert Role.by_id(2) == Role.AUTOMATIC_RIFLEMAN
        assert Role.by_id(3) == Role.MEDIC
        assert Role.by_id(4) == Role.SPOTTER
        assert Role.by_id(5) == Role.SUPPORT
        assert Role.by_id(6) == Role.MACHINE_GUNNER
        assert Role.by_id(7) == Role.ANTI_TANK
        assert Role.by_id(8) == Role.ENGINEER
        assert Role.by_id(9) == Role.OFFICER
        assert Role.by_id(10) == Role.SNIPER
        assert Role.by_id(11) == Role.CREWMAN
        assert Role.by_id(12) == Role.TANK_COMMANDER
        assert Role.by_id(13) == Role.COMMANDER

        with pytest.raises(ValueError, match="not found"):
            Team.by_id(14)

    def test_role_properties(self) -> None:
        all_squad_leaders = {role for role in Role.all() if role.is_squad_leader}
        assert all_squad_leaders == {
            Role.OFFICER,
            Role.SPOTTER,
            Role.COMMANDER,
            Role.TANK_COMMANDER,
        }

        grouped_by_type: dict[RoleType, set[Role]] = {}
        for role in Role.all():
            grouped_by_type.setdefault(role.type, set()).add(role)

        assert grouped_by_type == {
            RoleType.INFANTRY: {
                Role.RIFLEMAN,
                Role.ASSAULT,
                Role.AUTOMATIC_RIFLEMAN,
                Role.MEDIC,
                Role.SUPPORT,
                Role.MACHINE_GUNNER,
                Role.ANTI_TANK,
                Role.ENGINEER,
                Role.OFFICER,
            },
            RoleType.RECON: {
                Role.SPOTTER,
                Role.SNIPER,
            },
            RoleType.ARMOR: {
                Role.CREWMAN,
                Role.TANK_COMMANDER,
            },
            RoleType.COMMANDER: {
                Role.COMMANDER,
            },
        }


class TestDataWeapons:
    def test_weapon_by_id(self) -> None:
        assert Weapon.by_id("M1 GARAND") == Weapon.M1_GARAND
        assert Weapon.by_id("MP40") == Weapon.MP40
        assert (
            Weapon.by_id("COAXIAL M1919 [Sherman M4A3E2]")
            == Weapon.V_COAXIAL_M1919__SHERMAN_M4A3E2
        )

        with pytest.raises(ValueError, match="not found"):
            Weapon.by_id("invalid_weapon")

        with pytest.raises(ValueError, match="not found"):
            Weapon.by_id("m1 garand")

    def test_weapon_resolve_vehicle(self) -> None:
        for weapon in Weapon.all():
            weapon.vehicle  # noqa: B018


class TestDataVehicles:
    def test_vehicle_by_id(self) -> None:
        assert Vehicle.by_id("Sherman M4A3E2") == Vehicle.SHERMAN_M4A3E2
        assert Vehicle.by_id("sFH 18") == Vehicle.SFH_18

        with pytest.raises(ValueError, match="not found"):
            Vehicle.by_id("invalid_vehicle")

        with pytest.raises(ValueError, match="not found"):
            Vehicle.by_id("sherman m4a3e2")
