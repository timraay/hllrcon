from collections.abc import Generator
from typing import NamedTuple

import pytest
from hllrcon.data import (
    Faction,
    GameMode,
    GameModeScale,
    Grid,
    Layer,
    Loadout,
    LoadoutId,
    Map,
    Role,
    Strongpoint,
    Team,
    TimeOfDay,
    Vehicle,
    Weapon,
    Weather,
)
from hllrcon.data._utils import IndexedBaseModel, class_cached_property
from hllrcon.data.sectors import GridPositionalModel
from pydantic import BaseModel, ValidationError


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

    class FactionProperties(NamedTuple):
        faction: Faction
        is_allied: bool
        is_axis: bool

    @pytest.mark.parametrize(
        "properties",
        [
            FactionProperties(Faction.GER, False, True),
            FactionProperties(Faction.US, True, False),
            FactionProperties(Faction.SOV, True, False),
            FactionProperties(Faction.CW, True, False),
            FactionProperties(Faction.DAK, False, True),
            FactionProperties(Faction.B8A, True, False),
        ],
    )
    def test_faction_properties(self, properties: FactionProperties) -> None:
        assert properties.faction.is_allied is properties.is_allied
        assert properties.faction.is_axis is properties.is_axis


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
        assert Layer.by_id("DRL_S_1944_Day_P_Skirmish") == Layer.DRIEL_SKIRMISH_DAY
        assert Layer.by_id("drl_s_1944_day_p_skirmish") == Layer.DRIEL_SKIRMISH_DAY

        with pytest.raises(ValueError, match="not parse"):
            Layer.by_id("Not a layer", strict=False)

        with pytest.raises(ValueError, match="not found"):
            Layer.by_id("Not a layer", strict=True)

    def test_layer_str(self) -> None:
        layer = Layer.DRIEL_SKIRMISH_DAY
        assert str(layer) == layer.id

    def test_layer_repr(self) -> None:
        layer = Layer.DRIEL_SKIRMISH_DAY
        expected_repr = (
            f"Layer(id='DRL_S_1944_Day_P_Skirmish', map={layer.map!r}, "
            f"attackers={layer.attacking_team!r}, time_of_day={layer.time_of_day!r}, "
            f"weather={layer.weather!r})"
        )
        assert repr(layer) == expected_repr

    def test_layer_equality(self) -> None:
        layer = Layer.DRIEL_SKIRMISH_DAY
        assert layer == layer  # noqa: PLR0124
        assert layer == layer.id.lower()
        assert layer != Layer.DRIEL_SKIRMISH_DAWN
        assert layer != "Some other layer"
        assert layer != 12345

    def test_layer_hash(self) -> None:
        layer = Layer.DRIEL_SKIRMISH_DAY
        assert hash(layer) == hash(layer.id.lower())
        assert hash(layer) != hash(Layer.DRIEL_SKIRMISH_DAWN)

    @pytest.mark.parametrize(
        ("layer", "name"),
        [
            (Layer.DRIEL_SKIRMISH_DAY, "Driel Skirmish"),
            (Layer.DRIEL_OFFENSIVE_CW_DAY, "Driel Off. CW"),
            (Layer.MORTAIN_OFFENSIVE_GER_OVERCAST, "Mortain Off. GER (Overcast)"),
            (Layer.STMARIEDUMONT_SKIRMISH_RAIN, "St. Marie Du Mont Skirmish (Rain)"),
            (Layer.ELALAMEIN_WARFARE_DUSK, "El Alamein Warfare (Dusk)"),
            (
                Layer.ELSENBORNRIDGE_OFFENSIVE_US_DAWN,
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
            grid=Grid.large(),
            sectors=[],
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
        assert Layer.TOBRUK_WARFARE_DAY.sectors[0].area == (
            (-100000, -60000),
            (-60000, 60000),
        )

        assert Layer.PURPLEHEARTLANE_SKIRMISH_RAIN.sectors[0].area == (
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
        zone = Layer.STMEREEGLISE_WARFARE_DAY.sectors[2].capture_zones[2]

        assert zone.is_inside((0, 40000))
        assert zone.is_inside((-19000, 21000))
        assert zone.is_inside((19000, 21000))
        assert zone.is_inside((19000, 59000))
        assert zone.is_inside((-19000, 59000))

        assert not zone.is_inside((0, 0))
        assert not zone.is_inside((-21000, 40000))

    def test_sector_is_inside(self) -> None:
        sector = Layer.KHARKOV_WARFARE_DAY.sectors[2]

        assert sector.is_inside((0, 0))
        assert sector.is_inside((0, 19000))
        assert not sector.is_inside((0, 21000))
        assert sector.is_inside((59000, 19000))
        assert not sector.is_inside((61000, 19000))


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
            f"orientation={map_.orientation!r}, "
            f"mirror_factions={map_.mirror_factions!r})"
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

    class RoleProperties(NamedTuple):
        role: Role
        is_infantry: bool
        is_tanker: bool
        is_artillery: bool
        is_recon: bool
        is_squad_leader: bool

    @pytest.mark.parametrize(
        "properties",
        [
            RoleProperties(Role.RIFLEMAN, True, False, False, False, False),
            RoleProperties(Role.ASSAULT, True, False, False, False, False),
            RoleProperties(Role.AUTOMATIC_RIFLEMAN, True, False, False, False, False),
            RoleProperties(Role.MEDIC, True, False, False, False, False),
            RoleProperties(Role.SPOTTER, False, False, False, True, True),
            RoleProperties(Role.SUPPORT, True, False, False, False, False),
            RoleProperties(Role.MACHINE_GUNNER, True, False, False, False, False),
            RoleProperties(Role.ANTI_TANK, True, False, False, False, False),
            RoleProperties(Role.ENGINEER, True, False, False, False, False),
            RoleProperties(Role.OFFICER, True, False, False, False, True),
            RoleProperties(Role.SNIPER, False, False, False, True, False),
            RoleProperties(Role.CREWMAN, False, True, False, False, False),
            RoleProperties(Role.TANK_COMMANDER, False, True, False, False, True),
            RoleProperties(Role.COMMANDER, False, False, False, False, True),
            RoleProperties(Role.ARTILLERY_OBSERVER, False, False, True, False, True),
            RoleProperties(Role.ARTILLERY_ENGINEER, False, False, True, False, False),
            RoleProperties(Role.ARTILLERY_SUPPORT, False, False, True, False, False),
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


class TestDataLoadouts:
    def test_loadout_by_id(self) -> None:
        assert (
            Loadout.by_id(LoadoutId(Faction.US.id, Role.OFFICER.id, "NCO"))
            == Loadout.US_OFFICER_NCO
        )
        assert (
            Loadout.by_id(LoadoutId(Faction.CW.id, Role.RIFLEMAN.id, "Standard Issue"))
            == Loadout.CW_RIFLEMAN_STANDARD_ISSUE
        )

        assert (
            Loadout.by_id(LoadoutId(Faction.CW.id, Role.RIFLEMAN.id, "sTaNdArD iSsUe"))
            == Loadout.CW_RIFLEMAN_STANDARD_ISSUE
        )

        with pytest.raises(ValueError, match="not found"):
            Loadout.by_id(LoadoutId(Faction.US.id, Role.RIFLEMAN.id, "invalid_loadout"))
        with pytest.raises(ValueError, match="not found"):
            Loadout.by_id(LoadoutId(Faction.US.id, 69, "Standard Issue"))

    def test_loadout_by_name(self) -> None:
        assert (
            Loadout.by_name(Faction.US, Role.OFFICER, "NCO") == Loadout.US_OFFICER_NCO
        )
        assert (
            Loadout.by_name(Faction.CW, Role.RIFLEMAN, "Standard Issue")
            == Loadout.CW_RIFLEMAN_STANDARD_ISSUE
        )

        assert (
            Loadout.by_name(Faction.CW, Role.RIFLEMAN, "sTaNdArD iSsUe")
            == Loadout.CW_RIFLEMAN_STANDARD_ISSUE
        )

        with pytest.raises(ValueError, match="not found"):
            Loadout.by_name(Faction.US, Role.RIFLEMAN, "invalid_loadout")

    def test_loadout_equipment_weapon(self) -> None:
        assert Loadout.US_OFFICER_NCO.items[0].weapon == Weapon.M1_GARAND
        assert Loadout.US_OFFICER_NCO.items[1].weapon == Weapon.MK2_GRENADE
        assert Loadout.US_OFFICER_NCO.items[2].weapon is None
