from typing import Any, Generic

from scripts.extractlib.loader import (
    Model,
    Object,
    ObjectReference,
    ObjectT,
    ObjectT_co,
)

__all__ = ("BlueprintGeneratedClass",)


class BlueprintGeneratedClass(Object[Model], Generic[ObjectT]):
    class_default_object: ObjectReference[ObjectT]
    super: ObjectReference["BlueprintGeneratedClass[Any]"] | None = None
    super_struct: ObjectReference["BlueprintGeneratedClass[Any]"] | None = None

    def get_default_object(self, obj_type: type[ObjectT]) -> ObjectT:
        return self.class_default_object.get(obj_type)

    def get_super_struct(
        self,
        obj_type: type["BlueprintGeneratedClass[Any]"] | None = None,
    ) -> "BlueprintGeneratedClass[Any] | None":
        if (
            self.super_struct is None
            or self.super_struct.is_none()
            or self.super_struct.is_script()
        ):
            return None

        return self.super_struct.get(obj_type or BlueprintGeneratedClass[Any])

    def get_root_struct_name(self) -> str:
        if struct := self.get_super_struct():
            return struct.get_root_struct_name()

        if self.super_struct and self.super_struct.is_script():
            return self.super_struct.object_name

        return self.get_name()


class BGCReference(
    ObjectReference[BlueprintGeneratedClass[ObjectT_co]],
    Generic[ObjectT_co],
):
    def get_inst(self, obj_type: type[ObjectT_co]) -> ObjectT_co:
        bgc = self.get(BlueprintGeneratedClass[obj_type])  # type: ignore[valid-type]
        return bgc.get_default_object(obj_type)
