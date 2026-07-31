from collections.abc import Iterable

from scripts.extractlib.loader import Model, Object, ObjectReference
from scripts.extractlib.objects.capture_point_conquest import CapturePointConquest


class ConquestObjectivesPhase1Properties(Model):
    game_objectives: list[ObjectReference[CapturePointConquest]]

    def get_objectives(self) -> Iterable[CapturePointConquest]:
        for objective in self.game_objectives:
            yield objective.get(CapturePointConquest)


class ConquestObjectivesPhase1(Object[ConquestObjectivesPhase1Properties]):
    pass
