from collections.abc import Callable, Hashable
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Self, TypeVar, cast

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")
H = TypeVar("H", bound=Hashable)


class class_cached_property(Generic[T]):  # noqa: N801
    def __init__(self, func: Callable[[type], T]) -> None:
        if TYPE_CHECKING or not isinstance(func, classmethod):  # pragma: no cover
            self.func = func
        else:
            self.func = func.__func__
        self.resolved: bool = False
        self.value: T | None = None

    def __get__(self, instance: T | None, owner: type) -> T:
        if not self.resolved:
            self.resolve(owner)
        return self.value  # type: ignore[return-value]

    def resolve(self, cls: type) -> None:
        self.value = self.func(cls)
        self.resolved = True


class IndexedBaseModel(BaseModel, Generic[H]):
    model_config = ConfigDict(
        ignored_types=(class_cached_property,),
    )
    _lookup_map: ClassVar[dict[Any, "IndexedBaseModel[Any]"]]

    id: H

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:  # noqa: ANN401
        cls._lookup_map = {}

        for value in cls.__dict__.values():
            if isinstance(value, class_cached_property):
                value.resolve(cls)

    def model_post_init(self, context: Any) -> None:  # noqa: ANN401, ARG002
        if self.id in self._lookup_map:
            msg = f"{self.__class__.__name__} with ID {self.id} already exists."
            raise ValueError(msg)

        self._lookup_map[self.id] = self

    @classmethod
    def by_id(cls, id_: H) -> Self:
        if instance := cls._lookup_map.get(id_):
            return cast("Self", instance)

        msg = f"{cls.__name__} with ID {id_} not found."
        raise ValueError(msg)

    @classmethod
    def all(cls) -> list[Self]:
        return list(cls._lookup_map.values())  # type: ignore[arg-type]
