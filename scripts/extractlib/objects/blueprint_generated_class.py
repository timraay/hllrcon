from typing import Generic

from scripts.extractlib.loader import Model, Object, ObjectReference, ObjectT

__all__ = ("BlueprintGeneratedClass",)


class BlueprintGeneratedClass(Object[Model], Generic[ObjectT]):
    class_default_object: ObjectReference[ObjectT]

    def get_default_object(self, obj_type: type[ObjectT]) -> ObjectT:
        return self.class_default_object.get(obj_type)
