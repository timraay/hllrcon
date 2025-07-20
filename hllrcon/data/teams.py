from hllrcon.data.utils import IndexedBaseModel


class Team(IndexedBaseModel[int]):
    name: str


ALLIES = Team(id=1, name="Allies")
AXIS = Team(id=2, name="Axis")


def by_id(team_id: int) -> Team:
    return Team.by_id(team_id)
