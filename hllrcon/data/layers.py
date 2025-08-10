# ruff: noqa: N802

from enum import StrEnum

from pydantic import computed_field

from ._utils import IndexedBaseModel, class_cached_property
from .factions import Faction
from .game_modes import GameMode
from .maps import Map
from .teams import Team


class TimeOfDay(StrEnum):
    DAWN = "dawn"
    DAY = "day"
    DUSK = "dusk"
    NIGHT = "night"


class Weather(StrEnum):
    CLEAR = "clear"
    OVERCAST = "overcast"
    RAIN = "rain"
    SNOW = "snow"


class Layer(IndexedBaseModel[str]):
    map: Map
    game_mode: GameMode
    time_of_day: TimeOfDay
    weather: Weather
    attacking_team: Team | None = None

    def __str__(self) -> str:
        return self.id

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(id={self.id!r}, map={self.map!r},"
            f" attackers={self.attacking_team!r}, time_of_day={self.time_of_day!r},"
            f" weather={self.weather!r})"
        )

    def __hash__(self) -> int:
        return hash(self.id.lower())

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (Layer, str)):
            return str(self).lower() == str(other).lower()
        return NotImplemented

    @computed_field  # type: ignore[prop-decorator]
    @property
    def pretty_name(self) -> str:
        out = self.map.pretty_name
        if self.game_mode == GameMode.OFFENSIVE:
            out += " Off."
            if self.attacking_faction:
                out += f" {self.attacking_faction.short_name}"
        else:
            out += f" {self.game_mode.id.capitalize()}"

        environment: list[str] = []

        if self.time_of_day != TimeOfDay.DAY:
            environment.append(self.time_of_day.value.title())
        if self.weather != Weather.CLEAR:
            environment.append(self.weather.value.title())

        if environment:
            out += f" ({', '.join(environment)})"

        return out

    @computed_field  # type: ignore[prop-decorator]
    @property
    def attacking_faction(self) -> Faction | None:
        if self.attacking_team == Team.ALLIES:
            return self.map.allies
        if self.attacking_team == Team.AXIS:
            return self.map.axis
        return None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def defending_team(self) -> Team | None:
        if self.attacking_team == Team.ALLIES:
            return Team.AXIS
        if self.attacking_team == Team.AXIS:
            return Team.ALLIES
        return None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def defending_faction(self) -> Faction | None:
        if self.attacking_team == Team.ALLIES:
            return self.map.axis
        if self.attacking_team == Team.AXIS:
            return self.map.allies
        return None

    @class_cached_property
    @classmethod
    def SME_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="stmereeglise_warfare",
            map=Map.ST_MERE_EGLISE,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def SME_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="stmereeglise_warfare_night",
            map=Map.ST_MERE_EGLISE,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def SME_OFFENSIVE_US_DAY(cls) -> "Layer":
        return cls(
            id="stmereeglise_offensive_us",
            map=Map.ST_MERE_EGLISE,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def SME_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="stmereeglise_offensive_ger",
            map=Map.ST_MERE_EGLISE,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def SME_SKIRMISH_DAY(cls) -> "Layer":
        return cls(
            id="SME_S_1944_Day_P_Skirmish",
            map=Map.ST_MERE_EGLISE,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def SME_SKIRMISH_DAWN(cls) -> "Layer":
        return cls(
            id="SME_S_1944_Morning_P_Skirmish",
            map=Map.ST_MERE_EGLISE,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAWN,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def SME_SKIRMISH_NIGHT(cls) -> "Layer":
        return cls(
            id="SME_S_1944_Night_P_Skirmish",
            map=Map.ST_MERE_EGLISE,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def SMDM_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="stmariedumont_warfare",
            map=Map.ST_MARIE_DU_MONT,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def SMDM_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="stmariedumont_warfare_night",
            map=Map.ST_MARIE_DU_MONT,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def SMDM_OFFENSIVE_US_DAY(cls) -> "Layer":
        return cls(
            id="stmariedumont_off_us",
            map=Map.ST_MARIE_DU_MONT,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def SMDM_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="stmariedumont_off_ger",
            map=Map.ST_MARIE_DU_MONT,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def UTAH_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="utahbeach_warfare",
            map=Map.UTAH_BEACH,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def UTAH_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="utahbeach_warfare_night",
            map=Map.UTAH_BEACH,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def UTAH_OFFENSIVE_US_DAY(cls) -> "Layer":
        return cls(
            id="utahbeach_offensive_us",
            map=Map.UTAH_BEACH,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def UTAH_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="utahbeach_offensive_ger",
            map=Map.UTAH_BEACH,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def OMAHA_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="omahabeach_warfare",
            map=Map.OMAHA_BEACH,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def OMAHA_WARFARE_DUSK(cls) -> "Layer":
        return cls(
            id="omahabeach_warfare_night",
            map=Map.OMAHA_BEACH,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def OMAHA_OFFENSIVE_US_DAY(cls) -> "Layer":
        return cls(
            id="omahabeach_offensive_us",
            map=Map.OMAHA_BEACH,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def OMAHA_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="omahabeach_offensive_ger",
            map=Map.OMAHA_BEACH,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def PHL_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="PHL_L_1944_Warfare",
            map=Map.PURPLE_HEART_LANE,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def PHL_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="PHL_L_1944_Warfare_Night",
            map=Map.PURPLE_HEART_LANE,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def PHL_OFFENSIVE_US_DAY(cls) -> "Layer":
        return cls(
            id="PHL_L_1944_OffensiveUS",
            map=Map.PURPLE_HEART_LANE,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def PHL_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="PHL_L_1944_OffensiveGER",
            map=Map.PURPLE_HEART_LANE,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def PHL_SKIRMISH_RAIN(cls) -> "Layer":
        return cls(
            id="PHL_S_1944_Rain_P_Skirmish",
            map=Map.PURPLE_HEART_LANE,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.RAIN,
        )

    @class_cached_property
    @classmethod
    def PHL_SKIRMISH_DAWN(cls) -> "Layer":
        return cls(
            id="PHL_S_1944_Morning_P_Skirmish",
            map=Map.PURPLE_HEART_LANE,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAWN,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def PHL_SKIRMISH_NIGHT(cls) -> "Layer":
        return cls(
            id="PHL_S_1944_Night_P_Skirmish",
            map=Map.PURPLE_HEART_LANE,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def CARENTAN_WARFARE(cls) -> "Layer":
        return cls(
            id="carentan_warfare",
            map=Map.CARENTAN,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def CARENTAN_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="carentan_warfare_night",
            map=Map.CARENTAN,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def CARENTAN_OFFENSIVE_US_DAY(cls) -> "Layer":
        return cls(
            id="carentan_offensive_us",
            map=Map.CARENTAN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def CARENTAN_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="carentan_offensive_ger",
            map=Map.CARENTAN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def CARENTAN_SKIRMISH_DAY(cls) -> "Layer":
        return cls(
            id="CAR_S_1944_Day_P_Skirmish",
            map=Map.CARENTAN,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def CARENTAN_SKIRMISH_RAIN(cls) -> "Layer":
        return cls(
            id="CAR_S_1944_Rain_P_Skirmish",
            map=Map.CARENTAN,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.RAIN,
        )

    @class_cached_property
    @classmethod
    def CARENTAN_SKIRMISH_DUSK(cls) -> "Layer":
        return cls(
            id="CAR_S_1944_Dusk_P_Skirmish",
            map=Map.CARENTAN,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def HURTGEN_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="hurtgenforest_warfare_V2",
            map=Map.HURTGEN_FOREST,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def HURTGEN_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="hurtgenforest_warfare_V2_night",
            map=Map.HURTGEN_FOREST,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def HURTGEN_OFFENSIVE_US_DAY(cls) -> "Layer":
        return cls(
            id="hurtgenforest_offensive_US",
            map=Map.HURTGEN_FOREST,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def HURTGEN_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="hurtgenforest_offensive_ger",
            map=Map.HURTGEN_FOREST,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def HILL400_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="hill400_warfare",
            map=Map.HILL_400,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def HILL400_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="hill400_warfare_night",
            map=Map.HILL_400,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def HILL400_OFFENSIVE_US_DAY(cls) -> "Layer":
        return cls(
            id="hill400_offensive_US",
            map=Map.HILL_400,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def HILL400_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="hill400_offensive_ger",
            map=Map.HILL_400,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def HILL400_SKIRMISH_DAY(cls) -> "Layer":
        return cls(
            id="HIL_S_1944_Day_P_Skirmish",
            map=Map.HILL_400,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def HILL400_SKIRMISH_DUSK(cls) -> "Layer":
        return cls(
            id="HIL_S_1944_Dusk_P_Skirmish",
            map=Map.HILL_400,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def HILL400_SKIRMISH_NIGHT(cls) -> "Layer":
        return cls(
            id="HIL_S_1944_Night_P_Skirmish",
            map=Map.HILL_400,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def FOY_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="foy_warfare",
            map=Map.FOY,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def FOY_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="foy_warfare_night",
            map=Map.FOY,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def FOY_OFFENSIVE_US_DAY(cls) -> "Layer":
        return cls(
            id="foy_offensive_us",
            map=Map.FOY,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def FOY_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="foy_offensive_ger",
            map=Map.FOY,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def FOY_SKIRMISH_DAY(cls) -> "Layer":
        return cls(
            id="FOY_S_1944_P_Skirmish",
            map=Map.FOY,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def FOY_SKIRMISH_NIGHT(cls) -> "Layer":
        return cls(
            id="FOY_S_1944_Night_P_Skirmish",
            map=Map.FOY,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def KURSK_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="kursk_warfare",
            map=Map.KURSK,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def KURSK_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="kursk_warfare_night",
            map=Map.KURSK,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def KURSK_OFFENSIVE_SOV_DAY(cls) -> "Layer":
        return cls(
            id="kursk_offensive_rus",
            map=Map.KURSK,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def KURSK_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="kursk_offensive_ger",
            map=Map.KURSK,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def STALINGRAD_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="stalingrad_warfare",
            map=Map.STALINGRAD,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def STALINGRAD_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="stalingrad_warfare_night",
            map=Map.STALINGRAD,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def STALINGRAD_OFFENSIVE_SOV_DAY(cls) -> "Layer":
        return cls(
            id="stalingrad_offensive_rus",
            map=Map.STALINGRAD,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def STALINGRAD_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="stalingrad_offensive_ger",
            map=Map.STALINGRAD,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def REMAGEN_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="remagen_warfare",
            map=Map.REMAGEN,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def REMAGEN_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="remagen_warfare_night",
            map=Map.REMAGEN,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def REMAGEN_OFFENSIVE_US_DAY(cls) -> "Layer":
        return cls(
            id="remagen_offensive_us",
            map=Map.REMAGEN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def REMAGEN_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="remagen_offensive_ger",
            map=Map.REMAGEN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def KHARKOV_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="kharkov_warfare",
            map=Map.KHARKOV,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def KHARKOV_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="kharkov_warfare_night",
            map=Map.KHARKOV,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def KHARKOV_OFFENSIVE_SOV_DAY(cls) -> "Layer":
        return cls(
            id="kharkov_offensive_rus",
            map=Map.KHARKOV,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def KHARKOV_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="kharkov_offensive_ger",
            map=Map.KHARKOV,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def KHARKOV_SKIRMISH_DAY(cls) -> "Layer":
        return cls(
            id="KHA_S_1944_P_Skirmish",
            map=Map.KHARKOV,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def KHARKOV_SKIRMISH_NIGHT(cls) -> "Layer":
        return cls(
            id="KHA_S_1944_Night_P_Skirmish",
            map=Map.KHARKOV,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def DRIEL_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="driel_warfare",
            map=Map.DRIEL,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def DRIEL_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="driel_warfare_night",
            map=Map.DRIEL,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def DRIEL_OFFENSIVE_CW_DAY(cls) -> "Layer":
        return cls(
            id="driel_offensive_us",
            map=Map.DRIEL,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def DRIEL_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="driel_offensive_ger",
            map=Map.DRIEL,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def DRIEL_SKIRMISH_DAWN(cls) -> "Layer":
        return cls(
            id="DRL_S_1944_P_Skirmish",
            map=Map.DRIEL,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAWN,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def DRIEL_SKIRMISH_NIGHT(cls) -> "Layer":
        return cls(
            id="DRL_S_1944_Night_P_Skirmish",
            map=Map.DRIEL,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def DRIEL_SKIRMISH_DAY(cls) -> "Layer":
        return cls(
            id="DRL_S_1944_Day_P_Skirmish",
            map=Map.DRIEL,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def ALAMEIN_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="elalamein_warfare",
            map=Map.EL_ALAMEIN,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def ALAMEIN_WARFARE_DUSK(cls) -> "Layer":
        return cls(
            id="elalamein_warfare_night",
            map=Map.EL_ALAMEIN,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def ALAMEIN_OFFENSIVE_B8A_DAY(cls) -> "Layer":
        return cls(
            id="elalamein_offensive_CW",
            map=Map.EL_ALAMEIN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def ALAMEIN_OFFENSIVE_DAK_DAY(cls) -> "Layer":
        return cls(
            id="elalamein_offensive_ger",
            map=Map.EL_ALAMEIN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def ALAMEIN_SKIRMISH_DAY(cls) -> "Layer":
        return cls(
            id="ELA_S_1942_P_Skirmish",
            map=Map.EL_ALAMEIN,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def ALAMEIN_SKIRMISH_DUSK(cls) -> "Layer":
        return cls(
            id="ELA_S_1942_Night_P_Skirmish",
            map=Map.EL_ALAMEIN,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def SMDM_SKIRMISH_DAY(cls) -> "Layer":
        return cls(
            id="SMDM_S_1944_Day_P_Skirmish",
            map=Map.ST_MARIE_DU_MONT,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def SMDM_SKIRMISH_NIGHT(cls) -> "Layer":
        return cls(
            id="SMDM_S_1944_Night_P_Skirmish",
            map=Map.ST_MARIE_DU_MONT,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def SMDM_SKIRMISH_RAIN(cls) -> "Layer":
        return cls(
            id="SMDM_S_1944_Rain_P_Skirmish",
            map=Map.ST_MARIE_DU_MONT,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.RAIN,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="mortain_warfare_day",
            map=Map.MORTAIN,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_WARFARE_DUSK(cls) -> "Layer":
        return cls(
            id="mortain_warfare_dusk",
            map=Map.MORTAIN,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_WARFARE_OVERCAST(cls) -> "Layer":
        return cls(
            id="mortain_warfare_overcast",
            map=Map.MORTAIN,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.OVERCAST,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="mortain_warfare_night",
            map=Map.MORTAIN,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_OFFENSIVE_US_DAY(cls) -> "Layer":
        return cls(
            id="mortain_offensiveUS_day",
            map=Map.MORTAIN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_OFFENSIVE_US_OVERCAST(cls) -> "Layer":
        return cls(
            id="mortain_offensiveUS_overcast",
            map=Map.MORTAIN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.OVERCAST,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_OFFENSIVE_US_DUSK(cls) -> "Layer":
        return cls(
            id="mortain_offensiveUS_dusk",
            map=Map.MORTAIN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_OFFENSIVE_US_NIGHT(cls) -> "Layer":
        return cls(
            id="mortain_offensiveUS_night",
            map=Map.MORTAIN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="mortain_offensiveger_day",
            map=Map.MORTAIN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_OFFENSIVE_GER_OVERCAST(cls) -> "Layer":
        return cls(
            id="mortain_offensiveger_overcast",
            map=Map.MORTAIN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.OVERCAST,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_OFFENSIVE_GER_DUSK(cls) -> "Layer":
        return cls(
            id="mortain_offensiveger_dusk",
            map=Map.MORTAIN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_OFFENSIVE_GER_NIGHT(cls) -> "Layer":
        return cls(
            id="mortain_offensiveger_night",
            map=Map.MORTAIN,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_SKIRMISH_DAY(cls) -> "Layer":
        return cls(
            id="mortain_skirmish_day",
            map=Map.MORTAIN,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_SKIRMISH_OVERCAST(cls) -> "Layer":
        return cls(
            id="mortain_skirmish_overcast",
            map=Map.MORTAIN,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.OVERCAST,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_SKIRMISH_DUSK(cls) -> "Layer":
        return cls(
            id="mortain_skirmish_dusk",
            map=Map.MORTAIN,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def MORTAIN_SKIRMISH_NIGHT(cls) -> "Layer":
        return cls(
            id="mortain_skirmish_night",
            map=Map.MORTAIN,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="elsenbornridge_warfare_day",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.SNOW,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_WARFARE_DAWN(cls) -> "Layer":
        return cls(
            id="elsenbornridge_warfare_morning",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAWN,
            weather=Weather.SNOW,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_WARFARE_DUSK(cls) -> "Layer":
        return cls(
            id="elsenbornridge_warfare_evening",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.SNOW,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_WARFARE_NIGHT(cls) -> "Layer":
        return cls(
            id="elsenbornridge_warfare_night",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.SNOW,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_OFFENSIVE_US_DAY(cls) -> "Layer":
        return cls(
            id="elsenbornridge_offensiveUS_day",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.SNOW,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_OFFENSIVE_US_DAWN(cls) -> "Layer":
        return cls(
            id="elsenbornridge_offensiveUS_morning",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAWN,
            weather=Weather.SNOW,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_OFFENSIVE_US_DUSK(cls) -> "Layer":
        return cls(
            id="elsenbornridge_offensiveUS_evening",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.SNOW,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_OFFENSIVE_US_NIGHT(cls) -> "Layer":
        return cls(
            id="elsenbornridge_offensiveUS_night",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.SNOW,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_OFFENSIVE_GER_DAY(cls) -> "Layer":
        return cls(
            id="elsenbornridge_offensiveger_day",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.SNOW,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_OFFENSIVE_GER_DAWN(cls) -> "Layer":
        return cls(
            id="elsenbornridge_offensiveger_morning",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAWN,
            weather=Weather.SNOW,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_OFFENSIVE_GER_DUSK(cls) -> "Layer":
        return cls(
            id="elsenbornridge_offensiveger_evening",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.SNOW,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_OFFENSIVE_GER_NIGHT(cls) -> "Layer":
        return cls(
            id="elsenbornridge_offensiveger_night",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.SNOW,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_SKIRMISH_DAY(cls) -> "Layer":
        return cls(
            id="elsenbornridge_skirmish_day",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.SNOW,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_SKIRMISH_DAWN(cls) -> "Layer":
        return cls(
            id="elsenbornridge_skirmish_morning",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAWN,
            weather=Weather.SNOW,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_SKIRMISH_DUSK(cls) -> "Layer":
        return cls(
            id="elsenbornridge_skirmish_evening",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.SNOW,
        )

    @class_cached_property
    @classmethod
    def ELSENBORN_SKIRMISH_NIGHT(cls) -> "Layer":
        return cls(
            id="elsenbornridge_skirmish_night",
            map=Map.ELSENBORN_RIDGE,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.NIGHT,
            weather=Weather.SNOW,
        )

    @class_cached_property
    @classmethod
    def TOBRUK_WARFARE_DAY(cls) -> "Layer":
        return cls(
            id="tobruk_warfare_day",
            map=Map.TOBRUK,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def TOBRUK_WARFARE_DUSK(cls) -> "Layer":
        return cls(
            id="tobruk_warfare_dusk",
            map=Map.TOBRUK,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def TOBRUK_WARFARE_DAWN(cls) -> "Layer":
        return cls(
            id="tobruk_warfare_morning",
            map=Map.TOBRUK,
            game_mode=GameMode.WARFARE,
            time_of_day=TimeOfDay.DAWN,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def TOBRUK_OFFENSIVE_B8A_DAY(cls) -> "Layer":
        return cls(
            id="tobruk_offensivebritish_day",
            map=Map.TOBRUK,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def TOBRUK_OFFENSIVE_DAK_DAY(cls) -> "Layer":
        return cls(
            id="tobruk_offensiveger_day",
            map=Map.TOBRUK,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def TOBRUK_OFFENSIVE_B8A_DUSK(cls) -> "Layer":
        return cls(
            id="tobruk_offensivebritish_dusk",
            map=Map.TOBRUK,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def TOBRUK_OFFENSIVE_DAK_DUSK(cls) -> "Layer":
        return cls(
            id="tobruk_offensiveger_dusk",
            map=Map.TOBRUK,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def TOBRUK_OFFENSIVE_B8A_DAWN(cls) -> "Layer":
        return cls(
            id="tobruk_offensivebritish_morning",
            map=Map.TOBRUK,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAWN,
            weather=Weather.CLEAR,
            attacking_team=Team.ALLIES,
        )

    @class_cached_property
    @classmethod
    def TOBRUK_OFFENSIVE_DAK_DAWN(cls) -> "Layer":
        return cls(
            id="tobruk_offensiveger_morning",
            map=Map.TOBRUK,
            game_mode=GameMode.OFFENSIVE,
            time_of_day=TimeOfDay.DAWN,
            weather=Weather.CLEAR,
            attacking_team=Team.AXIS,
        )

    @class_cached_property
    @classmethod
    def TOBRUK_SKIRMISH_DAY(cls) -> "Layer":
        return cls(
            id="tobruk_skirmish_day",
            map=Map.TOBRUK,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAY,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def TOBRUK_SKIRMISH_DUSK(cls) -> "Layer":
        return cls(
            id="tobruk_skirmish_dusk",
            map=Map.TOBRUK,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DUSK,
            weather=Weather.CLEAR,
        )

    @class_cached_property
    @classmethod
    def TOBRUK_SKIRMISH_DAWN(cls) -> "Layer":
        return cls(
            id="tobruk_skirmish_morning",
            map=Map.TOBRUK,
            game_mode=GameMode.SKIRMISH,
            time_of_day=TimeOfDay.DAWN,
            weather=Weather.CLEAR,
        )
