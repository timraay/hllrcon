from hllrcon.data import teams
from hllrcon.data.utils import IndexedBaseModel


class Faction(IndexedBaseModel[int]):
    name: str
    short_name: str
    team: teams.Team


GER = Faction(id=0, name="Germany", short_name="GER", team=teams.AXIS)
US = Faction(id=1, name="United States", short_name="US", team=teams.ALLIES)
SOV = RUS = Faction(id=2, name="Soviet Union", short_name="SOV", team=teams.AXIS)
CW = GB = Faction(id=3, name="Allies", short_name="CW", team=teams.ALLIES)
DAK = Faction(id=4, name="German Africa Corps", short_name="DAK", team=teams.AXIS)
B8A = Faction(id=5, name="British Eighth Army", short_name="B8A", team=teams.ALLIES)


def by_id(faction_id: int) -> Faction:
    return Faction.by_id(faction_id)
