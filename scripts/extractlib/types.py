from scripts.extractlib.loader import Model


class LocalizationKey(Model):
    table_id: str | None = None
    namespace: str | None = None
    key: str
    source_string: str
    localized_string: str

    def __str__(self) -> str:
        return self.source_string
