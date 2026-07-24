from typing import Generic, TypeVar

from scripts.extractlib.loader import Model, Object, ObjectReference

T = TypeVar("T")

__all__ = ("DataTable", "DataTableProperties", "DataTableReference")


class DataTableProperties(Model):
    row_struct: ObjectReference


class DataTable(Object[DataTableProperties], Generic[T]):
    rows: dict[str, T]

    def get(self, row_name: str) -> T:
        if row_name not in self.rows:
            msg = f"Row {row_name} not found in data table {self.name}"
            raise KeyError(msg)
        return self.rows[row_name]


class DataTableReference(Model, Generic[T]):
    data_table: ObjectReference[DataTable[T]] | None
    row_name: str

    def is_null(self) -> bool:
        return self.data_table is None

    def get(self, row_type: type[T]) -> T:
        if self.data_table is None:
            msg = "DataTableReference is null"
            raise ValueError(msg)
        dt_obj = self.data_table.get(DataTable[row_type])  # type: ignore[valid-type]
        return dt_obj.get(self.row_name)
