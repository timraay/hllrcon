from enum import StrEnum

from pydantic import computed_field

from hllrcon.data import factions, game_modes, maps, teams
from hllrcon.data.utils import IndexedBaseModel


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
    map: maps.Map
    game_mode: game_modes.GameMode
    time_of_day: TimeOfDay
    weather: Weather
    attacking_team: teams.Team | None = None

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
        if self.game_mode == game_modes.OFFENSIVE:
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
    def attacking_faction(self) -> factions.Faction | None:
        if self.attacking_team == teams.ALLIES:
            return self.map.allies
        if self.attacking_team == teams.AXIS:
            return self.map.axis
        return None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def defending_team(self) -> teams.Team | None:
        if self.attacking_team == teams.ALLIES:
            return teams.AXIS
        if self.attacking_team == teams.AXIS:
            return teams.ALLIES
        return None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def defending_faction(self) -> factions.Faction | None:
        if self.attacking_team == teams.ALLIES:
            return self.map.axis
        if self.attacking_team == teams.AXIS:
            return self.map.allies
        return None


SME_WARFARE_DAY = Layer(
    id="stmereeglise_warfare",
    map=maps.ST_MERE_EGLISE,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
SME_WARFARE_NIGHT = Layer(
    id="stmereeglise_warfare_night",
    map=maps.ST_MERE_EGLISE,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.CLEAR,
)
SME_OFFENSIVE_US_DAY = Layer(
    id="stmereeglise_offensive_us",
    map=maps.ST_MERE_EGLISE,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.ALLIES,
)
SME_OFFENSIVE_GER_DAY = Layer(
    id="stmereeglise_offensive_ger",
    map=maps.ST_MERE_EGLISE,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.AXIS,
)
SME_SKIRMISH_DAY = Layer(
    id="SME_S_1944_Day_P_Skirmish",
    map=maps.ST_MERE_EGLISE,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
SME_SKIRMISH_DAWN = Layer(
    id="SME_S_1944_Morning_P_Skirmish",
    map=maps.ST_MERE_EGLISE,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DAWN,
    weather=Weather.CLEAR,
)
SME_SKIRMISH_NIGHT = Layer(
    id="SME_S_1944_Night_P_Skirmish",
    map=maps.ST_MERE_EGLISE,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.CLEAR,
)
SMDM_WARFARE_DAY = Layer(
    id="stmariedumont_warfare",
    map=maps.ST_MARIE_DU_MONT,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
SMDM_WARFARE_NIGHT = Layer(
    id="stmariedumont_warfare_night",
    map=maps.ST_MARIE_DU_MONT,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.CLEAR,
)
SMDM_OFFENSIVE_US_DAY = Layer(
    id="stmariedumont_off_us",
    map=maps.ST_MARIE_DU_MONT,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.ALLIES,
)
SMDM_OFFENSIVE_GER_DAY = Layer(
    id="stmariedumont_off_ger",
    map=maps.ST_MARIE_DU_MONT,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.AXIS,
)
UTAH_WARFARE_DAY = Layer(
    id="utahbeach_warfare",
    map=maps.UTAH_BEACH,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
UTAH_WARFARE_NIGHT = Layer(
    id="utahbeach_warfare_night",
    map=maps.UTAH_BEACH,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.CLEAR,
)
UTAH_OFFENSIVE_US_DAY = Layer(
    id="utahbeach_offensive_us",
    map=maps.UTAH_BEACH,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.ALLIES,
)
UTAH_OFFENSIVE_GER_DAY = Layer(
    id="utahbeach_offensive_ger",
    map=maps.UTAH_BEACH,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.AXIS,
)
OMAHA_WARFARE_DAY = Layer(
    id="omahabeach_warfare",
    map=maps.OMAHA_BEACH,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
OMAHA_WARFARE_DUSK = Layer(
    id="omahabeach_warfare_night",
    map=maps.OMAHA_BEACH,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DUSK,
    weather=Weather.CLEAR,
)
OMAHA_OFFENSIVE_US_DAY = Layer(
    id="omahabeach_offensive_us",
    map=maps.OMAHA_BEACH,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.ALLIES,
)
OMAHA_OFFENSIVE_GER_DAY = Layer(
    id="omahabeach_offensive_ger",
    map=maps.OMAHA_BEACH,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.AXIS,
)
PHL_WARFARE_DAY = Layer(
    id="PHL_L_1944_Warfare",
    map=maps.PURPLE_HEART_LANE,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
PHL_WARFARE_NIGHT = Layer(
    id="PHL_L_1944_Warfare_Night",
    map=maps.PURPLE_HEART_LANE,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.CLEAR,
)
PHL_OFFENSIVE_US_DAY = Layer(
    id="PHL_L_1944_OffensiveUS",
    map=maps.PURPLE_HEART_LANE,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.ALLIES,
)
PHL_OFFENSIVE_GER_DAY = Layer(
    id="PHL_L_1944_OffensiveGER",
    map=maps.PURPLE_HEART_LANE,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.AXIS,
)
PHL_SKIRMISH_RAIN = Layer(
    id="PHL_S_1944_Rain_P_Skirmish",
    map=maps.PURPLE_HEART_LANE,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.RAIN,
)
PHL_SKIRMISH_DAWN = Layer(
    id="PHL_S_1944_Morning_P_Skirmish",
    map=maps.PURPLE_HEART_LANE,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DAWN,
    weather=Weather.CLEAR,
)
PHL_SKIRMISH_NIGHT = Layer(
    id="PHL_S_1944_Night_P_Skirmish",
    map=maps.PURPLE_HEART_LANE,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.CLEAR,
)
CARENTAN_WARFARE = Layer(
    id="carentan_warfare",
    map=maps.CARENTAN,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
CARENTAN_WARFARE_NIGHT = Layer(
    id="carentan_warfare_night",
    map=maps.CARENTAN,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.CLEAR,
)
CARENTAN_OFFENSIVE_US_DAY = Layer(
    id="carentan_offensive_us",
    map=maps.CARENTAN,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.ALLIES,
)
CARENTAN_OFFENSIVE_GER_DAY = Layer(
    id="carentan_offensive_ger",
    map=maps.CARENTAN,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.AXIS,
)
CARENTAN_SKIRMISH_DAY = Layer(
    id="CAR_S_1944_Day_P_Skirmish",
    map=maps.CARENTAN,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
CARENTAN_SKIRMISH_RAIN = Layer(
    id="CAR_S_1944_Rain_P_Skirmish",
    map=maps.CARENTAN,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.RAIN,
)
CARENTAN_SKIRMISH_DUSK = Layer(
    id="CAR_S_1944_Dusk_P_Skirmish",
    map=maps.CARENTAN,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DUSK,
    weather=Weather.CLEAR,
)
HURTGEN_WARFARE_DAY = Layer(
    id="hurtgenforest_warfare_V2",
    map=maps.HURTGEN_FOREST,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
HURTGEN_WARFARE_NIGHT = Layer(
    id="hurtgenforest_warfare_V2_night",
    map=maps.HURTGEN_FOREST,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.CLEAR,
)
HURTGEN_OFFENSIVE_US_DAY = Layer(
    id="hurtgenforest_offensive_US",
    map=maps.HURTGEN_FOREST,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.ALLIES,
)
HURTGEN_OFFENSIVE_GER_DAY = Layer(
    id="hurtgenforest_offensive_ger",
    map=maps.HURTGEN_FOREST,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.AXIS,
)
HILL400_WARFARE_DAY = Layer(
    id="hill400_warfare",
    map=maps.HILL_400,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
HILL400_WARFARE_NIGHT = Layer(
    id="hill400_warfare_night",
    map=maps.HILL_400,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.CLEAR,
)
HILL400_OFFENSIVE_US_DAY = Layer(
    id="hill400_offensive_US",
    map=maps.HILL_400,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.ALLIES,
)
HILL400_OFFENSIVE_GER_DAY = Layer(
    id="hill400_offensive_ger",
    map=maps.HILL_400,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.AXIS,
)
HILL400_SKIRMISH_DAY = Layer(
    id="HIL_S_1944_Day_P_Skirmish",
    map=maps.HILL_400,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
HILL400_SKIRMISH_DUSK = Layer(
    id="HIL_S_1944_Dusk_P_Skirmish",
    map=maps.HILL_400,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DUSK,
    weather=Weather.CLEAR,
)
HILL400_SKIRMISH_NIGHT = Layer(
    id="HIL_S_1944_Night_P_Skirmish",
    map=maps.HILL_400,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.CLEAR,
)
FOY_WARFARE_DAY = Layer(
    id="foy_warfare",
    map=maps.FOY,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
FOY_WARFARE_NIGHT = Layer(
    id="foy_warfare_night",
    map=maps.FOY,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.CLEAR,
)
FOY_OFFENSIVE_US_DAY = Layer(
    id="foy_offensive_us",
    map=maps.FOY,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.ALLIES,
)
FOY_OFFENSIVE_GER_DAY = Layer(
    id="foy_offensive_ger",
    map=maps.FOY,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.AXIS,
)
FOY_SKIRMISH_DAY = Layer(
    id="FOY_S_1944_P_Skirmish",
    map=maps.FOY,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
FOY_SKIRMISH_NIGHT = Layer(
    id="FOY_S_1944_Night_P_Skirmish",
    map=maps.FOY,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.CLEAR,
)
KURSK_WARFARE_DAY = Layer(
    id="kursk_warfare",
    map=maps.KURSK,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
KURSK_WARFARE_NIGHT = Layer(
    id="kursk_warfare_night",
    map=maps.KURSK,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.CLEAR,
)
KURSK_OFFENSIVE_SOV_DAY = Layer(
    id="kursk_offensive_rus",
    map=maps.KURSK,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.ALLIES,
)
KURSK_OFFENSIVE_GER_DAY = Layer(
    id="kursk_offensive_ger",
    map=maps.KURSK,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.AXIS,
)
STALINGRAD_WARFARE_DAY = Layer(
    id="stalingrad_warfare",
    map=maps.STALINGRAD,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
STALINGRAD_WARFARE_NIGHT = Layer(
    id="stalingrad_warfare_night",
    map=maps.STALINGRAD,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.CLEAR,
)
STALINGRAD_OFFENSIVE_SOV_DAY = Layer(
    id="stalingrad_offensive_rus",
    map=maps.STALINGRAD,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.ALLIES,
)
STALINGRAD_OFFENSIVE_GER_DAY = Layer(
    id="stalingrad_offensive_ger",
    map=maps.STALINGRAD,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.AXIS,
)
REMAGEN_WARFARE_DAY = Layer(
    id="remagen_warfare",
    map=maps.REMAGEN,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
REMAGEN_WARFARE_NIGHT = Layer(
    id="remagen_warfare_night",
    map=maps.REMAGEN,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.CLEAR,
)
REMAGEN_OFFENSIVE_US_DAY = Layer(
    id="remagen_offensive_us",
    map=maps.REMAGEN,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.ALLIES,
)
REMAGEN_OFFENSIVE_GER_DAY = Layer(
    id="remagen_offensive_ger",
    map=maps.REMAGEN,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.AXIS,
)
KHARKOV_WARFARE_DAY = Layer(
    id="kharkov_warfare",
    map=maps.KHARKOV,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
KHARKOV_WARFARE_NIGHT = Layer(
    id="kharkov_warfare_night",
    map=maps.KHARKOV,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.CLEAR,
)
KHARKOV_OFFENSIVE_SOV_DAY = Layer(
    id="kharkov_offensive_rus",
    map=maps.KHARKOV,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.ALLIES,
)
KHARKOV_OFFENSIVE_GER_DAY = Layer(
    id="kharkov_offensive_ger",
    map=maps.KHARKOV,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.AXIS,
)
KHARKOV_SKIRMISH_DAY = Layer(
    id="KHA_S_1944_P_Skirmish",
    map=maps.KHARKOV,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
KHARKOV_SKIRMISH_NIGHT = Layer(
    id="KHA_S_1944_Night_P_Skirmish",
    map=maps.KHARKOV,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.CLEAR,
)
DRIEL_WARFARE_DAY = Layer(
    id="driel_warfare",
    map=maps.DRIEL,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
DRIEL_WARFARE_NIGHT = Layer(
    id="driel_warfare_night",
    map=maps.DRIEL,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.CLEAR,
)
DRIEL_OFFENSIVE_CW_DAY = Layer(
    id="driel_offensive_us",
    map=maps.DRIEL,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.ALLIES,
)
DRIEL_OFFENSIVE_GER_DAY = Layer(
    id="driel_offensive_ger",
    map=maps.DRIEL,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.AXIS,
)
DRIEL_SKIRMISH_DAWN = Layer(
    id="DRL_S_1944_P_Skirmish",
    map=maps.DRIEL,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DAWN,
    weather=Weather.CLEAR,
)
DRIEL_SKIRMISH_NIGHT = Layer(
    id="DRL_S_1944_Night_P_Skirmish",
    map=maps.DRIEL,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.CLEAR,
)
DRIEL_SKIRMISH_DAY = Layer(
    id="DRL_S_1944_Day_P_Skirmish",
    map=maps.DRIEL,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
ALAMEIN_WARFARE_DAY = Layer(
    id="elalamein_warfare",
    map=maps.EL_ALAMEIN,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
ALAMEIN_WARFARE_DUSK = Layer(
    id="elalamein_warfare_night",
    map=maps.EL_ALAMEIN,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DUSK,
    weather=Weather.CLEAR,
)
ALAMEIN_OFFENSIVE_B8A_DAY = Layer(
    id="elalamein_offensive_CW",
    map=maps.EL_ALAMEIN,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.ALLIES,
)
ALAMEIN_OFFENSIVE_DAK_DAY = Layer(
    id="elalamein_offensive_ger",
    map=maps.EL_ALAMEIN,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.AXIS,
)
ALAMEIN_SKIRMISH_DAY = Layer(
    id="ELA_S_1942_P_Skirmish",
    map=maps.EL_ALAMEIN,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
ALAMEIN_SKIRMISH_DUSK = Layer(
    id="ELA_S_1942_Night_P_Skirmish",
    map=maps.EL_ALAMEIN,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DUSK,
    weather=Weather.CLEAR,
)
SMDM_SKIRMISH_DAY = Layer(
    id="SMDM_S_1944_Day_P_Skirmish",
    map=maps.ST_MARIE_DU_MONT,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
SMDM_SKIRMISH_NIGHT = Layer(
    id="SMDM_S_1944_Night_P_Skirmish",
    map=maps.ST_MARIE_DU_MONT,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.CLEAR,
)
SMDM_SKIRMISH_RAIN = Layer(
    id="SMDM_S_1944_Rain_P_Skirmish",
    map=maps.ST_MARIE_DU_MONT,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.RAIN,
)
MORTAIN_WARFARE_DAY = Layer(
    id="mortain_warfare_day",
    map=maps.MORTAIN,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
MORTAIN_WARFARE_DUSK = Layer(
    id="mortain_warfare_dusk",
    map=maps.MORTAIN,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DUSK,
    weather=Weather.CLEAR,
)
MORTAIN_WARFARE_OVERCAST = Layer(
    id="mortain_warfare_overcast",
    map=maps.MORTAIN,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.OVERCAST,
)
MORTAIN_WARFARE_NIGHT = Layer(
    id="mortain_warfare_night",
    map=maps.MORTAIN,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.CLEAR,
)
MORTAIN_OFFENSIVE_US_DAY = Layer(
    id="mortain_offensiveUS_day",
    map=maps.MORTAIN,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.ALLIES,
)
MORTAIN_OFFENSIVE_US_OVERCAST = Layer(
    id="mortain_offensiveUS_overcast",
    map=maps.MORTAIN,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.OVERCAST,
    attacking_team=teams.ALLIES,
)
MORTAIN_OFFENSIVE_US_DUSK = Layer(
    id="mortain_offensiveUS_dusk",
    map=maps.MORTAIN,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DUSK,
    weather=Weather.CLEAR,
    attacking_team=teams.ALLIES,
)
MORTAIN_OFFENSIVE_US_NIGHT = Layer(
    id="mortain_offensiveUS_night",
    map=maps.MORTAIN,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.CLEAR,
    attacking_team=teams.ALLIES,
)
MORTAIN_OFFENSIVE_GER_DAY = Layer(
    id="mortain_offensiveger_day",
    map=maps.MORTAIN,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.AXIS,
)
MORTAIN_OFFENSIVE_GER_OVERCAST = Layer(
    id="mortain_offensiveger_overcast",
    map=maps.MORTAIN,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.OVERCAST,
    attacking_team=teams.AXIS,
)
MORTAIN_OFFENSIVE_GER_DUSK = Layer(
    id="mortain_offensiveger_dusk",
    map=maps.MORTAIN,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DUSK,
    weather=Weather.CLEAR,
    attacking_team=teams.AXIS,
)
MORTAIN_OFFENSIVE_GER_NIGHT = Layer(
    id="mortain_offensiveger_night",
    map=maps.MORTAIN,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.CLEAR,
    attacking_team=teams.AXIS,
)
MORTAIN_SKIRMISH_DAY = Layer(
    id="mortain_skirmish_day",
    map=maps.MORTAIN,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
MORTAIN_SKIRMISH_OVERCAST = Layer(
    id="mortain_skirmish_overcast",
    map=maps.MORTAIN,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.OVERCAST,
)
MORTAIN_SKIRMISH_DUSK = Layer(
    id="mortain_skirmish_dusk",
    map=maps.MORTAIN,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DUSK,
    weather=Weather.CLEAR,
)
MORTAIN_SKIRMISH_NIGHT = Layer(
    id="mortain_skirmish_night",
    map=maps.MORTAIN,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.CLEAR,
)
ELSENBORN_WARFARE_DAY = Layer(
    id="elsenbornridge_warfare_day",
    map=maps.ELSENBORN_RIDGE,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.SNOW,
)
ELSENBORN_WARFARE_DAWN = Layer(
    id="elsenbornridge_warfare_morning",
    map=maps.ELSENBORN_RIDGE,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DAWN,
    weather=Weather.SNOW,
)
ELSENBORN_WARFARE_DUSK = Layer(
    id="elsenbornridge_warfare_evening",
    map=maps.ELSENBORN_RIDGE,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DUSK,
    weather=Weather.SNOW,
)
ELSENBORN_WARFARE_NIGHT = Layer(
    id="elsenbornridge_warfare_night",
    map=maps.ELSENBORN_RIDGE,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.SNOW,
)
ELSENBORN_OFFENSIVE_US_DAY = Layer(
    id="elsenbornridge_offensiveUS_day",
    map=maps.ELSENBORN_RIDGE,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.SNOW,
    attacking_team=teams.ALLIES,
)
ELSENBORN_OFFENSIVE_US_DAWN = Layer(
    id="elsenbornridge_offensiveUS_morning",
    map=maps.ELSENBORN_RIDGE,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAWN,
    weather=Weather.SNOW,
    attacking_team=teams.ALLIES,
)
ELSENBORN_OFFENSIVE_US_DUSK = Layer(
    id="elsenbornridge_offensiveUS_evening",
    map=maps.ELSENBORN_RIDGE,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DUSK,
    weather=Weather.SNOW,
    attacking_team=teams.ALLIES,
)
ELSENBORN_OFFENSIVE_US_NIGHT = Layer(
    id="elsenbornridge_offensiveUS_night",
    map=maps.ELSENBORN_RIDGE,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.SNOW,
    attacking_team=teams.ALLIES,
)
ELSENBORN_OFFENSIVE_GER_DAY = Layer(
    id="elsenbornridge_offensiveger_day",
    map=maps.ELSENBORN_RIDGE,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.SNOW,
    attacking_team=teams.AXIS,
)
ELSENBORN_OFFENSIVE_GER_DAWN = Layer(
    id="elsenbornridge_offensiveger_morning",
    map=maps.ELSENBORN_RIDGE,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAWN,
    weather=Weather.SNOW,
    attacking_team=teams.AXIS,
)
ELSENBORN_OFFENSIVE_GER_DUSK = Layer(
    id="elsenbornridge_offensiveger_evening",
    map=maps.ELSENBORN_RIDGE,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DUSK,
    weather=Weather.SNOW,
    attacking_team=teams.AXIS,
)
ELSENBORN_OFFENSIVE_GER_NIGHT = Layer(
    id="elsenbornridge_offensiveger_night",
    map=maps.ELSENBORN_RIDGE,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.SNOW,
    attacking_team=teams.AXIS,
)
ELSENBORN_SKIRMISH_DAY = Layer(
    id="elsenbornridge_skirmish_day",
    map=maps.ELSENBORN_RIDGE,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.SNOW,
)
ELSENBORN_SKIRMISH_DAWN = Layer(
    id="elsenbornridge_skirmish_morning",
    map=maps.ELSENBORN_RIDGE,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DAWN,
    weather=Weather.SNOW,
)
ELSENBORN_SKIRMISH_DUSK = Layer(
    id="elsenbornridge_skirmish_evening",
    map=maps.ELSENBORN_RIDGE,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DUSK,
    weather=Weather.SNOW,
)
ELSENBORN_SKIRMISH_NIGHT = Layer(
    id="elsenbornridge_skirmish_night",
    map=maps.ELSENBORN_RIDGE,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.NIGHT,
    weather=Weather.SNOW,
)
TOBRUK_WARFARE_DAY = Layer(
    id="tobruk_warfare_day",
    map=maps.TOBRUK,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
TOBRUK_WARFARE_DUSK = Layer(
    id="tobruk_warfare_dusk",
    map=maps.TOBRUK,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DUSK,
    weather=Weather.CLEAR,
)
TOBRUK_WARFARE_DAWN = Layer(
    id="tobruk_warfare_morning",
    map=maps.TOBRUK,
    game_mode=game_modes.WARFARE,
    time_of_day=TimeOfDay.DAWN,
    weather=Weather.CLEAR,
)
TOBRUK_OFFENSIVE_B8A_DAY = Layer(
    id="tobruk_offensivebritish_day",
    map=maps.TOBRUK,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.ALLIES,
)
TOBRUK_OFFENSIVE_DAK_DAY = Layer(
    id="tobruk_offensiveger_day",
    map=maps.TOBRUK,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
    attacking_team=teams.AXIS,
)
TOBRUK_OFFENSIVE_B8A_DUSK = Layer(
    id="tobruk_offensivebritish_dusk",
    map=maps.TOBRUK,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DUSK,
    weather=Weather.CLEAR,
    attacking_team=teams.ALLIES,
)
TOBRUK_OFFENSIVE_DAK_DUSK = Layer(
    id="tobruk_offensiveger_dusk",
    map=maps.TOBRUK,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DUSK,
    weather=Weather.CLEAR,
    attacking_team=teams.AXIS,
)
TOBRUK_OFFENSIVE_B8A_DAWN = Layer(
    id="tobruk_offensivebritish_morning",
    map=maps.TOBRUK,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAWN,
    weather=Weather.CLEAR,
    attacking_team=teams.ALLIES,
)
TOBRUK_OFFENSIVE_DAK_DAWN = Layer(
    id="tobruk_offensiveger_morning",
    map=maps.TOBRUK,
    game_mode=game_modes.OFFENSIVE,
    time_of_day=TimeOfDay.DAWN,
    weather=Weather.CLEAR,
    attacking_team=teams.AXIS,
)
TOBRUK_SKIRMISH_DAY = Layer(
    id="tobruk_skirmish_day",
    map=maps.TOBRUK,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DAY,
    weather=Weather.CLEAR,
)
TOBRUK_SKIRMISH_DUSK = Layer(
    id="tobruk_skirmish_dusk",
    map=maps.TOBRUK,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DUSK,
    weather=Weather.CLEAR,
)
TOBRUK_SKIRMISH_DAWN = Layer(
    id="tobruk_skirmish_morning",
    map=maps.TOBRUK,
    game_mode=game_modes.SKIRMISH,
    time_of_day=TimeOfDay.DAWN,
    weather=Weather.CLEAR,
)


def by_id(layer_id: str) -> Layer:
    return Layer.by_id(layer_id)
