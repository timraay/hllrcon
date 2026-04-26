import json
from collections.abc import Generator
from typing import Annotated, NamedTuple

import pytest
from hllrcon.data import (
    GameModeScale,
    Grid,
    HLLFaction,
    HLLGameMode,
    HLLLayer,
    HLLLoadout,
    HLLMap,
    HLLRole,
    HLLTeam,
    HLLVehicle,
    HLLWeapon,
    LoadoutId,
    Strongpoint,
    TimeOfDay,
    Weather,
)
from hllrcon.data._utils import (
    IndexedBaseModel,
    IndexedBaseModelProxy,
    class_cached_property,
    model_sequence_serializer,
    model_serializer,
)
from hllrcon.data.sectors import GridPositionalModel
from pydantic import BaseModel, ValidationError


@pytest.fixture(autouse=True)
def reset_lookup_maps() -> Generator[None]:
    layer_lookup_map = HLLLayer._lookup_map.copy()
    map_lookup_map = HLLMap._lookup_map.copy()

    yield

    HLLLayer._lookup_map = layer_lookup_map
    HLLMap._lookup_map = map_lookup_map


class TestDataUtils:
    def test_indexed_model(self) -> None:
        class MyModel(IndexedBaseModel[int]):
            id: int
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

    def test_indexed_model_str_and_repr(self) -> None:
        class MyModel(IndexedBaseModel[str]):
            id: str
            foo: str

        foo = MyModel(id="bar", foo="baz")

        expected = "MyModel(id='bar')"
        assert str(foo) == expected
        assert repr(foo) == expected

    def test_indexed_model_equality(self) -> None:
        class MyModel(IndexedBaseModel[int]):
            id: int
            name: str

        foo = MyModel(id=1, name="Foo")
        bar = MyModel(id=2, name="Bar")

        assert foo == foo  # noqa: PLR0124
        assert foo == 1
        assert foo != bar
        assert foo != 2
        assert foo != "Some other type"

    def test_indexed_model_hashable(self) -> None:
        class MyModel(IndexedBaseModel[int]):
            id: int
            name: str

        foo = MyModel(id=1, name="Foo")
        bar = MyModel(id=2, name="Bar")

        model_set = {foo, bar}
        assert foo in model_set
        assert bar in model_set
        assert MyModel.by_id(1) in model_set
        assert MyModel.by_id(2) in model_set
        assert MyModel(id=3, name="Baz") not in model_set

    def test_indexed_model_resolves_properties(self) -> None:
        class MyModel(IndexedBaseModel[int]):
            id: int

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

    def test_missing_id(self) -> None:
        with pytest.raises(TypeError, match=r"must define an 'id' field."):

            class MyModel(IndexedBaseModel[int]):
                name: str

    def test_indexed_model_proxy_ordering(self) -> None:
        class Foo(IndexedBaseModel[int]):
            id: int

        class Bar(IndexedBaseModel[int]):
            id: int

        foo1 = IndexedBaseModelProxy.from_model(Foo(id=1))
        foo2 = IndexedBaseModelProxy.from_model(Foo(id=2))
        bar1 = IndexedBaseModelProxy.from_model(Bar(id=1))
        bar2 = IndexedBaseModelProxy.from_model(Bar(id=2))

        assert sorted([foo1, foo2, bar1, bar2]) == [bar1, bar2, foo1, foo2]

    def test_json_serialization(self) -> None:
        class Foo(IndexedBaseModel[int]):
            id: int

        class Bar(IndexedBaseModel[int]):
            id: int
            foo: Annotated[
                Foo | None,
                model_serializer(int, optional=True),
            ]
            foos: Annotated[
                set[Foo] | None,
                model_sequence_serializer(int, optional=True),
            ]
            foos2: Annotated[
                list[Foo] | None,
                model_sequence_serializer(int, optional=True),
            ]
            foo_n: Annotated[
                Foo | None,
                model_serializer(int, optional=True),
            ] = None
            foos_n: Annotated[
                set[Foo] | None,
                model_sequence_serializer(int, optional=True),
            ] = None

        foo1 = Foo(id=1)
        foo2 = Foo(id=2)
        bar1 = Bar(id=1, foo=foo1, foos={foo2, foo1}, foos2=[foo2, foo1])

        json_data = bar1.model_dump_json()

        assert json.loads(json_data) == {
            "id": 1,
            "foo": {"type": "foo", "id": 1, "key": "1"},
            "foos": [
                {"type": "foo", "id": 1, "key": "1"},
                {"type": "foo", "id": 2, "key": "2"},
            ],
            "foos2": [
                {"type": "foo", "id": 2, "key": "2"},
                {"type": "foo", "id": 1, "key": "1"},
            ],
            "foo_n": None,
            "foos_n": None,
        }


class TestDataFactions:
    def test_faction_by_id(self) -> None:
        assert HLLFaction.by_id(0) == HLLFaction.GER
        assert HLLFaction.by_id(1) == HLLFaction.US
        assert HLLFaction.by_id(2) == HLLFaction.SOV
        assert HLLFaction.by_id(3) == HLLFaction.CW
        assert HLLFaction.by_id(4) == HLLFaction.DAK
        assert HLLFaction.by_id(5) == HLLFaction.B8A
        assert HLLFaction.by_id(6) is None

        with pytest.raises(ValueError, match="not found"):
            HLLFaction.by_id(7)

        assert None not in HLLFaction.all()

    class FactionProperties(NamedTuple):
        faction: HLLFaction
        is_allied: bool
        is_axis: bool

    @pytest.mark.parametrize(
        "properties",
        [
            FactionProperties(HLLFaction.GER, False, True),
            FactionProperties(HLLFaction.US, True, False),
            FactionProperties(HLLFaction.SOV, True, False),
            FactionProperties(HLLFaction.CW, True, False),
            FactionProperties(HLLFaction.DAK, False, True),
            FactionProperties(HLLFaction.B8A, True, False),
        ],
    )
    def test_faction_properties(self, properties: FactionProperties) -> None:
        assert properties.faction.is_allied is properties.is_allied
        assert properties.faction.is_axis is properties.is_axis


class TestDataGameModes:
    def test_game_mode_by_id(self) -> None:
        assert HLLGameMode.by_id("warfare") == HLLGameMode.WARFARE
        assert HLLGameMode.by_id("offensive") == HLLGameMode.OFFENSIVE
        assert HLLGameMode.by_id("skirmish") == HLLGameMode.SKIRMISH

        assert HLLGameMode.by_id("wArFaRe") == HLLGameMode.WARFARE

        with pytest.raises(ValueError, match="not found"):
            HLLGameMode.by_id("invalid_mode")

    def test_game_mode_scale(self) -> None:
        large = HLLGameMode(id="large", scale=GameModeScale.LARGE)
        small = HLLGameMode(id="small", scale=GameModeScale.SMALL)

        assert large.is_large()
        assert not large.is_small()

        assert not small.is_large()
        assert small.is_small()


class TestDataLayers:
    def test_layer_by_id(self) -> None:
        assert (
            HLLLayer.by_id("DRL_S_1944_Day_P_Skirmish") == HLLLayer.DRIEL_SKIRMISH_DAY
        )
        assert (
            HLLLayer.by_id("drl_s_1944_day_p_skirmish") == HLLLayer.DRIEL_SKIRMISH_DAY
        )

        with pytest.raises(ValueError, match="not parse"):
            HLLLayer.by_id("Not a layer", strict=False)

        with pytest.raises(ValueError, match="not found"):
            HLLLayer.by_id("Not a layer", strict=True)

    def test_layer_str(self) -> None:
        layer = HLLLayer.DRIEL_SKIRMISH_DAY
        assert str(layer) == layer.id

    def test_layer_repr(self) -> None:
        layer = HLLLayer.DRIEL_SKIRMISH_DAY
        expected_repr = "HLLLayer(id='DRL_S_1944_Day_P_Skirmish')"
        assert repr(layer) == expected_repr

    def test_layer_equality(self) -> None:
        layer = HLLLayer.DRIEL_SKIRMISH_DAY
        assert layer == layer  # noqa: PLR0124
        assert layer == layer.id.upper()
        assert layer != HLLLayer.DRIEL_SKIRMISH_DAWN
        assert layer != "Some other layer"
        assert layer != 12345

    def test_layer_hash(self) -> None:
        layer = HLLLayer.DRIEL_SKIRMISH_DAY
        assert hash(layer) == hash(layer.id.lower())
        assert hash(layer) != hash(HLLLayer.DRIEL_SKIRMISH_DAWN)

    @pytest.mark.parametrize(
        ("layer", "name"),
        [
            (HLLLayer.DRIEL_SKIRMISH_DAY, "Driel Skirmish"),
            (HLLLayer.DRIEL_OFFENSIVE_CW_DAY, "Driel Off. CW"),
            (HLLLayer.MORTAIN_OFFENSIVE_GER_OVERCAST, "Mortain Off. GER (Overcast)"),
            (HLLLayer.STMARIEDUMONT_SKIRMISH_RAIN, "St. Marie Du Mont Skirmish (Rain)"),
            (HLLLayer.ELALAMEIN_WARFARE_DUSK, "El Alamein Warfare (Dusk)"),
            (
                HLLLayer.ELSENBORNRIDGE_OFFENSIVE_US_DAWN,
                "Elsenborn Ridge Off. US (Dawn, Snow)",
            ),
        ],
    )
    def test_layer_pretty_name(self, layer: HLLLayer, name: str) -> None:
        assert layer.pretty_name == name

    def test_layer_pretty_name_missing_attacking_team(self) -> None:
        layer = HLLLayer(
            id="test_layer",
            map=HLLMap.KHARKOV,
            game_mode=HLLGameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.OVERCAST,
            attacking_team=None,
            grid=Grid.large(),
            sectors=[],
        )
        assert layer.pretty_name == "Kharkov Off. (Overcast)"

    def test_layer_attackers(self) -> None:
        layer1 = HLLLayer.KURSK_OFFENSIVE_SOV_DAY
        assert layer1.attacking_team == HLLTeam.ALLIES
        assert layer1.defending_team == HLLTeam.AXIS
        assert layer1.attacking_faction == HLLFaction.SOV
        assert layer1.defending_faction == HLLFaction.GER

        layer2 = HLLLayer.KURSK_OFFENSIVE_GER_DAY
        assert layer2.attacking_team == HLLTeam.AXIS
        assert layer2.defending_team == HLLTeam.ALLIES
        assert layer2.attacking_faction == HLLFaction.GER
        assert layer2.defending_faction == HLLFaction.SOV

        layer3 = HLLLayer.KURSK_WARFARE_DAY
        assert layer3.attacking_team is None
        assert layer3.defending_team is None
        assert layer3.attacking_faction is None
        assert layer3.defending_faction is None

    def test_layer_parse_id_small(self) -> None:
        layer = HLLLayer.by_id("FOO_S_1942_Rain_P_Skirmish", strict=False)
        assert layer.map.id == "FOO"
        assert layer.map.tag == "FOO"
        assert layer.map.name == "Foo"
        assert layer.game_mode == HLLGameMode.SKIRMISH
        assert layer.time_of_day == TimeOfDay.DAY
        assert layer.weather == Weather.RAIN
        assert layer.attacking_faction is None

    def test_layer_parse_id_large(self) -> None:
        layer = HLLLayer.by_id("FOO_L_1942_OffensiveCW_Morning", strict=False)
        assert layer.map.id == "FOO"
        assert layer.map.tag == "FOO"
        assert layer.map.name == "Foo"
        assert layer.game_mode == HLLGameMode.OFFENSIVE
        assert layer.time_of_day == TimeOfDay.DAWN
        assert layer.weather == Weather.CLEAR
        assert layer.attacking_faction == HLLFaction.CW

    def test_layer_parse_id_legacy(self) -> None:
        layer = HLLLayer.by_id("foo_warfare_night", strict=False)
        assert layer.map.id == "foo"
        assert layer.map.tag == "FOO"
        assert layer.map.name == "Foo"
        assert layer.game_mode == HLLGameMode.WARFARE
        assert layer.time_of_day == TimeOfDay.NIGHT
        assert layer.weather == Weather.CLEAR
        assert layer.attacking_faction is None

    def test_layer_parse_id_legacy_offensive(self) -> None:
        layer = HLLLayer.by_id("foo_offensive_ger", strict=False)
        assert layer.map.id == "foo"
        assert layer.map.tag == "FOO"
        assert layer.map.name == "Foo"
        assert layer.game_mode == HLLGameMode.OFFENSIVE
        assert layer.time_of_day == TimeOfDay.DAY
        assert layer.weather == Weather.CLEAR
        assert layer.attacking_faction == HLLFaction.GER

    def test_layer_parse_id_unknown_game_mode(self) -> None:
        with pytest.raises(ValueError, match="not parse"):
            HLLLayer.by_id("foy_notamode", strict=False)

    def test_layer_can_parse_known_layers(self) -> None:
        all_layers = HLLLayer.all()
        HLLLayer._lookup_map.clear()

        for layer in all_layers:
            HLLMap._lookup_map.clear()
            HLLLayer._parse_id(layer.id)

    def test_layer_field_serializers(self) -> None:
        layer = HLLLayer.KURSK_OFFENSIVE_GER_DAY
        exclude = {
            "sectors",
            "grid",
        }
        assert json.loads(layer.model_dump_json(exclude=exclude)) == {
            **layer.model_dump(exclude=exclude),
            "map": {
                "type": "hll_map",
                "id": "kursk",
                "key": "kursk",
            },
            "game_mode": {
                "type": "hll_game_mode",
                "id": "offensive",
                "key": "offensive",
            },
            "time_of_day": "Day",
            "weather": "Clear",
            "attacking_team": {"type": "hll_team", "id": 2, "key": "2"},
            "attacking_faction": {"type": "hll_faction", "id": 0, "key": "0"},
            "defending_team": {"type": "hll_team", "id": 1, "key": "1"},
            "defending_faction": {"type": "hll_faction", "id": 2, "key": "2"},
        }


class TestSectors:
    def test_grid_to_world(self) -> None:
        grid = Grid(
            scale=20000,
            offset=(1000, 0),
            size=((-5, -5), (4, 4)),
        )

        assert grid.grid_to_world_from((1, 2)) == (21000, 40000)
        assert grid.grid_to_world_to((1, 2)) == (41000, 60000)

        assert grid.grid_to_world_from((-1, -2)) == (-19000, -40000)
        assert grid.grid_to_world_to((-1, -2)) == (1000, -20000)

    def test_world_to_grid(self) -> None:
        grid = Grid(
            scale=20000,
            offset=(1000, 0),
            size=((-5, -5), (4, 4)),
        )

        assert grid.world_to_grid((0, 0)) == (-1, 0)
        assert grid.world_to_grid((20000, 50000)) == (0, 2)
        assert grid.world_to_grid((-20000, -50000)) == (-2, -3)

    def test_grid_area(self) -> None:
        assert HLLLayer.TOBRUK_WARFARE_DAY.sectors[0].area == (
            (-100000, -60000),
            (-60000, 60000),
        )

        assert HLLLayer.PURPLEHEARTLANE_SKIRMISH_RAIN.sectors[0].area == (
            (-55705.6, -69632),
            (55705.6, -13926.4),
        )

    def test_validate_grid_coords_order(self) -> None:
        GridPositionalModel(grid_from=(0, 0), grid_to=(1, 1))
        GridPositionalModel(grid_from=(0, 0), grid_to=(0, 0))
        GridPositionalModel(grid_from=(-2, 0), grid_to=(-1, 3))

        with pytest.raises(
            ValidationError,
            match=r"grid_from must be smaller than grid_to",
        ):
            GridPositionalModel(grid_from=(1, 0), grid_to=(0, 1))

        with pytest.raises(
            ValidationError,
            match=r"grid_from must be smaller than grid_to",
        ):
            GridPositionalModel(grid_from=(0, 1), grid_to=(1, 0))

        with pytest.raises(
            ValidationError,
            match=r"grid_from must be smaller than grid_to",
        ):
            GridPositionalModel(grid_from=(1, 1), grid_to=(0, 0))

    def test_strongpoint_is_inside(self) -> None:
        sp = Strongpoint(
            id="FOO",
            name="Foo",
            center=(10, 0, 0),
            radius=10,
        )

        assert sp.is_inside((10, 0, 0))
        assert sp.is_inside((20, 0, 0))
        assert sp.is_inside((10, 10, 0))
        assert not sp.is_inside((-1, 0, 0))
        assert not sp.is_inside((10, 10, 10))

    def test_capture_zone_is_inside(self) -> None:
        zone = HLLLayer.STMEREEGLISE_WARFARE_DAY.sectors[2].capture_zones[2]

        assert zone.is_inside((0, 40000))
        assert zone.is_inside((-19000, 21000))
        assert zone.is_inside((19000, 21000))
        assert zone.is_inside((19000, 59000))
        assert zone.is_inside((-19000, 59000))

        assert not zone.is_inside((0, 0))
        assert not zone.is_inside((-21000, 40000))

    def test_sector_is_inside(self) -> None:
        sector = HLLLayer.KHARKOV_WARFARE_DAY.sectors[2]

        assert sector.is_inside((0, 0))
        assert sector.is_inside((0, 19000))
        assert not sector.is_inside((0, 21000))
        assert sector.is_inside((59000, 19000))
        assert not sector.is_inside((61000, 19000))


class TestDataMaps:
    def test_map_by_id(self) -> None:
        assert HLLMap.by_id("kharkov") == HLLMap.KHARKOV
        assert HLLMap.by_id("driel") == HLLMap.DRIEL
        assert HLLMap.by_id("elalamein") == HLLMap.EL_ALAMEIN
        assert HLLMap.by_id("mortain") == HLLMap.MORTAIN
        assert HLLMap.by_id("elsenbornridge") == HLLMap.ELSENBORN_RIDGE

        assert HLLMap.by_id("kHaRkOv") == HLLMap.KHARKOV

        with pytest.raises(ValueError, match="not found"):
            HLLMap.by_id("invalid_map")

    def test_map_str(self) -> None:
        map_ = HLLMap.KHARKOV
        assert str(map_) == map_.id

    def test_map_repr(self) -> None:
        map_ = HLLMap.KHARKOV
        expected_repr = "HLLMap(id='kharkov')"
        assert repr(map_) == expected_repr

    def test_map_equality(self) -> None:
        map_ = HLLMap.KHARKOV
        assert map_ == map_  # noqa: PLR0124
        assert map_ == map_.id.lower()
        assert map_ != HLLMap.DRIEL
        assert map_ != "Some other map"
        assert map_ != 12345

    def test_map_hash(self) -> None:
        map_ = HLLMap.KHARKOV
        assert hash(map_) == hash(map_.id.lower())
        assert hash(map_) != hash(HLLMap.DRIEL)


class TestDataTeams:
    def test_team_by_id(self) -> None:
        assert HLLTeam.by_id(1) == HLLTeam.ALLIES
        assert HLLTeam.by_id(2) == HLLTeam.AXIS

        with pytest.raises(ValueError, match="not found"):
            HLLTeam.by_id(3)


class TestDataRoles:
    def test_role_by_id(self) -> None:
        assert HLLRole.by_id(0) == HLLRole.RIFLEMAN
        assert HLLRole.by_id(1) == HLLRole.ASSAULT
        assert HLLRole.by_id(2) == HLLRole.AUTOMATIC_RIFLEMAN
        assert HLLRole.by_id(3) == HLLRole.MEDIC
        assert HLLRole.by_id(4) == HLLRole.SPOTTER
        assert HLLRole.by_id(5) == HLLRole.SUPPORT
        assert HLLRole.by_id(6) == HLLRole.MACHINE_GUNNER
        assert HLLRole.by_id(7) == HLLRole.ANTI_TANK
        assert HLLRole.by_id(8) == HLLRole.ENGINEER
        assert HLLRole.by_id(9) == HLLRole.OFFICER
        assert HLLRole.by_id(10) == HLLRole.SNIPER
        assert HLLRole.by_id(11) == HLLRole.CREWMAN
        assert HLLRole.by_id(12) == HLLRole.TANK_COMMANDER
        assert HLLRole.by_id(13) == HLLRole.COMMANDER

        with pytest.raises(ValueError, match="not found"):
            HLLTeam.by_id(14)

    class RoleProperties(NamedTuple):
        role: HLLRole
        is_infantry: bool
        is_tanker: bool
        is_artillery: bool
        is_recon: bool
        is_squad_leader: bool

    @pytest.mark.parametrize(
        "properties",
        [
            RoleProperties(HLLRole.RIFLEMAN, True, False, False, False, False),
            RoleProperties(HLLRole.ASSAULT, True, False, False, False, False),
            RoleProperties(
                HLLRole.AUTOMATIC_RIFLEMAN,
                True,
                False,
                False,
                False,
                False,
            ),
            RoleProperties(HLLRole.MEDIC, True, False, False, False, False),
            RoleProperties(HLLRole.SPOTTER, False, False, False, True, True),
            RoleProperties(HLLRole.SUPPORT, True, False, False, False, False),
            RoleProperties(HLLRole.MACHINE_GUNNER, True, False, False, False, False),
            RoleProperties(HLLRole.ANTI_TANK, True, False, False, False, False),
            RoleProperties(HLLRole.ENGINEER, True, False, False, False, False),
            RoleProperties(HLLRole.OFFICER, True, False, False, False, True),
            RoleProperties(HLLRole.SNIPER, False, False, False, True, False),
            RoleProperties(HLLRole.CREWMAN, False, True, False, False, False),
            RoleProperties(HLLRole.TANK_COMMANDER, False, True, False, False, True),
            RoleProperties(HLLRole.COMMANDER, False, False, False, False, True),
            RoleProperties(HLLRole.ARTILLERY_OBSERVER, False, False, True, False, True),
            RoleProperties(HLLRole.OPERATOR, False, False, True, False, False),
            RoleProperties(HLLRole.GUNNER, False, False, True, False, False),
        ],
    )
    def test_role_properties(self, properties: RoleProperties) -> None:
        assert properties.role.is_infantry is properties.is_infantry
        assert properties.role.is_tanker is properties.is_tanker
        assert properties.role.is_artillery is properties.is_artillery
        assert properties.role.is_recon is properties.is_recon
        assert properties.role.is_squad_leader is properties.is_squad_leader


class TestDataWeapons:
    def test_weapon_by_id(self) -> None:
        assert HLLWeapon.by_id("M1 GARAND") == HLLWeapon.M1_GARAND
        assert HLLWeapon.by_id("MP40") == HLLWeapon.MP40
        assert (
            HLLWeapon.by_id("COAXIAL M1919 [Sherman M4A3E2]")
            == HLLWeapon.V_COAXIAL_M1919__SHERMAN_M4A3E2
        )

        with pytest.raises(ValueError, match="not found"):
            HLLWeapon.by_id("invalid_weapon")

        with pytest.raises(ValueError, match="not found"):
            HLLWeapon.by_id("m1 garand")

    def test_weapon_resolve_vehicle(self) -> None:
        for weapon in HLLWeapon.all():
            weapon.vehicle  # noqa: B018


class TestDataVehicles:
    def test_vehicle_by_id(self) -> None:
        assert HLLVehicle.by_id("Sherman M4A3E2") == HLLVehicle.SHERMAN_M4A3E2
        assert HLLVehicle.by_id("sFH 18") == HLLVehicle.SFH_18

        with pytest.raises(ValueError, match="not found"):
            HLLVehicle.by_id("invalid_vehicle")

        with pytest.raises(ValueError, match="not found"):
            HLLVehicle.by_id("sherman m4a3e2")

    class VehicleProperties(NamedTuple):
        vehicle: HLLVehicle
        is_truck: bool
        is_tank: bool
        is_artilerry: bool
        is_emplacement: bool

    @pytest.mark.parametrize(
        "properties",
        [
            VehicleProperties(HLLVehicle.BA_10, False, True, False, False),
            VehicleProperties(HLLVehicle.BEDFORD_OYD_SUPPLY, True, False, False, False),
            VehicleProperties(
                HLLVehicle.BEDFORD_OYD_TRANSPORT,
                True,
                False,
                False,
                False,
            ),
            VehicleProperties(HLLVehicle.M1938_M_30, False, False, True, True),
            VehicleProperties(HLLVehicle.KV_2, False, False, True, False),
        ],
    )
    def test_vehicle_properties(self, properties: VehicleProperties) -> None:
        assert properties.vehicle.is_truck is properties.is_truck
        assert properties.vehicle.is_tank is properties.is_tank
        assert properties.vehicle.is_artillery is properties.is_artilerry
        assert properties.vehicle.is_emplacement is properties.is_emplacement


class TestDataLoadouts:
    def test_loadout_by_id(self) -> None:
        assert (
            HLLLoadout.by_id(LoadoutId(HLLFaction.US.id, HLLRole.OFFICER.id, "NCO"))
            == HLLLoadout.US_OFFICER_NCO
        )
        assert (
            HLLLoadout.by_id(
                LoadoutId(HLLFaction.CW.id, HLLRole.RIFLEMAN.id, "Standard Issue"),
            )
            == HLLLoadout.CW_RIFLEMAN_STANDARD_ISSUE
        )

        assert (
            HLLLoadout.by_id(
                LoadoutId(HLLFaction.CW.id, HLLRole.RIFLEMAN.id, "sTaNdArD iSsUe"),
            )
            == HLLLoadout.CW_RIFLEMAN_STANDARD_ISSUE
        )

        with pytest.raises(ValueError, match="not found"):
            HLLLoadout.by_id(
                LoadoutId(HLLFaction.US.id, HLLRole.RIFLEMAN.id, "invalid_loadout"),
            )
        with pytest.raises(ValueError, match="not found"):
            HLLLoadout.by_id(LoadoutId(HLLFaction.US.id, 69, "Standard Issue"))

    def test_loadout_by_name(self) -> None:
        assert (
            HLLLoadout.by_name(HLLFaction.US, HLLRole.OFFICER, "NCO")
            == HLLLoadout.US_OFFICER_NCO
        )
        assert (
            HLLLoadout.by_name(HLLFaction.CW, HLLRole.RIFLEMAN, "Standard Issue")
            == HLLLoadout.CW_RIFLEMAN_STANDARD_ISSUE
        )

        assert (
            HLLLoadout.by_name(HLLFaction.CW, HLLRole.RIFLEMAN, "sTaNdArD iSsUe")
            == HLLLoadout.CW_RIFLEMAN_STANDARD_ISSUE
        )

        with pytest.raises(ValueError, match="not found"):
            HLLLoadout.by_name(HLLFaction.US, HLLRole.RIFLEMAN, "invalid_loadout")

    def test_loadout_equipment_weapon(self) -> None:
        assert HLLLoadout.US_OFFICER_NCO.items[0].weapon == HLLWeapon.M1_GARAND
        assert HLLLoadout.US_OFFICER_NCO.items[1].weapon == HLLWeapon.MK2_GRENADE
        assert HLLLoadout.US_OFFICER_NCO.items[2].weapon is None
