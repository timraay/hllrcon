from enum import StrEnum

from hllrcon.data.factions import HLLFaction


class EFaction(StrEnum):
    GER = "EFaction::Germany"
    US = "EFaction::UnitedStates"
    SOV = "EFaction::Russia"
    CW = "EFaction::Commonwealth"
    DAK = "EFaction::Ger_DAK"
    B8A = "EFaction::Brit_EighthArmy"
    CAN = "EFaction::Canadian"

    def to_hll_faction(self) -> "HLLFaction":
        for faction in HLLFaction.all():
            if faction.short_name == self.name:
                return faction
        msg = f"Unknown faction: {self.name}"
        raise ValueError(msg)
