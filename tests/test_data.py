import pytest
from hllrcon.data import factions, game_modes, layers, maps, teams
from hllrcon.data.utils import IndexedBaseModel


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
        assert factions.by_id(0) == factions.GER
        assert factions.by_id(1) == factions.US
        assert factions.by_id(2) == factions.SOV
        assert factions.by_id(3) == factions.CW
        assert factions.by_id(4) == factions.DAK
        assert factions.by_id(5) == factions.B8A

        with pytest.raises(ValueError, match="not found"):
            factions.by_id(6)


class TestDataGameModes:
    def test_game_mode_by_id(self) -> None:
        assert game_modes.by_id("warfare") == game_modes.WARFARE
        assert game_modes.by_id("offensive") == game_modes.OFFENSIVE
        assert game_modes.by_id("skirmish") == game_modes.SKIRMISH

        with pytest.raises(ValueError, match="not found"):
            game_modes.by_id("invalid_mode")

    def test_game_mode_scale(self) -> None:
        large = game_modes.GameMode(id="large", scale=game_modes.GameModeScale.LARGE)
        small = game_modes.GameMode(id="small", scale=game_modes.GameModeScale.SMALL)

        assert large.is_large()
        assert not large.is_small()

        assert not small.is_large()
        assert small.is_small()


class TestDataLayers:
    def test_layer_by_id(self) -> None:
        assert layers.by_id("KHA_S_1944_P_Skirmish") == layers.KHARKOV_SKIRMISH_DAY

        with pytest.raises(ValueError, match="not found"):
            layers.by_id("Not a layer")

    def test_layer_str(self) -> None:
        layer = layers.KHARKOV_SKIRMISH_DAY
        assert str(layer) == layer.id

    def test_layer_repr(self) -> None:
        layer = layers.KHARKOV_SKIRMISH_DAY
        expected_repr = (
            f"Layer(id='KHA_S_1944_P_Skirmish', map={layer.map!r}, "
            f"attackers={layer.attacking_team!r}, time_of_day={layer.time_of_day!r}, "
            f"weather={layer.weather!r})"
        )
        assert repr(layer) == expected_repr

    def test_layer_equality(self) -> None:
        layer = layers.KHARKOV_SKIRMISH_DAY
        assert layer == layer  # noqa: PLR0124
        assert layer == layer.id.lower()
        assert layer != layers.KHARKOV_SKIRMISH_NIGHT
        assert layer != "Some other layer"
        assert layer != 12345

    def test_layer_hash(self) -> None:
        layer = layers.KHARKOV_SKIRMISH_DAY
        assert hash(layer) == hash(layer.id.lower())
        assert hash(layer) != hash(layers.KHARKOV_SKIRMISH_NIGHT)

    @pytest.mark.parametrize(
        ("layer", "name"),
        [
            (layers.KHARKOV_SKIRMISH_DAY, "Kharkov Skirmish"),
            (layers.DRIEL_OFFENSIVE_CW_DAY, "Driel Off. CW"),
            (layers.MORTAIN_OFFENSIVE_GER_OVERCAST, "Mortain Off. GER (Overcast)"),
            (layers.SMDM_SKIRMISH_RAIN, "St. Marie Du Mont Skirmish (Rain)"),
            (layers.ALAMEIN_WARFARE_DUSK, "El Alamein Warfare (Dusk)"),
            (
                layers.ELSENBORN_OFFENSIVE_US_DAWN,
                "Elsenborn Ridge Off. US (Dawn, Snow)",
            ),
        ],
    )
    def test_layer_pretty_name(self, layer: layers.Layer, name: str) -> None:
        assert layer.pretty_name == name

    def test_layer_pretty_name_missing_attacking_team(self) -> None:
        layer = layers.Layer(
            id="test_layer",
            map=maps.KHARKOV,
            game_mode=game_modes.OFFENSIVE,
            time_of_day=layers.TimeOfDay.DAY,
            weather=layers.Weather.OVERCAST,
            attacking_team=None,
        )
        assert layer.pretty_name == "Kharkov Off. (Overcast)"

    def test_layer_attackers(self) -> None:
        layer1 = layers.KURSK_OFFENSIVE_SOV_DAY
        assert layer1.attacking_team == teams.ALLIES
        assert layer1.defending_team == teams.AXIS
        assert layer1.attacking_faction == factions.SOV
        assert layer1.defending_faction == factions.GER

        layer2 = layers.KURSK_OFFENSIVE_GER_DAY
        assert layer2.attacking_team == teams.AXIS
        assert layer2.defending_team == teams.ALLIES
        assert layer2.attacking_faction == factions.GER
        assert layer2.defending_faction == factions.SOV

        layer3 = layers.KURSK_WARFARE_DAY
        assert layer3.attacking_team is None
        assert layer3.defending_team is None
        assert layer3.attacking_faction is None
        assert layer3.defending_faction is None


class TestDataMaps:
    def test_map_by_id(self) -> None:
        assert maps.by_id("kharkov") == maps.KHARKOV
        assert maps.by_id("driel") == maps.DRIEL
        assert maps.by_id("elalamein") == maps.EL_ALAMEIN
        assert maps.by_id("mortain") == maps.MORTAIN
        assert maps.by_id("elsenbornridge") == maps.ELSENBORN_RIDGE

        with pytest.raises(ValueError, match="not found"):
            maps.by_id("invalid_map")

    def test_map_str(self) -> None:
        map_ = maps.KHARKOV
        assert str(map_) == map_.id

    def test_map_repr(self) -> None:
        map_ = maps.KHARKOV
        expected_repr = (
            f"Map(id='kharkov', name='Kharkov', tag='KHA', "
            f"pretty_name='Kharkov', short_name='Kharkov', "
            f"allies={map_.allies!r}, axis={map_.axis!r}, "
            f"orientation={map_.orientation!r}, mirrored={map_.mirrored!r})"
        )
        assert repr(map_) == expected_repr

    def test_map_equality(self) -> None:
        map_ = maps.KHARKOV
        assert map_ == map_  # noqa: PLR0124
        assert map_ == map_.id.lower()
        assert map_ != maps.DRIEL
        assert map_ != "Some other map"
        assert map_ != 12345

    def test_map_hash(self) -> None:
        map_ = maps.KHARKOV
        assert hash(map_) == hash(map_.id.lower())
        assert hash(map_) != hash(maps.DRIEL)


class TestDataTeams:
    def test_team_by_id(self) -> None:
        assert teams.by_id(1) == teams.ALLIES
        assert teams.by_id(2) == teams.AXIS

        with pytest.raises(ValueError, match="not found"):
            teams.by_id(3)
