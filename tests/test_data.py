import pytest
from hllrcon.data import Faction, GameMode, Layer, Map, Team
from hllrcon.data._utils import IndexedBaseModel
from hllrcon.data.game_modes import GameModeScale
from hllrcon.data.layers import TimeOfDay, Weather


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


class TestDataFactions:
    def test_faction_by_id(self) -> None:
        assert Faction.by_id(0) == Faction.GER
        assert Faction.by_id(1) == Faction.US
        assert Faction.by_id(2) == Faction.SOV
        assert Faction.by_id(3) == Faction.CW
        assert Faction.by_id(4) == Faction.DAK
        assert Faction.by_id(5) == Faction.B8A

        with pytest.raises(ValueError, match="not found"):
            Faction.by_id(6)


class TestDataGameModes:
    def test_game_mode_by_id(self) -> None:
        assert GameMode.by_id("warfare") == GameMode.WARFARE
        assert GameMode.by_id("offensive") == GameMode.OFFENSIVE
        assert GameMode.by_id("skirmish") == GameMode.SKIRMISH

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

        with pytest.raises(ValueError, match="not found"):
            Layer.by_id("Not a layer")

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


class TestDataMaps:
    def test_map_by_id(self) -> None:
        assert Map.by_id("kharkov") == Map.KHARKOV
        assert Map.by_id("driel") == Map.DRIEL
        assert Map.by_id("elalamein") == Map.EL_ALAMEIN
        assert Map.by_id("mortain") == Map.MORTAIN
        assert Map.by_id("elsenbornridge") == Map.ELSENBORN_RIDGE

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
