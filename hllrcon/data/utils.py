from collections.abc import Hashable
from typing import Any, ClassVar, Generic, Self, TypeVar, cast

from pydantic import BaseModel

T = TypeVar("T", bound=Hashable)


class IndexedBaseModel(BaseModel, Generic[T]):
    __lookup_map: ClassVar[dict[Any, "IndexedBaseModel[Any]"]]

    id: T

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:  # noqa: ANN401
        cls.__lookup_map = {}

    def model_post_init(self, context: Any) -> None:  # noqa: ANN401, ARG002
        if self.id in self.__lookup_map:
            msg = f"{self.__class__.__name__} with ID {self.id} already exists."
            raise ValueError(msg)

        self.__lookup_map[self.id] = self

    @classmethod
    def by_id(cls, id_: T) -> Self:
        if instance := cls.__lookup_map.get(id_):
            return cast("Self", instance)

        msg = f"{cls.__name__} with ID {id_} not found."
        raise ValueError(msg)
