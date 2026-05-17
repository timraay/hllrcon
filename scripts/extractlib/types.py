from typing import TypeAlias

from scripts.extractlib.loader import Model


class LocalizedString(Model):
    table_id: str | None = None
    namespace: str | None = None
    key: str
    source_string: str
    localized_string: str

    def __str__(self) -> str:
        return self.source_string


class CultureInvariantString(Model):
    culture_invariant_string: str | None

    def __str__(self) -> str:
        return self.culture_invariant_string or ""


String: TypeAlias = LocalizedString | CultureInvariantString
