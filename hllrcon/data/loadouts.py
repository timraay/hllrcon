# mypy: disable-error-code="prop-decorator"
# ruff: noqa: N802, RUF001

from enum import StrEnum
from functools import cached_property
from typing import Annotated, NamedTuple, Self

from pydantic import BaseModel, Field

from hllrcon.data._utils import (
    IndexedBaseModel,
    class_cached_property,
    model_serializer,
)
from hllrcon.data.factions import HLLFaction, HLLVFaction
from hllrcon.data.roles import HLLRole, HLLVRole
from hllrcon.data.weapons import HLLVWeapon, HLLWeapon


class HLLLoadoutId(NamedTuple):
    faction_id: int
    role_id: int
    name: str


class HLLLoadoutItem(BaseModel, frozen=True):
    name: str
    """The name of this item."""
    amount: int = 1
    """The amount of this item. For small arms, refers to the number of magazines."""

    @cached_property
    def weapon(self) -> HLLWeapon | None:
        """The weapon corresponding to this item, if any."""
        try:
            return HLLWeapon.by_id(self.name)  # type: ignore[return-value]
        except ValueError:
            return None


class HLLLoadout(IndexedBaseModel[HLLLoadoutId]):
    name: str
    faction: Annotated[
        HLLFaction,
        model_serializer(int),
    ]
    role: HLLRole
    requires_level: int = Field(ge=1, le=10)
    items: list[HLLLoadoutItem]

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(faction_id={self.faction.id!r},"
            f" role_id={self.role.id!r}, name={self.name!r})"
        )

    # @computed_field
    @cached_property  # type: ignore[misc]
    def id(self) -> HLLLoadoutId:  # type: ignore[override]
        return HLLLoadoutId(  # pragma: no cover
            faction_id=self.faction.id,
            role_id=self.role.id,
            name=self.name,
        )

    @classmethod
    def _lookup_register(cls, id_: HLLLoadoutId, instance: Self) -> None:  # ty:ignore[invalid-method-override]
        new_id = HLLLoadoutId(*id_[:2], name=id_[2].lower())
        return super()._lookup_register(new_id, instance)

    @classmethod
    def by_id(cls, id_: HLLLoadoutId | tuple[int, int, str]) -> Self:
        """Look up a loadout by its identifier.

        An identifier consists of a faction ID, role ID, and name.

        For convenience, it is suggested that you use `Loadout.by_name()` instead.

        Parameters
        ----------
        id_ : LoadoutId
            The identifier of the loadout to look up.

        Returns
        -------
        Loadout
            The loadout with the given identifier.

        Raises
        ------
        KeyError
            If no loadout with the given identifier exists.

        """
        new_id = HLLLoadoutId(*id_[:2], name=id_[2].lower())
        return super().by_id(new_id)

    @classmethod
    def by_name(cls, faction: HLLFaction, role: HLLRole, name: str) -> Self:
        """Look up a loadout by its faction, role, and name.

        Parameters
        ----------
        faction : HLLFaction
            The faction of the loadout.
        role : HLLRole
            The role of the loadout.
        name : str
            The name of the loadout.

        Returns
        -------
        Loadout
            The loadout with the given faction, role, and name.

        Raises
        ------
        ValueError
            If no loadout with the given faction, role, and name exists.

        """
        return cls.by_id(
            HLLLoadoutId(
                faction_id=faction.id,
                role_id=role.id,
                name=name,
            ),
        )

    ### INJECT "hll loadouts" START

    @class_cached_property
    @classmethod
    def GER_RIFLEMAN_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.GER,
            role=HLLRole.RIFLEMAN,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=13),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="SMALL AMMUNITION BOX", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_RIFLEMAN_STURMTRUPPEN(cls) -> "HLLLoadout":
        return cls(
            name="Sturmtruppen",
            faction=HLLFaction.GER,
            role=HLLRole.RIFLEMAN,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=12),
                HLLLoadoutItem(name="WALTHER P38", amount=10),
                HLLLoadoutItem(name="M24 STIELHANDGRANATE", amount=4),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_RIFLEMAN_PANZERGRENADIER(cls) -> "HLLLoadout":
        return cls(
            name="Panzergrenadier",
            faction=HLLFaction.GER,
            role=HLLRole.RIFLEMAN,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="GEWEHR 43", amount=8),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="EXPLOSIVE AMMO BOX", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_ASSAULT_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.GER,
            role=HLLRole.ASSAULT,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="GEWEHR 43", amount=10),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_ASSAULT_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.GER,
            role=HLLRole.ASSAULT,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="MP40", amount=8),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_ASSAULT_GRENADIER(cls) -> "HLLLoadout":
        return cls(
            name="Grenadier",
            faction=HLLFaction.GER,
            role=HLLRole.ASSAULT,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="GEWEHR 43", amount=8),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=6),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=3),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_ASSAULT_RAIDER(cls) -> "HLLLoadout":
        return cls(
            name="Raider",
            faction=HLLFaction.GER,
            role=HLLRole.ASSAULT,
            requires_level=9,
            items=[
                HLLLoadoutItem(name="STG44", amount=6),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=1),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="SATCHEL", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_AUTOMATIC_RIFLEMAN_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.GER,
            role=HLLRole.AUTOMATIC_RIFLEMAN,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="STG44", amount=6),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_AUTOMATIC_RIFLEMAN_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.GER,
            role=HLLRole.AUTOMATIC_RIFLEMAN,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="MP40", amount=10),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_AUTOMATIC_RIFLEMAN_PARATROOPER(cls) -> "HLLLoadout":
        return cls(
            name="Paratrooper",
            faction=HLLFaction.GER,
            role=HLLRole.AUTOMATIC_RIFLEMAN,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="FG42", amount=5),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_MEDIC_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.GER,
            role=HLLRole.MEDIC,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=8),
                HLLLoadoutItem(name="WALTHER P38", amount=6),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=4),
                HLLLoadoutItem(name="MORPHINE AMPOULE", amount=20),
                HLLLoadoutItem(name="BANDAGE", amount=20),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_MEDIC_SANITATER(cls) -> "HLLLoadout":
        return cls(
            name="Sanitater",
            faction=HLLFaction.GER,
            role=HLLRole.MEDIC,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="LUGER P08", amount=16),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=6),
                HLLLoadoutItem(name="MORPHINE AMPOULE", amount=20),
                HLLLoadoutItem(name="BANDAGE", amount=20),
                HLLLoadoutItem(name="MEDICAL SUPPLIES", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_SPOTTER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.GER,
            role=HLLRole.SPOTTER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="MP40", amount=8),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="S-MINE", amount=1),
                HLLLoadoutItem(name="SMALL AMMUNITION BOX", amount=1),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="DIENSTGLAS 6×30", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_SPOTTER_SCOUT(cls) -> "HLLLoadout":
        return cls(
            name="Scout",
            faction=HLLFaction.GER,
            role=HLLRole.SPOTTER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=10),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="DIENSTGLAS 6×30", amount=1),
                HLLLoadoutItem(name="FLARE GUN", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_SUPPORT_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.GER,
            role=HLLRole.SUPPORT,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=12),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="SUPPLIES", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_SUPPORT_AMMO_CARRIER(cls) -> "HLLLoadout":
        return cls(
            name="Ammo Carrier",
            faction=HLLFaction.GER,
            role=HLLRole.SUPPORT,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="MP40", amount=6),
                HLLLoadoutItem(name="SUPPLIES", amount=1),
                HLLLoadoutItem(name="SMALL AMMUNITION BOX", amount=1),
                HLLLoadoutItem(name="EXPLOSIVE AMMO BOX", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_SUPPORT_FLAMMENWERFER(cls) -> "HLLLoadout":
        return cls(
            name="Flammenwerfer",
            faction=HLLFaction.GER,
            role=HLLRole.SUPPORT,
            requires_level=8,
            items=[
                HLLLoadoutItem(name="FLAMMENWERFER 41", amount=1),
                HLLLoadoutItem(name="WALTHER P38", amount=4),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="SUPPLIES", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_MACHINE_GUNNER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.GER,
            role=HLLRole.MACHINE_GUNNER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="MG34", amount=10),
                HLLLoadoutItem(name="WALTHER P38", amount=6),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_MACHINE_GUNNER_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.GER,
            role=HLLRole.MACHINE_GUNNER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="MG42", amount=6),
                HLLLoadoutItem(name="LUGER P08", amount=6),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_ANTI_TANK_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.GER,
            role=HLLRole.ANTI_TANK,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=12),
                HLLLoadoutItem(name="PANZERSCHRECK", amount=2),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_ANTI_TANK_GUN_CREW(cls) -> "HLLLoadout":
        return cls(
            name="Gun Crew",
            faction=HLLFaction.GER,
            role=HLLRole.ANTI_TANK,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=12),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="PAK 40", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_ANTI_TANK_AMBUSHER(cls) -> "HLLLoadout":
        return cls(
            name="Ambusher",
            faction=HLLFaction.GER,
            role=HLLRole.ANTI_TANK,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="MP40", amount=6),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="SATCHEL", amount=1),
                HLLLoadoutItem(name="TELLERMINE 43", amount=4),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_ENGINEER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.GER,
            role=HLLRole.ENGINEER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=12),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WRENCH", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="TORCH", amount=1),
                HLLLoadoutItem(name="S-MINE", amount=2),
                HLLLoadoutItem(name="TELLERMINE 43", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_ENGINEER_PIONIER(cls) -> "HLLLoadout":
        return cls(
            name="Pionier",
            faction=HLLFaction.GER,
            role=HLLRole.ENGINEER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="MP40", amount=6),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="S-MINE", amount=2),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="SATCHEL", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_OFFICER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.GER,
            role=HLLRole.OFFICER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="MP40", amount=8),
                HLLLoadoutItem(name="LUGER P08", amount=6),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="DIENSTGLAS 6×30", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_OFFICER_POINT_MAN(cls) -> "HLLLoadout":
        return cls(
            name="Point Man",
            faction=HLLFaction.GER,
            role=HLLRole.OFFICER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="GEWEHR 43", amount=10),
                HLLLoadoutItem(name="WALTHER P38", amount=4),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="DIENSTGLAS 6×30", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_OFFICER_NCO(cls) -> "HLLLoadout":
        return cls(
            name="NCO",
            faction=HLLFaction.GER,
            role=HLLRole.OFFICER,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=13),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=3),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=3),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="DIENSTGLAS 6×30", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_SNIPER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.GER,
            role=HLLRole.SNIPER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="KARABINER 98K x8", amount=19),
                HLLLoadoutItem(name="WALTHER P38", amount=6),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_SNIPER_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.GER,
            role=HLLRole.SNIPER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="FG42 x4", amount=12),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="S-MINE", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_CREWMAN_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.GER,
            role=HLLRole.CREWMAN,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="WALTHER P38", amount=6),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
                HLLLoadoutItem(name="EXTERIOR CUSTOMIZATION", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_CREWMAN_MECHANIC(cls) -> "HLLLoadout":
        return cls(
            name="Mechanic",
            faction=HLLFaction.GER,
            role=HLLRole.CREWMAN,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="WALTHER P38", amount=6),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="TORCH", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
                HLLLoadoutItem(name="EXTERIOR CUSTOMIZATION", amount=1),
                HLLLoadoutItem(name="SUPPLIES", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_CREWMAN_TECHNICIAN(cls) -> "HLLLoadout":
        return cls(
            name="Technician",
            faction=HLLFaction.GER,
            role=HLLRole.CREWMAN,
            requires_level=7,
            items=[
                HLLLoadoutItem(name="WALTHER P38", amount=6),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WRENCH", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
                HLLLoadoutItem(name="EXTERIOR CUSTOMIZATION", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_TANK_COMMANDER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.GER,
            role=HLLRole.TANK_COMMANDER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="MP40", amount=4),
                HLLLoadoutItem(name="LUGER P08", amount=6),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="DIENSTGLAS 6×30", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
                HLLLoadoutItem(name="EXTERIOR CUSTOMIZATION", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_TANK_COMMANDER_MECHANIC(cls) -> "HLLLoadout":
        return cls(
            name="Mechanic",
            faction=HLLFaction.GER,
            role=HLLRole.TANK_COMMANDER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="LUGER P08", amount=6),
                HLLLoadoutItem(name="TORCH", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="DIENSTGLAS 6×30", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
                HLLLoadoutItem(name="EXTERIOR CUSTOMIZATION", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_COMMANDER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.GER,
            role=HLLRole.COMMANDER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="MP40", amount=6),
                HLLLoadoutItem(name="LUGER P08", amount=4),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="DIENSTGLAS 6×30", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_COMMANDER_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.GER,
            role=HLLRole.COMMANDER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="GEWEHR 43", amount=12),
                HLLLoadoutItem(name="WALTHER P38", amount=4),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="DIENSTGLAS 6×30", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_ARTILLERY_OBSERVER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.GER,
            role=HLLRole.ARTILLERY_OBSERVER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="MP40", amount=8),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="DIENSTGLAS 6×30", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FLARE GUN", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_ARTILLERY_OBSERVER_NCO(cls) -> "HLLLoadout":
        return cls(
            name="NCO",
            faction=HLLFaction.GER,
            role=HLLRole.ARTILLERY_OBSERVER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=10),
                HLLLoadoutItem(name="WALTHER P38", amount=4),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="S-MINE", amount=1),
                HLLLoadoutItem(name="DIENSTGLAS 6×30", amount=1),
                HLLLoadoutItem(name="FLARE GUN", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_OPERATOR_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.GER,
            role=HLLRole.OPERATOR,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=12),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WRENCH", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="TORCH", amount=1),
                HLLLoadoutItem(name="S-MINE", amount=1),
                HLLLoadoutItem(name="TELLERMINE 43", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_OPERATOR_PIONEER(cls) -> "HLLLoadout":
        return cls(
            name="Pioneer",
            faction=HLLFaction.GER,
            role=HLLRole.OPERATOR,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="MP40", amount=6),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="S-MINE", amount=2),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="TORCH", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_GUNNER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.GER,
            role=HLLRole.GUNNER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=12),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="SUPPLIES", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=2),
            ],
        )

    @class_cached_property
    @classmethod
    def GER_GUNNER_AMMO_CARRIER(cls) -> "HLLLoadout":
        return cls(
            name="Ammo Carrier",
            faction=HLLFaction.GER,
            role=HLLRole.GUNNER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="MP40", amount=6),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="SUPPLIES", amount=1),
                HLLLoadoutItem(name="EXPLOSIVE AMMO BOX", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_RIFLEMAN_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.US,
            role=HLLRole.RIFLEMAN,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="M1 GARAND", amount=19),
                HLLLoadoutItem(name="MK2 GRENADE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="SMALL AMMUNITION BOX", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_RIFLEMAN_POINT_MAN(cls) -> "HLLLoadout":
        return cls(
            name="Point Man",
            faction=HLLFaction.US,
            role=HLLRole.RIFLEMAN,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="M1 CARBINE", amount=12),
                HLLLoadoutItem(name="MK2 GRENADE", amount=4),
                HLLLoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_ASSAULT_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.US,
            role=HLLRole.ASSAULT,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="M1A1 THOMPSON", amount=6),
                HLLLoadoutItem(name="MK2 GRENADE", amount=2),
                HLLLoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_ASSAULT_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.US,
            role=HLLRole.ASSAULT,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="M97 TRENCH GUN", amount=6),
                HLLLoadoutItem(name="MK2 GRENADE", amount=2),
                HLLLoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_ASSAULT_GRENADIER(cls) -> "HLLLoadout":
        return cls(
            name="Grenadier",
            faction=HLLFaction.US,
            role=HLLRole.ASSAULT,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="M1A1 THOMPSON", amount=6),
                HLLLoadoutItem(name="MK2 GRENADE", amount=6),
                HLLLoadoutItem(name="M18 SMOKE GRENADE", amount=4),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_ASSAULT_RAIDER(cls) -> "HLLLoadout":
        return cls(
            name="Raider",
            faction=HLLFaction.US,
            role=HLLRole.ASSAULT,
            requires_level=9,
            items=[
                HLLLoadoutItem(name="M3 GREASE GUN", amount=6),
                HLLLoadoutItem(name="MK2 GRENADE", amount=1),
                HLLLoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                HLLLoadoutItem(name="SATCHEL", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_AUTOMATIC_RIFLEMAN_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.US,
            role=HLLRole.AUTOMATIC_RIFLEMAN,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="M1918A2 BAR", amount=10),
                HLLLoadoutItem(name="MK2 GRENADE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_AUTOMATIC_RIFLEMAN_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.US,
            role=HLLRole.AUTOMATIC_RIFLEMAN,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="M1A1 THOMPSON", amount=6),
                HLLLoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_MEDIC_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.US,
            role=HLLRole.MEDIC,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="M1 CARBINE", amount=3),
                HLLLoadoutItem(name="COLT M1911", amount=6),
                HLLLoadoutItem(name="M18 SMOKE GRENADE", amount=4),
                HLLLoadoutItem(name="MORPHINE SYRETTE", amount=20),
                HLLLoadoutItem(name="BANDAGE", amount=20),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_MEDIC_CORPSMAN(cls) -> "HLLLoadout":
        return cls(
            name="Corpsman",
            faction=HLLFaction.US,
            role=HLLRole.MEDIC,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="COLT M1911", amount=16),
                HLLLoadoutItem(name="M18 SMOKE GRENADE", amount=6),
                HLLLoadoutItem(name="MORPHINE SYRETTE", amount=20),
                HLLLoadoutItem(name="BANDAGE", amount=20),
                HLLLoadoutItem(name="MEDICAL SUPPLIES", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_SPOTTER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.US,
            role=HLLRole.SPOTTER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="M1A1 THOMPSON", amount=6),
                HLLLoadoutItem(name="MK2 GRENADE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="M2 AP MINE", amount=1),
                HLLLoadoutItem(name="SMALL AMMUNITION BOX", amount=1),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="WESTINGHOUSE M3 6×30", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_SPOTTER_SCOUT(cls) -> "HLLLoadout":
        return cls(
            name="Scout",
            faction=HLLFaction.US,
            role=HLLRole.SPOTTER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="M1 CARBINE", amount=12),
                HLLLoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="WESTINGHOUSE M3 6×30", amount=1),
                HLLLoadoutItem(name="FLARE GUN", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_SUPPORT_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.US,
            role=HLLRole.SUPPORT,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="M1 GARAND", amount=12),
                HLLLoadoutItem(name="MK2 GRENADE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="SUPPLIES", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_SUPPORT_AMMO_CARRIER(cls) -> "HLLLoadout":
        return cls(
            name="Ammo Carrier",
            faction=HLLFaction.US,
            role=HLLRole.SUPPORT,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="M3 GREASE GUN", amount=6),
                HLLLoadoutItem(name="SUPPLIES", amount=1),
                HLLLoadoutItem(name="SMALL AMMUNITION BOX", amount=1),
                HLLLoadoutItem(name="EXPLOSIVE AMMO BOX", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_SUPPORT_FLAMER(cls) -> "HLLLoadout":
        return cls(
            name="Flamer",
            faction=HLLFaction.US,
            role=HLLRole.SUPPORT,
            requires_level=8,
            items=[
                HLLLoadoutItem(name="M2 FLAMETHROWER", amount=1),
                HLLLoadoutItem(name="COLT M1911", amount=4),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                HLLLoadoutItem(name="SUPPLIES", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_MACHINE_GUNNER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.US,
            role=HLLRole.MACHINE_GUNNER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="BROWNING M1919", amount=6),
                HLLLoadoutItem(name="COLT M1911", amount=6),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_MACHINE_GUNNER_FIRE_SUPPORT(cls) -> "HLLLoadout":
        return cls(
            name="Fire Support",
            faction=HLLFaction.US,
            role=HLLRole.MACHINE_GUNNER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="M1918A2 BAR", amount=14),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_ANTI_TANK_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.US,
            role=HLLRole.ANTI_TANK,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="M1 GARAND", amount=12),
                HLLLoadoutItem(name="BAZOOKA", amount=2),
                HLLLoadoutItem(name="MK2 GRENADE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_ANTI_TANK_GUN_CREW(cls) -> "HLLLoadout":
        return cls(
            name="Gun Crew",
            faction=HLLFaction.US,
            role=HLLRole.ANTI_TANK,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="M1 GARAND", amount=12),
                HLLLoadoutItem(name="MK2 GRENADE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="57MM M1", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_ANTI_TANK_AMBUSHER(cls) -> "HLLLoadout":
        return cls(
            name="Ambusher",
            faction=HLLFaction.US,
            role=HLLRole.ANTI_TANK,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="M1A1 THOMPSON", amount=6),
                HLLLoadoutItem(name="MK2 GRENADE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="SATCHEL", amount=1),
                HLLLoadoutItem(name="M1A1 AT MINE", amount=4),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_ENGINEER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.US,
            role=HLLRole.ENGINEER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="M1 CARBINE", amount=12),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WRENCH", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="TORCH", amount=1),
                HLLLoadoutItem(name="M2 AP MINE", amount=2),
                HLLLoadoutItem(name="M1A1 AT MINE", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_ENGINEER_SAPPER(cls) -> "HLLLoadout":
        return cls(
            name="Sapper",
            faction=HLLFaction.US,
            role=HLLRole.ENGINEER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="M97 TRENCH GUN", amount=6),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="M2 AP MINE", amount=2),
                HLLLoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                HLLLoadoutItem(name="SATCHEL", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_ENGINEER_FIELD_ENGINEER(cls) -> "HLLLoadout":
        return cls(
            name="Field Engineer",
            faction=HLLFaction.US,
            role=HLLRole.ENGINEER,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="M3 GREASE GUN", amount=6),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WRENCH", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="MK2 GRENADE", amount=2),
                HLLLoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                HLLLoadoutItem(name="TORCH", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_OFFICER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.US,
            role=HLLRole.OFFICER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="M1A1 THOMPSON", amount=6),
                HLLLoadoutItem(name="COLT M1911", amount=4),
                HLLLoadoutItem(name="MK2 GRENADE", amount=2),
                HLLLoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="WESTINGHOUSE M3 6×30", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_OFFICER_POINT_MAN(cls) -> "HLLLoadout":
        return cls(
            name="Point Man",
            faction=HLLFaction.US,
            role=HLLRole.OFFICER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="M1 CARBINE", amount=12),
                HLLLoadoutItem(name="COLT M1911", amount=4),
                HLLLoadoutItem(name="MK2 GRENADE", amount=2),
                HLLLoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="WESTINGHOUSE M3 6×30", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_OFFICER_NCO(cls) -> "HLLLoadout":
        return cls(
            name="NCO",
            faction=HLLFaction.US,
            role=HLLRole.OFFICER,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="M1 GARAND", amount=19),
                HLLLoadoutItem(name="MK2 GRENADE", amount=3),
                HLLLoadoutItem(name="M18 SMOKE GRENADE", amount=3),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="WESTINGHOUSE M3 6×30", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_SNIPER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.US,
            role=HLLRole.SNIPER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="M1903 SPRINGFIELD", amount=17),
                HLLLoadoutItem(name="COLT M1911", amount=6),
                HLLLoadoutItem(name="MK2 GRENADE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_SNIPER_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.US,
            role=HLLRole.SNIPER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="M1903 SPRINGFIELD", amount=17),
                HLLLoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                HLLLoadoutItem(name="M2 AP MINE", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_CREWMAN_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.US,
            role=HLLRole.CREWMAN,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="COLT M1911", amount=4),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
                HLLLoadoutItem(name="EXTERIOR CUSTOMIZATION", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_CREWMAN_MECHANIC(cls) -> "HLLLoadout":
        return cls(
            name="Mechanic",
            faction=HLLFaction.US,
            role=HLLRole.CREWMAN,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="COLT M1911", amount=4),
                HLLLoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                HLLLoadoutItem(name="TORCH", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
                HLLLoadoutItem(name="EXTERIOR CUSTOMIZATION", amount=1),
                HLLLoadoutItem(name="SUPPLIES", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_CREWMAN_TECHNICIAN(cls) -> "HLLLoadout":
        return cls(
            name="Technician",
            faction=HLLFaction.US,
            role=HLLRole.CREWMAN,
            requires_level=7,
            items=[
                HLLLoadoutItem(name="COLT M1911", amount=4),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WRENCH", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
                HLLLoadoutItem(name="EXTERIOR CUSTOMIZATION", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_TANK_COMMANDER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.US,
            role=HLLRole.TANK_COMMANDER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="M1A1 THOMPSON", amount=4),
                HLLLoadoutItem(name="COLT M1911", amount=4),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WESTINGHOUSE M3 6×30", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
                HLLLoadoutItem(name="EXTERIOR CUSTOMIZATION", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_TANK_COMMANDER_MECHANIC(cls) -> "HLLLoadout":
        return cls(
            name="Mechanic",
            faction=HLLFaction.US,
            role=HLLRole.TANK_COMMANDER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="COLT M1911", amount=6),
                HLLLoadoutItem(name="TORCH", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WESTINGHOUSE M3 6×30", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
                HLLLoadoutItem(name="EXTERIOR CUSTOMIZATION", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_COMMANDER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.US,
            role=HLLRole.COMMANDER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="M1A1 THOMPSON", amount=6),
                HLLLoadoutItem(name="COLT M1911", amount=4),
                HLLLoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="WESTINGHOUSE M3 6×30", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_COMMANDER_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.US,
            role=HLLRole.COMMANDER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="M1 GARAND", amount=12),
                HLLLoadoutItem(name="COLT M1911", amount=4),
                HLLLoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="WESTINGHOUSE M3 6×30", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_ARTILLERY_OBSERVER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.US,
            role=HLLRole.ARTILLERY_OBSERVER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="M1A1 THOMPSON", amount=6),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="MK2 GRENADE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="WESTINGHOUSE M3 6×30", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FLARE GUN", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_ARTILLERY_OBSERVER_NCO(cls) -> "HLLLoadout":
        return cls(
            name="NCO",
            faction=HLLFaction.US,
            role=HLLRole.ARTILLERY_OBSERVER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="M1 CARBINE", amount=12),
                HLLLoadoutItem(name="COLT M1911", amount=4),
                HLLLoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="M2 AP MINE", amount=1),
                HLLLoadoutItem(name="WESTINGHOUSE M3 6×30", amount=1),
                HLLLoadoutItem(name="FLARE GUN", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_OPERATOR_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.US,
            role=HLLRole.OPERATOR,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="M1 CARBINE", amount=12),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WRENCH", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="TORCH", amount=1),
                HLLLoadoutItem(name="M2 AP MINE", amount=1),
                HLLLoadoutItem(name="M1A1 AT MINE", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_OPERATOR_PIONEER(cls) -> "HLLLoadout":
        return cls(
            name="Pioneer",
            faction=HLLFaction.US,
            role=HLLRole.OPERATOR,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="M97 TRENCH GUN", amount=6),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="M2 AP MINE", amount=2),
                HLLLoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="TORCH", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_GUNNER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.US,
            role=HLLRole.GUNNER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="M1 GARAND", amount=12),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="MK2 GRENADE", amount=2),
                HLLLoadoutItem(name="SUPPLIES", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def US_GUNNER_AMMO_CARRIER(cls) -> "HLLLoadout":
        return cls(
            name="Ammo Carrier",
            faction=HLLFaction.US,
            role=HLLRole.GUNNER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="M3 GREASE GUN", amount=6),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="M18 SMOKE GRENADE", amount=2),
                HLLLoadoutItem(name="SUPPLIES", amount=1),
                HLLLoadoutItem(name="EXPLOSIVE AMMO BOX", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="M3 KNIFE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_RIFLEMAN_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.SOV,
            role=HLLRole.RIFLEMAN,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="MOSIN NAGANT 1891", amount=12),
                HLLLoadoutItem(name="RG-42 GRENADE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="SMALL AMMUNITION BOX", amount=1),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_RIFLEMAN_GRENADIER(cls) -> "HLLLoadout":
        return cls(
            name="Grenadier",
            faction=HLLFaction.SOV,
            role=HLLRole.RIFLEMAN,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="MOSIN NAGANT M38", amount=12),
                HLLLoadoutItem(name="RG-42 GRENADE", amount=4),
                HLLLoadoutItem(name="RDG-2 SMOKE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="EXPLOSIVE AMMO BOX", amount=1),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_RIFLEMAN_FLAMER(cls) -> "HLLLoadout":
        return cls(
            name="Flamer",
            faction=HLLFaction.SOV,
            role=HLLRole.RIFLEMAN,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="MOSIN NAGANT M38", amount=12),
                HLLLoadoutItem(name="MOLOTOV", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="EXPLOSIVE AMMO BOX", amount=1),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_ASSAULT_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.SOV,
            role=HLLRole.ASSAULT,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="PPSH 41", amount=14),
                HLLLoadoutItem(name="RG-42 GRENADE", amount=2),
                HLLLoadoutItem(name="RDG-2 SMOKE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_ASSAULT_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.SOV,
            role=HLLRole.ASSAULT,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="PPSH 41 W/DRUM", amount=5),
                HLLLoadoutItem(name="RG-42 GRENADE", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_ASSAULT_GRENADIER(cls) -> "HLLLoadout":
        return cls(
            name="Grenadier",
            faction=HLLFaction.SOV,
            role=HLLRole.ASSAULT,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="SVT40", amount=12),
                HLLLoadoutItem(name="RG-42 GRENADE", amount=6),
                HLLLoadoutItem(name="RDG-2 SMOKE", amount=3),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_ASSAULT_FLAMER(cls) -> "HLLLoadout":
        return cls(
            name="Flamer",
            faction=HLLFaction.SOV,
            role=HLLRole.ASSAULT,
            requires_level=9,
            items=[
                HLLLoadoutItem(name="PPSH 41 W/DRUM", amount=5),
                HLLLoadoutItem(name="MOLOTOV", amount=2),
                HLLLoadoutItem(name="SATCHEL CHARGE", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_AUTOMATIC_RIFLEMAN_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.SOV,
            role=HLLRole.AUTOMATIC_RIFLEMAN,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="PPSH 41 W/DRUM", amount=5),
                HLLLoadoutItem(name="RG-42 GRENADE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_AUTOMATIC_RIFLEMAN_FLAMER(cls) -> "HLLLoadout":
        return cls(
            name="Flamer",
            faction=HLLFaction.SOV,
            role=HLLRole.AUTOMATIC_RIFLEMAN,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="PPSH 41 W/DRUM", amount=5),
                HLLLoadoutItem(name="MOLOTOV", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_MEDIC_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.SOV,
            role=HLLRole.MEDIC,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="MOSIN NAGANT 91/30", amount=8),
                HLLLoadoutItem(name="NAGANT M1895", amount=7),
                HLLLoadoutItem(name="RDG-2 SMOKE", amount=4),
                HLLLoadoutItem(name="REVIVE", amount=20),
                HLLLoadoutItem(name="BANDAGE", amount=20),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_MEDIC_SANITATI(cls) -> "HLLLoadout":
        return cls(
            name="Sanitati",
            faction=HLLFaction.SOV,
            role=HLLRole.MEDIC,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="NAGANT M1895", amount=18),
                HLLLoadoutItem(name="RDG-2 SMOKE", amount=6),
                HLLLoadoutItem(name="REVIVE", amount=20),
                HLLLoadoutItem(name="BANDAGE", amount=20),
                HLLLoadoutItem(name="MEDICAL SUPPLIES", amount=1),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_SPOTTER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.SOV,
            role=HLLRole.SPOTTER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="PPSH 41", amount=8),
                HLLLoadoutItem(name="RG-42 GRENADE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="POMZ AP MINE", amount=1),
                HLLLoadoutItem(name="SMALL AMMUNITION BOX", amount=1),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="RKKA 8×40", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_SPOTTER_SCOUT(cls) -> "HLLLoadout":
        return cls(
            name="Scout",
            faction=HLLFaction.SOV,
            role=HLLRole.SPOTTER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="SVT40", amount=12),
                HLLLoadoutItem(name="RDG-2 SMOKE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="RKKA 8×40", amount=1),
                HLLLoadoutItem(name="FLARE GUN", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_SUPPORT_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.SOV,
            role=HLLRole.SUPPORT,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="MOSIN NAGANT 91/30", amount=12),
                HLLLoadoutItem(name="RG-42 GRENADE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="SUPPLIES", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_SUPPORT_AMMO_CARRIER(cls) -> "HLLLoadout":
        return cls(
            name="Ammo Carrier",
            faction=HLLFaction.SOV,
            role=HLLRole.SUPPORT,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="SVT40", amount=12),
                HLLLoadoutItem(name="SUPPLIES", amount=1),
                HLLLoadoutItem(name="SMALL AMMUNITION BOX", amount=1),
                HLLLoadoutItem(name="EXPLOSIVE AMMO BOX", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_SUPPORT_FLAMER(cls) -> "HLLLoadout":
        return cls(
            name="Flamer",
            faction=HLLFaction.SOV,
            role=HLLRole.SUPPORT,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="MOSIN NAGANT M38", amount=12),
                HLLLoadoutItem(name="NAGANT M1895", amount=4),
                HLLLoadoutItem(name="MOLOTOV", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="SUPPLIES", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_MACHINE_GUNNER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.SOV,
            role=HLLRole.MACHINE_GUNNER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="DP-27", amount=12),
                HLLLoadoutItem(name="NAGANT M1895", amount=6),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_ANTI_TANK_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.SOV,
            role=HLLRole.ANTI_TANK,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="MOSIN NAGANT 91/30", amount=16),
                HLLLoadoutItem(name="PTRS-41", amount=8),
                HLLLoadoutItem(name="RG-42 GRENADE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_ANTI_TANK_GUN_CREW(cls) -> "HLLLoadout":
        return cls(
            name="Gun Crew",
            faction=HLLFaction.SOV,
            role=HLLRole.ANTI_TANK,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="MOSIN NAGANT 91/30", amount=12),
                HLLLoadoutItem(name="RG-42 GRENADE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="ZiS-2", amount=1),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_ANTI_TANK_AMBUSHER(cls) -> "HLLLoadout":
        return cls(
            name="Ambusher",
            faction=HLLFaction.SOV,
            role=HLLRole.ANTI_TANK,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="PPSH 41", amount=8),
                HLLLoadoutItem(name="RG-42 GRENADE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="SATCHEL CHARGE", amount=1),
                HLLLoadoutItem(name="TM-35 AT MINE", amount=4),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_ANTI_TANK_LEND_LEASE(cls) -> "HLLLoadout":
        return cls(
            name="Lend Lease",
            faction=HLLFaction.SOV,
            role=HLLRole.ANTI_TANK,
            requires_level=8,
            items=[
                HLLLoadoutItem(name="PPSH 41", amount=8),
                HLLLoadoutItem(name="BAZOOKA", amount=2),
                HLLLoadoutItem(name="RG-42 GRENADE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_ENGINEER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.SOV,
            role=HLLRole.ENGINEER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="MOSIN NAGANT 91/30", amount=12),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WRENCH", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="TORCH", amount=1),
                HLLLoadoutItem(name="POMZ AP MINE", amount=2),
                HLLLoadoutItem(name="TM-35 AT MINE", amount=1),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_ENGINEER_SAPPER(cls) -> "HLLLoadout":
        return cls(
            name="Sapper",
            faction=HLLFaction.SOV,
            role=HLLRole.ENGINEER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="MOSIN NAGANT 91/30", amount=6),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="POMZ AP MINE", amount=2),
                HLLLoadoutItem(name="RDG-2 SMOKE", amount=2),
                HLLLoadoutItem(name="SATCHEL CHARGE", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_OFFICER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.SOV,
            role=HLLRole.OFFICER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="PPSH 41", amount=8),
                HLLLoadoutItem(name="TOKAREV TT33", amount=6),
                HLLLoadoutItem(name="RG-42 GRENADE", amount=2),
                HLLLoadoutItem(name="RDG-2 SMOKE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="RKKA 8×40", amount=1),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_OFFICER_JUNIOR_SERGEANT(cls) -> "HLLLoadout":
        return cls(
            name="Junior Sergeant",
            faction=HLLFaction.SOV,
            role=HLLRole.OFFICER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="SVT40", amount=12),
                HLLLoadoutItem(name="TOKAREV TT33", amount=4),
                HLLLoadoutItem(name="RG-42 GRENADE", amount=2),
                HLLLoadoutItem(name="RDG-2 SMOKE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="RKKA 8×40", amount=1),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_OFFICER_STARSHINA(cls) -> "HLLLoadout":
        return cls(
            name="Starshina",
            faction=HLLFaction.SOV,
            role=HLLRole.OFFICER,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="PPSH 41 W/DRUM", amount=5),
                HLLLoadoutItem(name="RG-42 GRENADE", amount=2),
                HLLLoadoutItem(name="RDG-2 SMOKE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="RKKA 8×40", amount=1),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_SNIPER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.SOV,
            role=HLLRole.SNIPER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="SCOPED MOSIN NAGANT 91/30", amount=17),
                HLLLoadoutItem(name="NAGANT M1895", amount=6),
                HLLLoadoutItem(name="RG-42 GRENADE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_SNIPER_AUTOMATIC_MARKSMAN(cls) -> "HLLLoadout":
        return cls(
            name="Automatic Marksman",
            faction=HLLFaction.SOV,
            role=HLLRole.SNIPER,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="SCOPED SVT40", amount=12),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_CREWMAN_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.SOV,
            role=HLLRole.CREWMAN,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="NAGANT M1895", amount=4),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
                HLLLoadoutItem(name="EXTERIOR CUSTOMIZATION", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_CREWMAN_MECHANIC(cls) -> "HLLLoadout":
        return cls(
            name="Mechanic",
            faction=HLLFaction.SOV,
            role=HLLRole.CREWMAN,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="NAGANT M1895", amount=6),
                HLLLoadoutItem(name="RDG-2 SMOKE", amount=2),
                HLLLoadoutItem(name="TORCH", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
                HLLLoadoutItem(name="SUPPLIES", amount=1),
                HLLLoadoutItem(name="EXTERIOR CUSTOMIZATION", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_CREWMAN_TECHNICIAN(cls) -> "HLLLoadout":
        return cls(
            name="Technician",
            faction=HLLFaction.SOV,
            role=HLLRole.CREWMAN,
            requires_level=7,
            items=[
                HLLLoadoutItem(name="NAGANT M1895", amount=4),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WRENCH", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
                HLLLoadoutItem(name="EXTERIOR CUSTOMIZATION", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_TANK_COMMANDER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.SOV,
            role=HLLRole.TANK_COMMANDER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="PPSH 41", amount=4),
                HLLLoadoutItem(name="NAGANT M1895", amount=4),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="RKKA 8×40", amount=1),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
                HLLLoadoutItem(name="EXTERIOR CUSTOMIZATION", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_TANK_COMMANDER_MECHANIC(cls) -> "HLLLoadout":
        return cls(
            name="Mechanic",
            faction=HLLFaction.SOV,
            role=HLLRole.TANK_COMMANDER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="TOKAREV TT33", amount=6),
                HLLLoadoutItem(name="TORCH", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="RKKA 8×40", amount=1),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
                HLLLoadoutItem(name="EXTERIOR CUSTOMIZATION", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_COMMANDER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.SOV,
            role=HLLRole.COMMANDER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="PPSH 41", amount=10),
                HLLLoadoutItem(name="NAGANT M1895", amount=4),
                HLLLoadoutItem(name="RDG-2 SMOKE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="RKKA 8×40", amount=1),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_ARTILLERY_OBSERVER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.SOV,
            role=HLLRole.ARTILLERY_OBSERVER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="PPSH 41", amount=8),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="RG-42 GRENADE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="RKKA 8×40", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FLARE GUN", amount=1),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_ARTILLERY_OBSERVER_NCO(cls) -> "HLLLoadout":
        return cls(
            name="NCO",
            faction=HLLFaction.SOV,
            role=HLLRole.ARTILLERY_OBSERVER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="SVT40", amount=12),
                HLLLoadoutItem(name="TOKAREV TT33", amount=12),
                HLLLoadoutItem(name="RDG-2 SMOKE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="POMZ AP MINE", amount=1),
                HLLLoadoutItem(name="RKKA 8×40", amount=1),
                HLLLoadoutItem(name="FLARE GUN", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_OPERATOR_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.SOV,
            role=HLLRole.OPERATOR,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="MOSIN NAGANT M38", amount=12),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WRENCH", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="TORCH", amount=1),
                HLLLoadoutItem(name="POMZ AP MINE", amount=1),
                HLLLoadoutItem(name="TM-35 AT MINE", amount=1),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_OPERATOR_PIONEER(cls) -> "HLLLoadout":
        return cls(
            name="Pioneer",
            faction=HLLFaction.SOV,
            role=HLLRole.OPERATOR,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="MOSIN NAGANT 91/30", amount=12),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="POMZ AP MINE", amount=2),
                HLLLoadoutItem(name="RDG-2 SMOKE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="TORCH", amount=1),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_GUNNER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.SOV,
            role=HLLRole.GUNNER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="MOSIN NAGANT M38", amount=12),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="RG-42 GRENADE", amount=2),
                HLLLoadoutItem(name="SUPPLIES", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def SOV_GUNNER_AMMO_CARRIER(cls) -> "HLLLoadout":
        return cls(
            name="Ammo Carrier",
            faction=HLLFaction.SOV,
            role=HLLRole.GUNNER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="SVT40", amount=12),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="RDG-2 SMOKE", amount=2),
                HLLLoadoutItem(name="SUPPLIES", amount=1),
                HLLLoadoutItem(name="EXPLOSIVE AMMO BOX", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="MPL-50 SPADE", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_RIFLEMAN_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CW,
            role=HLLRole.RIFLEMAN,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="SMLE No.1 Mk III", amount=6),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Small Ammunition Box", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_RIFLEMAN_GRENADIER(cls) -> "HLLLoadout":
        return cls(
            name="Grenadier",
            faction=HLLFaction.CW,
            role=HLLRole.RIFLEMAN,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Rifle No.4 Mk I", amount=6),
                HLLLoadoutItem(name="Mills Bomb", amount=4),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_RIFLEMAN_TROOPER(cls) -> "HLLLoadout":
        return cls(
            name="Trooper",
            faction=HLLFaction.CW,
            role=HLLRole.RIFLEMAN,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="SMLE No.1 Mk III", amount=6),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=2),
                HLLLoadoutItem(name="Explosive Ammo Box", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_ASSAULT_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CW,
            role=HLLRole.ASSAULT,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="Sten Gun Mk.V", amount=8),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_ASSAULT_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.CW,
            role=HLLRole.ASSAULT,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="M1928A1 THOMPSON", amount=8),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_ASSAULT_GRENADIER(cls) -> "HLLLoadout":
        return cls(
            name="Grenadier",
            faction=HLLFaction.CW,
            role=HLLRole.ASSAULT,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="Rifle No.4 Mk I", amount=6),
                HLLLoadoutItem(name="Mills Bomb", amount=6),
                HLLLoadoutItem(name="No.77", amount=4),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_ASSAULT_RAIDER(cls) -> "HLLLoadout":
        return cls(
            name="Raider",
            faction=HLLFaction.CW,
            role=HLLRole.ASSAULT,
            requires_level=9,
            items=[
                HLLLoadoutItem(name="M1928A1 THOMPSON", amount=5),
                HLLLoadoutItem(name="Mills Bomb", amount=1),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Satchel", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_AUTOMATIC_RIFLEMAN_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CW,
            role=HLLRole.AUTOMATIC_RIFLEMAN,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="Bren Gun", amount=10),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_AUTOMATIC_RIFLEMAN_DRUM_GUNNER(cls) -> "HLLLoadout":
        return cls(
            name="Drum Gunner",
            faction=HLLFaction.CW,
            role=HLLRole.AUTOMATIC_RIFLEMAN,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="M1928A1 THOMPSON", amount=5),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_MEDIC_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CW,
            role=HLLRole.MEDIC,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="SMLE No.1 Mk III", amount=4),
                HLLLoadoutItem(name="Webley MK VI", amount=8),
                HLLLoadoutItem(name="No.77", amount=4),
                HLLLoadoutItem(name="Morphine", amount=20),
                HLLLoadoutItem(name="Bandage", amount=20),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_MEDIC_CORPSMAN(cls) -> "HLLLoadout":
        return cls(
            name="Corpsman",
            faction=HLLFaction.CW,
            role=HLLRole.MEDIC,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Webley MK VI", amount=21),
                HLLLoadoutItem(name="No.77", amount=6),
                HLLLoadoutItem(name="Morphine", amount=20),
                HLLLoadoutItem(name="Bandage", amount=20),
                HLLLoadoutItem(name="Medical Supplies", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_SPOTTER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CW,
            role=HLLRole.SPOTTER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="Sten Gun Mk.V", amount=8),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=1),
                HLLLoadoutItem(name="Small Ammunition Box", amount=1),
                HLLLoadoutItem(name="Watch", amount=1),
                HLLLoadoutItem(name="Prism No.2 Mk II x6", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_SPOTTER_SCOUT(cls) -> "HLLLoadout":
        return cls(
            name="Scout",
            faction=HLLFaction.CW,
            role=HLLRole.SPOTTER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="SMLE No.1 Mk III", amount=6),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Watch", amount=1),
                HLLLoadoutItem(name="Prism No.2 Mk II x6", amount=1),
                HLLLoadoutItem(name="No.2 Mk 5 Flare Pistol", amount=1),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_SUPPORT_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CW,
            role=HLLRole.SUPPORT,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="SMLE No.1 Mk III", amount=6),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Supplies", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_SUPPORT_AMMO_CARRIER(cls) -> "HLLLoadout":
        return cls(
            name="Ammo Carrier",
            faction=HLLFaction.CW,
            role=HLLRole.SUPPORT,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Rifle No.4 Mk I", amount=6),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Supplies", amount=1),
                HLLLoadoutItem(name="Small Ammunition Box", amount=1),
                HLLLoadoutItem(name="Explosive Ammo Box", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_SUPPORT_FLAMER(cls) -> "HLLLoadout":
        return cls(
            name="Flamer",
            faction=HLLFaction.CW,
            role=HLLRole.SUPPORT,
            requires_level=8,
            items=[
                HLLLoadoutItem(name="FLAMETHROWER", amount=1),
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Supplies", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_MACHINE_GUNNER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CW,
            role=HLLRole.MACHINE_GUNNER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="Lewis Gun", amount=10),
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_MACHINE_GUNNER_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.CW,
            role=HLLRole.MACHINE_GUNNER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Bren Gun", amount=14),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_ANTI_TANK_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CW,
            role=HLLRole.ANTI_TANK,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="SMLE No.1 Mk III", amount=6),
                HLLLoadoutItem(name="PIAT", amount=2),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_ANTI_TANK_GUN_CREW(cls) -> "HLLLoadout":
        return cls(
            name="Gun Crew",
            faction=HLLFaction.CW,
            role=HLLRole.ANTI_TANK,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Rifle No.4 Mk I", amount=6),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Ordnance QF 6-pounder", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_ANTI_TANK_AMBUSHER(cls) -> "HLLLoadout":
        return cls(
            name="Ambusher",
            faction=HLLFaction.CW,
            role=HLLRole.ANTI_TANK,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="Sten Gun Mk.V", amount=8),
                HLLLoadoutItem(name="No.82 Grenade", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Satchel", amount=1),
                HLLLoadoutItem(name="A.T. Mine G.S. Mk V", amount=4),
                HLLLoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_ANTI_TANK_ELEPHANT_GUNNER(cls) -> "HLLLoadout":
        return cls(
            name="Elephant Gunner",
            faction=HLLFaction.CW,
            role=HLLRole.ANTI_TANK,
            requires_level=8,
            items=[
                HLLLoadoutItem(name="Rifle No.4 Mk I", amount=6),
                HLLLoadoutItem(name="Boys Anti-tank Rifle", amount=8),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_ENGINEER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CW,
            role=HLLRole.ENGINEER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="SMLE No.1 Mk III", amount=6),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Wrench", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Torch", amount=1),
                HLLLoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=2),
                HLLLoadoutItem(name="A.T. Mine G.S. Mk V", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_ENGINEER_SAPPER(cls) -> "HLLLoadout":
        return cls(
            name="Sapper",
            faction=HLLFaction.CW,
            role=HLLRole.ENGINEER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Rifle No.4 Mk I", amount=6),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=2),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="Satchel", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_ENGINEER_FIELD_ENGINEER(cls) -> "HLLLoadout":
        return cls(
            name="Field Engineer",
            faction=HLLFaction.CW,
            role=HLLRole.ENGINEER,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="Sten Gun Mk.V", amount=5),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Wrench", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="No.82 Grenade", amount=2),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Torch", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_OFFICER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CW,
            role=HLLRole.OFFICER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="Sten Gun Mk.V", amount=5),
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Watch", amount=1),
                HLLLoadoutItem(name="Prism No.2 Mk II x6", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_OFFICER_POINT_MAN(cls) -> "HLLLoadout":
        return cls(
            name="Point Man",
            faction=HLLFaction.CW,
            role=HLLRole.OFFICER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Rifle No.4 Mk I", amount=6),
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Watch", amount=1),
                HLLLoadoutItem(name="Prism No.2 Mk II x6", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_OFFICER_NCO(cls) -> "HLLLoadout":
        return cls(
            name="NCO",
            faction=HLLFaction.CW,
            role=HLLRole.OFFICER,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="SMLE No.1 Mk III", amount=6),
                HLLLoadoutItem(name="Mills Bomb", amount=3),
                HLLLoadoutItem(name="No.77", amount=3),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Watch", amount=1),
                HLLLoadoutItem(name="Prism No.2 Mk II x6", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_SNIPER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CW,
            role=HLLRole.SNIPER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="Rifle No.4 Mk I Sniper", amount=6),
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_SNIPER_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.CW,
            role=HLLRole.SNIPER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Rifle No.4 Mk I Sniper", amount=6),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=1),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_CREWMAN_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CW,
            role=HLLRole.CREWMAN,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_CREWMAN_MECHANIC(cls) -> "HLLLoadout":
        return cls(
            name="Mechanic",
            faction=HLLFaction.CW,
            role=HLLRole.CREWMAN,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Torch", amount=1),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
                HLLLoadoutItem(name="Supplies", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_CREWMAN_TECHNICIAN(cls) -> "HLLLoadout":
        return cls(
            name="Technician",
            faction=HLLFaction.CW,
            role=HLLRole.CREWMAN,
            requires_level=7,
            items=[
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Wrench", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_TANK_COMMANDER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CW,
            role=HLLRole.TANK_COMMANDER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="Sten Gun Mk.II", amount=4),
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Prism No.2 Mk II x6", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_TANK_COMMANDER_MECHANIC(cls) -> "HLLLoadout":
        return cls(
            name="Mechanic",
            faction=HLLFaction.CW,
            role=HLLRole.TANK_COMMANDER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="Torch", amount=1),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Prism No.2 Mk II x6", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_COMMANDER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CW,
            role=HLLRole.COMMANDER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="M1928A1 THOMPSON", amount=8),
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Watch", amount=1),
                HLLLoadoutItem(name="Prism No.2 Mk II x6", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_COMMANDER_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.CW,
            role=HLLRole.COMMANDER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Rifle No.4 Mk I", amount=6),
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Watch", amount=1),
                HLLLoadoutItem(name="Prism No.2 Mk II x6", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_ARTILLERY_OBSERVER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CW,
            role=HLLRole.ARTILLERY_OBSERVER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="Sten Gun Mk.II", amount=5),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="Watch", amount=1),
                HLLLoadoutItem(name="Prism No.2 Mk II x6", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="No.2 Mk 5 Flare Pistol", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_ARTILLERY_OBSERVER_JUNIOR_SERGEANT(cls) -> "HLLLoadout":
        return cls(
            name="Junior Sergeant",
            faction=HLLFaction.CW,
            role=HLLRole.ARTILLERY_OBSERVER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="SMLE No.1 Mk III", amount=6),
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Watch", amount=1),
                HLLLoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=1),
                HLLLoadoutItem(name="Prism No.2 Mk II x6", amount=1),
                HLLLoadoutItem(name="No.2 Mk 5 Flare Pistol", amount=1),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_OPERATOR_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CW,
            role=HLLRole.OPERATOR,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="SMLE No.1 Mk III", amount=6),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Wrench", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Torch", amount=1),
                HLLLoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=1),
                HLLLoadoutItem(name="A.T. Mine G.S. Mk V", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_OPERATOR_PIONEER(cls) -> "HLLLoadout":
        return cls(
            name="Pioneer",
            faction=HLLFaction.CW,
            role=HLLRole.OPERATOR,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Sten Gun Mk.II", amount=5),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=2),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Torch", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=2),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_GUNNER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CW,
            role=HLLRole.GUNNER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="SMLE No.1 Mk III", amount=6),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="Supplies", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def CW_GUNNER_AMMO_CARRIER(cls) -> "HLLLoadout":
        return cls(
            name="Ammo Carrier",
            faction=HLLFaction.CW,
            role=HLLRole.GUNNER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Sten Gun Mk.II", amount=5),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Supplies", amount=1),
                HLLLoadoutItem(name="Explosive Ammo Box", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_RIFLEMAN_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.DAK,
            role=HLLRole.RIFLEMAN,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=13),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="SMALL AMMUNITION BOX", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_RIFLEMAN_STURMTRUPPEN(cls) -> "HLLLoadout":
        return cls(
            name="Sturmtruppen",
            faction=HLLFaction.DAK,
            role=HLLRole.RIFLEMAN,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=12),
                HLLLoadoutItem(name="WALTHER P38", amount=10),
                HLLLoadoutItem(name="M24 STIELHANDGRANATE", amount=4),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_RIFLEMAN_PANZERGRENADIER(cls) -> "HLLLoadout":
        return cls(
            name="Panzergrenadier",
            faction=HLLFaction.DAK,
            role=HLLRole.RIFLEMAN,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=12),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="EXPLOSIVE AMMO BOX", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_ASSAULT_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.DAK,
            role=HLLRole.ASSAULT,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=12),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_ASSAULT_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.DAK,
            role=HLLRole.ASSAULT,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="MP40", amount=8),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_ASSAULT_GRENADIER(cls) -> "HLLLoadout":
        return cls(
            name="Grenadier",
            faction=HLLFaction.DAK,
            role=HLLRole.ASSAULT,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=12),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=6),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=3),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_ASSAULT_RAIDER(cls) -> "HLLLoadout":
        return cls(
            name="Raider",
            faction=HLLFaction.DAK,
            role=HLLRole.ASSAULT,
            requires_level=9,
            items=[
                HLLLoadoutItem(name="MP40", amount=8),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=1),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="SATCHEL", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_AUTOMATIC_RIFLEMAN_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.DAK,
            role=HLLRole.AUTOMATIC_RIFLEMAN,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="MP40", amount=10),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_AUTOMATIC_RIFLEMAN_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.DAK,
            role=HLLRole.AUTOMATIC_RIFLEMAN,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="MP40", amount=10),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_MEDIC_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.DAK,
            role=HLLRole.MEDIC,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=8),
                HLLLoadoutItem(name="WALTHER P38", amount=6),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=4),
                HLLLoadoutItem(name="MORPHINE AMPOULE", amount=20),
                HLLLoadoutItem(name="BANDAGE", amount=20),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_MEDIC_SANITATER(cls) -> "HLLLoadout":
        return cls(
            name="Sanitater",
            faction=HLLFaction.DAK,
            role=HLLRole.MEDIC,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="LUGER P08", amount=16),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=6),
                HLLLoadoutItem(name="MORPHINE AMPOULE", amount=20),
                HLLLoadoutItem(name="BANDAGE", amount=20),
                HLLLoadoutItem(name="MEDICAL SUPPLIES", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_SPOTTER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.DAK,
            role=HLLRole.SPOTTER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="MP40", amount=8),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="S-MINE", amount=1),
                HLLLoadoutItem(name="SMALL AMMUNITION BOX", amount=1),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="DIENSTGLAS 6×30", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_SPOTTER_SCOUT(cls) -> "HLLLoadout":
        return cls(
            name="Scout",
            faction=HLLFaction.DAK,
            role=HLLRole.SPOTTER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=10),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="DIENSTGLAS 6×30", amount=1),
                HLLLoadoutItem(name="FLARE GUN", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_SUPPORT_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.DAK,
            role=HLLRole.SUPPORT,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=12),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="SUPPLIES", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_SUPPORT_AMMO_CARRIER(cls) -> "HLLLoadout":
        return cls(
            name="Ammo Carrier",
            faction=HLLFaction.DAK,
            role=HLLRole.SUPPORT,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="MP40", amount=6),
                HLLLoadoutItem(name="SUPPLIES", amount=1),
                HLLLoadoutItem(name="SMALL AMMUNITION BOX", amount=1),
                HLLLoadoutItem(name="EXPLOSIVE AMMO BOX", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_SUPPORT_FLAMMENWERFER(cls) -> "HLLLoadout":
        return cls(
            name="Flammenwerfer",
            faction=HLLFaction.DAK,
            role=HLLRole.SUPPORT,
            requires_level=8,
            items=[
                HLLLoadoutItem(name="FLAMMENWERFER 41", amount=1),
                HLLLoadoutItem(name="WALTHER P38", amount=4),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="SUPPLIES", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_MACHINE_GUNNER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.DAK,
            role=HLLRole.MACHINE_GUNNER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="MG34", amount=10),
                HLLLoadoutItem(name="WALTHER P38", amount=6),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_MACHINE_GUNNER_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.DAK,
            role=HLLRole.MACHINE_GUNNER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="MG42", amount=6),
                HLLLoadoutItem(name="LUGER P08", amount=6),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_ANTI_TANK_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.DAK,
            role=HLLRole.ANTI_TANK,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=12),
                HLLLoadoutItem(name="PANZERSCHRECK", amount=2),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_ANTI_TANK_GUN_CREW(cls) -> "HLLLoadout":
        return cls(
            name="Gun Crew",
            faction=HLLFaction.DAK,
            role=HLLRole.ANTI_TANK,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=12),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="PAK 40", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_ANTI_TANK_AMBUSHER(cls) -> "HLLLoadout":
        return cls(
            name="Ambusher",
            faction=HLLFaction.DAK,
            role=HLLRole.ANTI_TANK,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="MP40", amount=6),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="SATCHEL", amount=1),
                HLLLoadoutItem(name="TELLERMINE 43", amount=4),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_ENGINEER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.DAK,
            role=HLLRole.ENGINEER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=12),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WRENCH", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="TORCH", amount=1),
                HLLLoadoutItem(name="S-MINE", amount=2),
                HLLLoadoutItem(name="TELLERMINE 43", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_ENGINEER_PIONIER(cls) -> "HLLLoadout":
        return cls(
            name="Pionier",
            faction=HLLFaction.DAK,
            role=HLLRole.ENGINEER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="MP40", amount=6),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="S-MINE", amount=2),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="SATCHEL", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_OFFICER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.DAK,
            role=HLLRole.OFFICER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="MP40", amount=8),
                HLLLoadoutItem(name="LUGER P08", amount=6),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="DIENSTGLAS 6×30", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_OFFICER_POINT_MAN(cls) -> "HLLLoadout":
        return cls(
            name="Point Man",
            faction=HLLFaction.DAK,
            role=HLLRole.OFFICER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=12),
                HLLLoadoutItem(name="WALTHER P38", amount=4),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="DIENSTGLAS 6×30", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_OFFICER_NCO(cls) -> "HLLLoadout":
        return cls(
            name="NCO",
            faction=HLLFaction.DAK,
            role=HLLRole.OFFICER,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="MP40", amount=8),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=3),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=3),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="DIENSTGLAS 6×30", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_SNIPER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.DAK,
            role=HLLRole.SNIPER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="KARABINER 98K x8", amount=19),
                HLLLoadoutItem(name="WALTHER P38", amount=6),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_SNIPER_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.DAK,
            role=HLLRole.SNIPER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="KARABINER 98K x8", amount=12),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="S-MINE", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_CREWMAN_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.DAK,
            role=HLLRole.CREWMAN,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="WALTHER P38", amount=6),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_CREWMAN_MECHANIC(cls) -> "HLLLoadout":
        return cls(
            name="Mechanic",
            faction=HLLFaction.DAK,
            role=HLLRole.CREWMAN,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="WALTHER P38", amount=6),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="TORCH", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
                HLLLoadoutItem(name="SUPPLIES", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_CREWMAN_TECHNICIAN(cls) -> "HLLLoadout":
        return cls(
            name="Technician",
            faction=HLLFaction.DAK,
            role=HLLRole.CREWMAN,
            requires_level=7,
            items=[
                HLLLoadoutItem(name="WALTHER P38", amount=6),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WRENCH", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_TANK_COMMANDER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.DAK,
            role=HLLRole.TANK_COMMANDER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="MP40", amount=4),
                HLLLoadoutItem(name="LUGER P08", amount=6),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="DIENSTGLAS 6×30", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_TANK_COMMANDER_MECHANIC(cls) -> "HLLLoadout":
        return cls(
            name="Mechanic",
            faction=HLLFaction.DAK,
            role=HLLRole.TANK_COMMANDER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="LUGER P08", amount=6),
                HLLLoadoutItem(name="TORCH", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="DIENSTGLAS 6×30", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_COMMANDER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.DAK,
            role=HLLRole.COMMANDER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="MP40", amount=6),
                HLLLoadoutItem(name="LUGER P08", amount=4),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="DIENSTGLAS 6×30", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_COMMANDER_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.DAK,
            role=HLLRole.COMMANDER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=12),
                HLLLoadoutItem(name="WALTHER P38", amount=4),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="DIENSTGLAS 6×30", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_ARTILLERY_OBSERVER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.DAK,
            role=HLLRole.ARTILLERY_OBSERVER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="MP40", amount=8),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="DIENSTGLAS 6×30", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FLARE GUN", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_ARTILLERY_OBSERVER_NCO(cls) -> "HLLLoadout":
        return cls(
            name="NCO",
            faction=HLLFaction.DAK,
            role=HLLRole.ARTILLERY_OBSERVER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=10),
                HLLLoadoutItem(name="WALTHER P38", amount=4),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="WATCH", amount=1),
                HLLLoadoutItem(name="S-MINE", amount=1),
                HLLLoadoutItem(name="DIENSTGLAS 6×30", amount=1),
                HLLLoadoutItem(name="FLARE GUN", amount=1),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_OPERATOR_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.DAK,
            role=HLLRole.OPERATOR,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=12),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="WRENCH", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="TORCH", amount=1),
                HLLLoadoutItem(name="S-MINE", amount=1),
                HLLLoadoutItem(name="TELLERMINE 43", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_OPERATOR_PIONEER(cls) -> "HLLLoadout":
        return cls(
            name="Pioneer",
            faction=HLLFaction.DAK,
            role=HLLRole.OPERATOR,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="MP40", amount=6),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="S-MINE", amount=2),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="TORCH", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_GUNNER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.DAK,
            role=HLLRole.GUNNER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="KARABINER 98K", amount=12),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="M43 STIELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="SUPPLIES", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=2),
            ],
        )

    @class_cached_property
    @classmethod
    def DAK_GUNNER_AMMO_CARRIER(cls) -> "HLLLoadout":
        return cls(
            name="Ammo Carrier",
            faction=HLLFaction.DAK,
            role=HLLRole.GUNNER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="MP40", amount=6),
                HLLLoadoutItem(name="BANDAGE", amount=2),
                HLLLoadoutItem(name="NB39 NEBELHANDGRANATE", amount=2),
                HLLLoadoutItem(name="SUPPLIES", amount=1),
                HLLLoadoutItem(name="EXPLOSIVE AMMO BOX", amount=1),
                HLLLoadoutItem(name="HAMMER", amount=1),
                HLLLoadoutItem(name="FELDSPATEN", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_RIFLEMAN_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.B8A,
            role=HLLRole.RIFLEMAN,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="SMLE No.1 Mk III", amount=6),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Small Ammunition Box", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_RIFLEMAN_GRENADIER(cls) -> "HLLLoadout":
        return cls(
            name="Grenadier",
            faction=HLLFaction.B8A,
            role=HLLRole.RIFLEMAN,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Rifle No.4 Mk I", amount=6),
                HLLLoadoutItem(name="Mills Bomb", amount=4),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_RIFLEMAN_TROOPER(cls) -> "HLLLoadout":
        return cls(
            name="Trooper",
            faction=HLLFaction.B8A,
            role=HLLRole.RIFLEMAN,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="SMLE No.1 Mk III", amount=6),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Explosive Ammo Box", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_ASSAULT_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.B8A,
            role=HLLRole.ASSAULT,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="Sten Gun Mk.II", amount=8),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_ASSAULT_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.B8A,
            role=HLLRole.ASSAULT,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="M1928A1 THOMPSON", amount=8),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_ASSAULT_GRENADIER(cls) -> "HLLLoadout":
        return cls(
            name="Grenadier",
            faction=HLLFaction.B8A,
            role=HLLRole.ASSAULT,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="Rifle No.4 Mk I", amount=6),
                HLLLoadoutItem(name="Mills Bomb", amount=6),
                HLLLoadoutItem(name="No.77", amount=4),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_ASSAULT_RAIDER(cls) -> "HLLLoadout":
        return cls(
            name="Raider",
            faction=HLLFaction.B8A,
            role=HLLRole.ASSAULT,
            requires_level=9,
            items=[
                HLLLoadoutItem(name="M1928A1 THOMPSON", amount=5),
                HLLLoadoutItem(name="Mills Bomb", amount=1),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Satchel", amount=1),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_AUTOMATIC_RIFLEMAN_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.B8A,
            role=HLLRole.AUTOMATIC_RIFLEMAN,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="Bren Gun", amount=10),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_AUTOMATIC_RIFLEMAN_DRUM_GUNNER(cls) -> "HLLLoadout":
        return cls(
            name="Drum Gunner",
            faction=HLLFaction.B8A,
            role=HLLRole.AUTOMATIC_RIFLEMAN,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="M1928A1 THOMPSON", amount=5),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_MEDIC_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.B8A,
            role=HLLRole.MEDIC,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="SMLE No.1 Mk III", amount=4),
                HLLLoadoutItem(name="Webley MK VI", amount=8),
                HLLLoadoutItem(name="No.77", amount=4),
                HLLLoadoutItem(name="Morphine", amount=20),
                HLLLoadoutItem(name="Bandage", amount=20),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_MEDIC_CORPSMAN(cls) -> "HLLLoadout":
        return cls(
            name="Corpsman",
            faction=HLLFaction.B8A,
            role=HLLRole.MEDIC,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Webley MK VI", amount=21),
                HLLLoadoutItem(name="No.77", amount=6),
                HLLLoadoutItem(name="Morphine", amount=20),
                HLLLoadoutItem(name="Bandage", amount=20),
                HLLLoadoutItem(name="Medical Supplies", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_SPOTTER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.B8A,
            role=HLLRole.SPOTTER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="M1928A1 THOMPSON", amount=8),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=1),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Small Ammunition Box", amount=1),
                HLLLoadoutItem(name="Watch", amount=1),
                HLLLoadoutItem(name="Prism No.2 Mk II x6", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_SPOTTER_SCOUT(cls) -> "HLLLoadout":
        return cls(
            name="Scout",
            faction=HLLFaction.B8A,
            role=HLLRole.SPOTTER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="SMLE No.1 Mk III", amount=6),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Watch", amount=1),
                HLLLoadoutItem(name="Prism No.2 Mk II x6", amount=1),
                HLLLoadoutItem(name="No.2 Mk 5 Flare Pistol", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_SUPPORT_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.B8A,
            role=HLLRole.SUPPORT,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="SMLE No.1 Mk III", amount=6),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Supplies", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_SUPPORT_AMMO_CARRIER(cls) -> "HLLLoadout":
        return cls(
            name="Ammo Carrier",
            faction=HLLFaction.B8A,
            role=HLLRole.SUPPORT,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Rifle No.4 Mk I", amount=6),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Supplies", amount=1),
                HLLLoadoutItem(name="Small Ammunition Box", amount=1),
                HLLLoadoutItem(name="Explosive Ammo Box", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_SUPPORT_FLAMER(cls) -> "HLLLoadout":
        return cls(
            name="Flamer",
            faction=HLLFaction.B8A,
            role=HLLRole.SUPPORT,
            requires_level=8,
            items=[
                HLLLoadoutItem(name="FLAMETHROWER", amount=1),
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Supplies", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_MACHINE_GUNNER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.B8A,
            role=HLLRole.MACHINE_GUNNER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="Lewis Gun", amount=10),
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_MACHINE_GUNNER_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.B8A,
            role=HLLRole.MACHINE_GUNNER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Bren Gun", amount=14),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_ANTI_TANK_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.B8A,
            role=HLLRole.ANTI_TANK,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="SMLE No.1 Mk III", amount=6),
                HLLLoadoutItem(name="PIAT", amount=2),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_ANTI_TANK_GUN_CREW(cls) -> "HLLLoadout":
        return cls(
            name="Gun Crew",
            faction=HLLFaction.B8A,
            role=HLLRole.ANTI_TANK,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Rifle No.4 Mk I", amount=6),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="Ordnance QF 6-pounder", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_ANTI_TANK_AMBUSHER(cls) -> "HLLLoadout":
        return cls(
            name="Ambusher",
            faction=HLLFaction.B8A,
            role=HLLRole.ANTI_TANK,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="M1928A1 THOMPSON", amount=8),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=1),
                HLLLoadoutItem(name="A.T. Mine G.S. Mk V", amount=4),
                HLLLoadoutItem(name="Satchel", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_ANTI_TANK_ELEPHANT_GUNNER(cls) -> "HLLLoadout":
        return cls(
            name="Elephant Gunner",
            faction=HLLFaction.B8A,
            role=HLLRole.ANTI_TANK,
            requires_level=8,
            items=[
                HLLLoadoutItem(name="Rifle No.4 Mk I", amount=6),
                HLLLoadoutItem(name="Boys Anti-tank Rifle", amount=8),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_ENGINEER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.B8A,
            role=HLLRole.ENGINEER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="SMLE No.1 Mk III", amount=6),
                HLLLoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=2),
                HLLLoadoutItem(name="A.T. Mine G.S. Mk V", amount=1),
                HLLLoadoutItem(name="Wrench", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Torch", amount=1),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_ENGINEER_SAPPER(cls) -> "HLLLoadout":
        return cls(
            name="Sapper",
            faction=HLLFaction.B8A,
            role=HLLRole.ENGINEER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Rifle No.4 Mk I", amount=6),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=2),
                HLLLoadoutItem(name="Satchel", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_ENGINEER_FIELD_ENGINEER(cls) -> "HLLLoadout":
        return cls(
            name="Field Engineer",
            faction=HLLFaction.B8A,
            role=HLLRole.ENGINEER,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="Sten Gun Mk.II", amount=5),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Wrench", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Torch", amount=1),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_OFFICER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.B8A,
            role=HLLRole.OFFICER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="M1928A1 THOMPSON", amount=5),
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Watch", amount=1),
                HLLLoadoutItem(name="Prism No.2 Mk II x6", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_OFFICER_POINT_MAN(cls) -> "HLLLoadout":
        return cls(
            name="Point Man",
            faction=HLLFaction.B8A,
            role=HLLRole.OFFICER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Rifle No.4 Mk I", amount=6),
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Watch", amount=1),
                HLLLoadoutItem(name="Prism No.2 Mk II x6", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_OFFICER_NCO(cls) -> "HLLLoadout":
        return cls(
            name="NCO",
            faction=HLLFaction.B8A,
            role=HLLRole.OFFICER,
            requires_level=6,
            items=[
                HLLLoadoutItem(name="SMLE No.1 Mk III", amount=6),
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="Mills Bomb", amount=3),
                HLLLoadoutItem(name="No.77", amount=3),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Watch", amount=1),
                HLLLoadoutItem(name="Prism No.2 Mk II x6", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_SNIPER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.B8A,
            role=HLLRole.SNIPER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="Rifle No.4 Mk I Sniper", amount=6),
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_SNIPER_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.B8A,
            role=HLLRole.SNIPER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Rifle No.4 Mk I Sniper", amount=6),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=1),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_CREWMAN_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.B8A,
            role=HLLRole.CREWMAN,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
                HLLLoadoutItem(name="EXTERIOR CUSTOMIZATION", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_CREWMAN_MECHANIC(cls) -> "HLLLoadout":
        return cls(
            name="Mechanic",
            faction=HLLFaction.B8A,
            role=HLLRole.CREWMAN,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Torch", amount=1),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
                HLLLoadoutItem(name="Supplies", amount=1),
                HLLLoadoutItem(name="EXTERIOR CUSTOMIZATION", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_CREWMAN_TECHNICIAN(cls) -> "HLLLoadout":
        return cls(
            name="Technician",
            faction=HLLFaction.B8A,
            role=HLLRole.CREWMAN,
            requires_level=7,
            items=[
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Wrench", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
                HLLLoadoutItem(name="EXTERIOR CUSTOMIZATION", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_TANK_COMMANDER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.B8A,
            role=HLLRole.TANK_COMMANDER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="Sten Gun Mk.II", amount=4),
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Prism No.2 Mk II x6", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
                HLLLoadoutItem(name="EXTERIOR CUSTOMIZATION", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_TANK_COMMANDER_MECHANIC(cls) -> "HLLLoadout":
        return cls(
            name="Mechanic",
            faction=HLLFaction.B8A,
            role=HLLRole.TANK_COMMANDER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="Torch", amount=1),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Prism No.2 Mk II x6", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
                HLLLoadoutItem(name="EXTERIOR CUSTOMIZATION", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_COMMANDER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.B8A,
            role=HLLRole.COMMANDER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="M1928A1 THOMPSON", amount=8),
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Watch", amount=1),
                HLLLoadoutItem(name="Prism No.2 Mk II x6", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_COMMANDER_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.B8A,
            role=HLLRole.COMMANDER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Rifle No.4 Mk I", amount=6),
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Watch", amount=1),
                HLLLoadoutItem(name="Prism No.2 Mk II x6", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_ARTILLERY_OBSERVER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.B8A,
            role=HLLRole.ARTILLERY_OBSERVER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="Sten Gun Mk.II", amount=5),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="Watch", amount=1),
                HLLLoadoutItem(name="Prism No.2 Mk II x6", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="No.2 Mk 5 Flare Pistol", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_ARTILLERY_OBSERVER_JUNIOR_SERGEANT(cls) -> "HLLLoadout":
        return cls(
            name="Junior Sergeant",
            faction=HLLFaction.B8A,
            role=HLLRole.ARTILLERY_OBSERVER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="SMLE No.1 Mk III", amount=6),
                HLLLoadoutItem(name="Webley MK VI", amount=4),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Watch", amount=1),
                HLLLoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=1),
                HLLLoadoutItem(name="Prism No.2 Mk II x6", amount=1),
                HLLLoadoutItem(name="No.2 Mk 5 Flare Pistol", amount=1),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_OPERATOR_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.B8A,
            role=HLLRole.OPERATOR,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="SMLE No.1 Mk III", amount=6),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Wrench", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Torch", amount=1),
                HLLLoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=1),
                HLLLoadoutItem(name="A.T. Mine G.S. Mk V", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_OPERATOR_PIONEER(cls) -> "HLLLoadout":
        return cls(
            name="Pioneer",
            faction=HLLFaction.B8A,
            role=HLLRole.OPERATOR,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Bren Gun", amount=6),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="A.P. Shrapnel Mine Mk II", amount=2),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Torch", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=2),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_GUNNER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.B8A,
            role=HLLRole.GUNNER,
            requires_level=1,
            items=[
                HLLLoadoutItem(name="SMLE No.1 Mk III", amount=6),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="Mills Bomb", amount=2),
                HLLLoadoutItem(name="Supplies", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    @class_cached_property
    @classmethod
    def B8A_GUNNER_AMMO_CARRIER(cls) -> "HLLLoadout":
        return cls(
            name="Ammo Carrier",
            faction=HLLFaction.B8A,
            role=HLLRole.GUNNER,
            requires_level=3,
            items=[
                HLLLoadoutItem(name="Sten Gun Mk.II", amount=5),
                HLLLoadoutItem(name="Bandage", amount=2),
                HLLLoadoutItem(name="No.77", amount=2),
                HLLLoadoutItem(name="Supplies", amount=1),
                HLLLoadoutItem(name="Explosive Ammo Box", amount=1),
                HLLLoadoutItem(name="Hammer", amount=1),
                HLLLoadoutItem(name="Fairbairn–Sykes", amount=1),
            ],
        )

    ### INJECT "hll loadouts" END


class HLLVLoadoutItemType(StrEnum):
    PRIMARY = "Primary"
    UTILITY = "Utility"
    LETHAL = "Lethal"
    VERSATILE = "Versatile"
    """An item that can be equipped as either a primary or a secondary item."""
    LOCKED_ITEM = "Locked Item"
    """An item that, when unlocked, is automatically included in a loadout and cannot
    manually be equipped or removed."""


class HLLVLoadoutItem(IndexedBaseModel[str]):
    id: str
    name: str
    faction: HLLVFaction
    weapon: HLLVWeapon
    type: HLLVLoadoutItemType
    weight: int
    """The base weight of this item."""
    description_tags: list[str]
    base_ammo: int
    """The minimum amount of ammo that this item is equipped with."""
    max_ammo: int
    """The maximum amount of ammo that this item can be equipped with."""
    ammo_weight: int
    """The weight added for each additional ammo equipped beyond the base ammo."""
    level_requirements: dict[HLLVRole, int]
    """The level a role must reach in order for the player to be able to equip this
    item.

    If a role is not present in this dictionary, the item is not available to that role.
    """

    def calculate_weight(self, total_ammo: int) -> int:
        """Calculate the total weight of this item based on the total ammo equipped.

        Parameters
        ----------
        total_ammo : int
            The total amount of ammo equipped for this item.

        Returns
        -------
        int
            The total weight of this item based on the total ammo.

        """
        if total_ammo <= self.base_ammo:
            return self.weight
        extra_ammo = total_ammo - self.base_ammo
        return self.weight + extra_ammo * self.ammo_weight

    ### INJECT "hllv loadout items" START

    @class_cached_property
    @classmethod
    def _1911A1(cls) -> "HLLVLoadoutItem":
        return cls(
            id="1911A1",
            name="M1911A1",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.M1911A1,
            type=HLLVLoadoutItemType.VERSATILE,
            weight=2,
            description_tags=[
                "Secondary",
                "Pistol",
                "Semi-Automatic",
            ],
            base_ammo=3,
            max_ammo=6,
            ammo_weight=1,
            level_requirements={
                HLLVRole.RIFLEMAN: 0,
                HLLVRole.MEDIC: 0,
                HLLVRole.SPOTTER: 0,
                HLLVRole.SPECIALIST: 0,
                HLLVRole.MACHINE_GUNNER: 0,
                HLLVRole.GRENADIER: 0,
                HLLVRole.ENGINEER: 0,
                HLLVRole.SQUAD_LEADER: 0,
                HLLVRole.SNIPER: 0,
                HLLVRole.CREWMAN: 0,
                HLLVRole.TANK_COMMANDER: 0,
                HLLVRole.SUPPORT: 0,
                HLLVRole.OBSERVER: 0,
                HLLVRole.GUNNER: 0,
                HLLVRole.PILOT: 0,
                HLLVRole.LOGISTICS_OFFICER: 0,
                HLLVRole.COMMANDER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def DH10_AP(cls) -> "HLLVLoadoutItem":
        return cls(
            id="DH10_AP",
            name="DH10 AP Mine",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.DH10_AP_MINE,
            type=HLLVLoadoutItemType.LETHAL,
            weight=2,
            description_tags=[
                "Equipment",
                "Lethal",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=2,
            level_requirements={
                HLLVRole.OBSERVER: 3,
                HLLVRole.SUPPORT: 3,
                HLLVRole.SPOTTER: 3,
                HLLVRole.SNIPER: 3,
                HLLVRole.ENGINEER: 3,
                HLLVRole.MACHINE_GUNNER: 3,
                HLLVRole.SPECIALIST: 3,
                HLLVRole.GRENADIER: 3,
            },
        )

    @class_cached_property
    @classmethod
    def DH10_APX2(cls) -> "HLLVLoadoutItem":
        return cls(
            id="DH10_APx2",
            name="DH10 AP Mine x2",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.DH10_AP_MINE,
            type=HLLVLoadoutItemType.LETHAL,
            weight=4,
            description_tags=[],
            base_ammo=2,
            max_ammo=2,
            ammo_weight=2,
            level_requirements={
                HLLVRole.SUPPORT: 6,
                HLLVRole.SPOTTER: 6,
                HLLVRole.SNIPER: 6,
                HLLVRole.ENGINEER: 6,
                HLLVRole.GRENADIER: 6,
                HLLVRole.OBSERVER: 6,
                HLLVRole.MACHINE_GUNNER: 6,
                HLLVRole.SPECIALIST: 6,
            },
        )

    @class_cached_property
    @classmethod
    def IZH58(cls) -> "HLLVLoadoutItem":
        return cls(
            id="IZH58",
            name="IZH 58",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.IZH_58,
            type=HLLVLoadoutItemType.VERSATILE,
            weight=3,
            description_tags=[
                "Primary",
                "Shotgun",
                "Break Action",
            ],
            base_ammo=6,
            max_ammo=8,
            ammo_weight=1,
            level_requirements={
                HLLVRole.COMMANDER: 7,
                HLLVRole.TANK_COMMANDER: 7,
                HLLVRole.CREWMAN: 7,
                HLLVRole.ENGINEER: 7,
                HLLVRole.SPOTTER: 7,
                HLLVRole.MACHINE_GUNNER: 7,
                HLLVRole.GRENADIER: 7,
                HLLVRole.SQUAD_LEADER: 7,
                HLLVRole.SNIPER: 7,
                HLLVRole.SUPPORT: 7,
                HLLVRole.OBSERVER: 7,
                HLLVRole.GUNNER: 7,
            },
        )

    @class_cached_property
    @classmethod
    def K50M(cls) -> "HLLVLoadoutItem":
        return cls(
            id="K50M",
            name="K50M",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.K50M,
            type=HLLVLoadoutItemType.VERSATILE,
            weight=3,
            description_tags=[
                "Primary",
                "Submachine Gun",
                "Automatic",
                "Semi-Automatic",
            ],
            base_ammo=4,
            max_ammo=8,
            ammo_weight=1,
            level_requirements={
                HLLVRole.COMMANDER: 3,
                HLLVRole.TANK_COMMANDER: 3,
                HLLVRole.CREWMAN: 3,
                HLLVRole.OBSERVER: 3,
                HLLVRole.SNIPER: 3,
                HLLVRole.SQUAD_LEADER: 3,
                HLLVRole.MEDIC: 3,
                HLLVRole.SPECIALIST: 3,
                HLLVRole.ENGINEER: 3,
                HLLVRole.GRENADIER: 3,
            },
        )

    @class_cached_property
    @classmethod
    def K50M_DRUM(cls) -> "HLLVLoadoutItem":
        return cls(
            id="K50M_Drum",
            name="K50M Drum",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.K50M_DRUM,
            type=HLLVLoadoutItemType.VERSATILE,
            weight=4,
            description_tags=[
                "Primary",
                "Submachine Gun",
                "Automatic",
                "Semi-Automatic",
            ],
            base_ammo=3,
            max_ammo=6,
            ammo_weight=2,
            level_requirements={
                HLLVRole.GRENADIER: 6,
                HLLVRole.ENGINEER: 6,
                HLLVRole.MACHINE_GUNNER: 6,
            },
        )

    @class_cached_property
    @classmethod
    def LPO50(cls) -> "HLLVLoadoutItem":
        return cls(
            id="LPO50",
            name="LPO-50",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.LPO_50,
            type=HLLVLoadoutItemType.VERSATILE,
            weight=6,
            description_tags=[
                "Primary",
                "Incendiary Weapon",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=2,
            level_requirements={
                HLLVRole.SPECIALIST: 7,
            },
        )

    @class_cached_property
    @classmethod
    def M16A1(cls) -> "HLLVLoadoutItem":
        return cls(
            id="M16A1",
            name="M16A1",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.M16A1,
            type=HLLVLoadoutItemType.PRIMARY,
            weight=4,
            description_tags=[
                "Primary",
                "Rifle",
                "Automatic",
                "Semi-Automatic",
            ],
            base_ammo=4,
            max_ammo=8,
            ammo_weight=1,
            level_requirements={
                HLLVRole.RIFLEMAN: 0,
                HLLVRole.MEDIC: 0,
                HLLVRole.SPOTTER: 0,
                HLLVRole.SPECIALIST: 0,
                HLLVRole.GRENADIER: 0,
                HLLVRole.ENGINEER: 0,
                HLLVRole.SQUAD_LEADER: 0,
                HLLVRole.CREWMAN: 3,
                HLLVRole.TANK_COMMANDER: 3,
                HLLVRole.SUPPORT: 0,
                HLLVRole.OBSERVER: 0,
                HLLVRole.GUNNER: 0,
                HLLVRole.PILOT: 3,
                HLLVRole.LOGISTICS_OFFICER: 3,
                HLLVRole.COMMANDER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def M16A1_BAYONET(cls) -> "HLLVLoadoutItem":
        return cls(
            id="M16A1_Bayonet",
            name="M16A1 With Bayonet",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.M16A1_WITH_BAYONET,
            type=HLLVLoadoutItemType.PRIMARY,
            weight=5,
            description_tags=[
                "Primary",
                "Rifle",
                "Automatic",
                "Semi-Automatic",
            ],
            base_ammo=4,
            max_ammo=8,
            ammo_weight=1,
            level_requirements={
                HLLVRole.COMMANDER: 4,
                HLLVRole.RIFLEMAN: 4,
                HLLVRole.MEDIC: 4,
                HLLVRole.SPOTTER: 4,
                HLLVRole.SPECIALIST: 4,
                HLLVRole.GRENADIER: 4,
                HLLVRole.ENGINEER: 4,
                HLLVRole.CREWMAN: 4,
                HLLVRole.TANK_COMMANDER: 4,
                HLLVRole.SUPPORT: 4,
                HLLVRole.OBSERVER: 4,
                HLLVRole.GUNNER: 4,
                HLLVRole.PILOT: 4,
                HLLVRole.LOGISTICS_OFFICER: 4,
                HLLVRole.SQUAD_LEADER: 4,
            },
        )

    @class_cached_property
    @classmethod
    def M183_DEMO(cls) -> "HLLVLoadoutItem":
        return cls(
            id="M183_Demo",
            name="M183 Demolition Charge",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.M183_DEMOLITION_CHARGE,
            type=HLLVLoadoutItemType.LETHAL,
            weight=5,
            description_tags=[
                "Equipment",
                "Lethal",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.ENGINEER: 5,
                HLLVRole.GRENADIER: 5,
            },
        )

    @class_cached_property
    @classmethod
    def M18_CLAYMORE(cls) -> "HLLVLoadoutItem":
        return cls(
            id="M18_Claymore",
            name="M18 Claymore",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.M18_CLAYMORE,
            type=HLLVLoadoutItemType.LETHAL,
            weight=2,
            description_tags=[
                "Equipment",
                "Lethal",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.OBSERVER: 3,
                HLLVRole.SUPPORT: 3,
                HLLVRole.SPOTTER: 3,
                HLLVRole.SNIPER: 3,
                HLLVRole.ENGINEER: 3,
                HLLVRole.MACHINE_GUNNER: 3,
                HLLVRole.SPECIALIST: 3,
                HLLVRole.GRENADIER: 3,
            },
        )

    @class_cached_property
    @classmethod
    def M18_CLAYMOREX2(cls) -> "HLLVLoadoutItem":
        return cls(
            id="M18_Claymorex2",
            name="M18 Claymore x2",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.M18_CLAYMORE,
            type=HLLVLoadoutItemType.LETHAL,
            weight=4,
            description_tags=[
                "Equipment",
                "Lethal",
            ],
            base_ammo=2,
            max_ammo=2,
            ammo_weight=1,
            level_requirements={
                HLLVRole.OBSERVER: 6,
                HLLVRole.SUPPORT: 6,
                HLLVRole.SPOTTER: 6,
                HLLVRole.SNIPER: 6,
                HLLVRole.ENGINEER: 6,
                HLLVRole.MACHINE_GUNNER: 6,
                HLLVRole.SPECIALIST: 6,
                HLLVRole.GRENADIER: 6,
            },
        )

    @class_cached_property
    @classmethod
    def M18_SMOKE(cls) -> "HLLVLoadoutItem":
        return cls(
            id="M18_Smoke",
            name="M18 Smoke Grenade",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.M18_SMOKE_GRENADE,
            type=HLLVLoadoutItemType.UTILITY,
            weight=1,
            description_tags=[
                "Equipment",
                "Utility",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.RIFLEMAN: 0,
                HLLVRole.MEDIC: 0,
                HLLVRole.SPOTTER: 0,
                HLLVRole.SPECIALIST: 0,
                HLLVRole.MACHINE_GUNNER: 0,
                HLLVRole.GRENADIER: 0,
                HLLVRole.ENGINEER: 0,
                HLLVRole.SQUAD_LEADER: 0,
                HLLVRole.SNIPER: 0,
                HLLVRole.CREWMAN: 0,
                HLLVRole.TANK_COMMANDER: 0,
                HLLVRole.SUPPORT: 0,
                HLLVRole.OBSERVER: 0,
                HLLVRole.GUNNER: 0,
                HLLVRole.PILOT: 0,
                HLLVRole.LOGISTICS_OFFICER: 0,
                HLLVRole.COMMANDER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def M18_SMOKEX2(cls) -> "HLLVLoadoutItem":
        return cls(
            id="M18_Smokex2",
            name="M18 Smoke Grenade x2",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.M18_SMOKE_GRENADE,
            type=HLLVLoadoutItemType.UTILITY,
            weight=3,
            description_tags=[
                "Equipment",
                "Utility",
            ],
            base_ammo=2,
            max_ammo=2,
            ammo_weight=1,
            level_requirements={
                HLLVRole.RIFLEMAN: 3,
                HLLVRole.MEDIC: 3,
                HLLVRole.SPOTTER: 3,
                HLLVRole.SPECIALIST: 3,
                HLLVRole.MACHINE_GUNNER: 3,
                HLLVRole.GRENADIER: 3,
                HLLVRole.ENGINEER: 3,
                HLLVRole.SQUAD_LEADER: 3,
                HLLVRole.SNIPER: 3,
                HLLVRole.CREWMAN: 3,
                HLLVRole.TANK_COMMANDER: 3,
                HLLVRole.SUPPORT: 3,
                HLLVRole.OBSERVER: 3,
                HLLVRole.GUNNER: 3,
                HLLVRole.PILOT: 3,
                HLLVRole.LOGISTICS_OFFICER: 3,
                HLLVRole.COMMANDER: 3,
            },
        )

    @class_cached_property
    @classmethod
    def M18_SMOKEX3(cls) -> "HLLVLoadoutItem":
        return cls(
            id="M18_Smokex3",
            name="M18 Smoke Grenade x3",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.M18_SMOKE_GRENADE,
            type=HLLVLoadoutItemType.UTILITY,
            weight=5,
            description_tags=[
                "Equipment",
                "Utility",
            ],
            base_ammo=3,
            max_ammo=3,
            ammo_weight=1,
            level_requirements={
                HLLVRole.RIFLEMAN: 5,
                HLLVRole.MEDIC: 5,
                HLLVRole.SPOTTER: 5,
                HLLVRole.SPECIALIST: 5,
                HLLVRole.MACHINE_GUNNER: 5,
                HLLVRole.GRENADIER: 5,
                HLLVRole.ENGINEER: 5,
                HLLVRole.SQUAD_LEADER: 5,
                HLLVRole.SNIPER: 5,
                HLLVRole.CREWMAN: 5,
                HLLVRole.TANK_COMMANDER: 5,
                HLLVRole.SUPPORT: 5,
                HLLVRole.OBSERVER: 5,
                HLLVRole.GUNNER: 5,
                HLLVRole.PILOT: 5,
                HLLVRole.LOGISTICS_OFFICER: 5,
                HLLVRole.COMMANDER: 5,
            },
        )

    @class_cached_property
    @classmethod
    def M203(cls) -> "HLLVLoadoutItem":
        return cls(
            id="M203",
            name="M16A1-M203",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.M16A1_M203,
            type=HLLVLoadoutItemType.PRIMARY,
            weight=6,
            description_tags=[
                "Primary",
                "Rifle",
                "Automatic",
                "Semi-Automatic",
                "Grenade Launcher",
            ],
            base_ammo=4,
            max_ammo=6,
            ammo_weight=1,
            level_requirements={
                HLLVRole.RIFLEMAN: 10,
                HLLVRole.GRENADIER: 10,
                HLLVRole.SPECIALIST: 10,
                HLLVRole.ENGINEER: 10,
            },
        )

    @class_cached_property
    @classmethod
    def M2_FLAMETHROWER(cls) -> "HLLVLoadoutItem":
        return cls(
            id="M2_FlameThrower",
            name="M2A1-7",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.M2A1_7,
            type=HLLVLoadoutItemType.VERSATILE,
            weight=6,
            description_tags=[
                "Primary",
                "Incendiary Weapon",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=2,
            level_requirements={
                HLLVRole.SPECIALIST: 7,
            },
        )

    @class_cached_property
    @classmethod
    def M3_KNIFE(cls) -> "HLLVLoadoutItem":
        return cls(
            id="M3_Knife",
            name="M3 Knife",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.M3_KNIFE,
            type=HLLVLoadoutItemType.LOCKED_ITEM,
            weight=1,
            description_tags=[
                "Melee",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.RIFLEMAN: 0,
                HLLVRole.MEDIC: 0,
                HLLVRole.SPOTTER: 0,
                HLLVRole.SPECIALIST: 0,
                HLLVRole.MACHINE_GUNNER: 0,
                HLLVRole.GRENADIER: 0,
                HLLVRole.ENGINEER: 0,
                HLLVRole.SQUAD_LEADER: 0,
                HLLVRole.SNIPER: 0,
                HLLVRole.CREWMAN: 0,
                HLLVRole.TANK_COMMANDER: 0,
                HLLVRole.SUPPORT: 0,
                HLLVRole.OBSERVER: 0,
                HLLVRole.GUNNER: 0,
                HLLVRole.PILOT: 0,
                HLLVRole.LOGISTICS_OFFICER: 0,
                HLLVRole.COMMANDER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def M40(cls) -> "HLLVLoadoutItem":
        return cls(
            id="M40",
            name="M40",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.M40,
            type=HLLVLoadoutItemType.PRIMARY,
            weight=4,
            description_tags=[
                "Primary",
                "Sniper",
                "Bolt Action",
            ],
            base_ammo=4,
            max_ammo=8,
            ammo_weight=1,
            level_requirements={
                HLLVRole.SNIPER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def M60(cls) -> "HLLVLoadoutItem":
        return cls(
            id="M60",
            name="M60",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.M60,
            type=HLLVLoadoutItemType.PRIMARY,
            weight=4,
            description_tags=[
                "Primary",
                "Machine Gun",
                "Automatic",
            ],
            base_ammo=3,
            max_ammo=6,
            ammo_weight=2,
            level_requirements={
                HLLVRole.MACHINE_GUNNER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def M61(cls) -> "HLLVLoadoutItem":
        return cls(
            id="M61",
            name="M61 Frag Grenade",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.M61_FRAG_GRENADE,
            type=HLLVLoadoutItemType.LETHAL,
            weight=2,
            description_tags=[
                "Equipment",
                "Lethal",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.RIFLEMAN: 0,
                HLLVRole.MEDIC: 0,
                HLLVRole.SPOTTER: 0,
                HLLVRole.SPECIALIST: 0,
                HLLVRole.MACHINE_GUNNER: 0,
                HLLVRole.GRENADIER: 0,
                HLLVRole.ENGINEER: 0,
                HLLVRole.SQUAD_LEADER: 0,
                HLLVRole.SNIPER: 0,
                HLLVRole.CREWMAN: 0,
                HLLVRole.TANK_COMMANDER: 0,
                HLLVRole.SUPPORT: 0,
                HLLVRole.OBSERVER: 0,
                HLLVRole.GUNNER: 0,
                HLLVRole.PILOT: 0,
                HLLVRole.LOGISTICS_OFFICER: 0,
                HLLVRole.COMMANDER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def M61X2(cls) -> "HLLVLoadoutItem":
        return cls(
            id="M61x2",
            name="M61 Frag Grenade x2",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.M61_FRAG_GRENADE,
            type=HLLVLoadoutItemType.LETHAL,
            weight=4,
            description_tags=[
                "Equipment",
                "Lethal",
            ],
            base_ammo=2,
            max_ammo=2,
            ammo_weight=1,
            level_requirements={
                HLLVRole.RIFLEMAN: 5,
                HLLVRole.MEDIC: 5,
                HLLVRole.SPOTTER: 5,
                HLLVRole.SPECIALIST: 5,
                HLLVRole.MACHINE_GUNNER: 5,
                HLLVRole.GRENADIER: 5,
                HLLVRole.ENGINEER: 5,
                HLLVRole.SQUAD_LEADER: 5,
                HLLVRole.SNIPER: 5,
                HLLVRole.CREWMAN: 5,
                HLLVRole.TANK_COMMANDER: 5,
                HLLVRole.SUPPORT: 5,
                HLLVRole.OBSERVER: 5,
                HLLVRole.GUNNER: 5,
                HLLVRole.PILOT: 5,
                HLLVRole.LOGISTICS_OFFICER: 5,
                HLLVRole.COMMANDER: 5,
            },
        )

    @class_cached_property
    @classmethod
    def M61X3(cls) -> "HLLVLoadoutItem":
        return cls(
            id="M61x3",
            name="M61 Frag Grenade x3",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.M61_FRAG_GRENADE,
            type=HLLVLoadoutItemType.LETHAL,
            weight=6,
            description_tags=[
                "Equipment",
                "Lethal",
            ],
            base_ammo=3,
            max_ammo=3,
            ammo_weight=1,
            level_requirements={
                HLLVRole.OBSERVER: 8,
                HLLVRole.GUNNER: 8,
                HLLVRole.SUPPORT: 8,
                HLLVRole.SPOTTER: 8,
                HLLVRole.SNIPER: 8,
                HLLVRole.RIFLEMAN: 8,
                HLLVRole.ENGINEER: 8,
                HLLVRole.MACHINE_GUNNER: 8,
                HLLVRole.SPECIALIST: 8,
                HLLVRole.GRENADIER: 8,
            },
        )

    @class_cached_property
    @classmethod
    def M72(cls) -> "HLLVLoadoutItem":
        return cls(
            id="M72",
            name="M72 ",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.M72,
            type=HLLVLoadoutItemType.VERSATILE,
            weight=6,
            description_tags=[
                "Secondary",
                "Launcher",
            ],
            base_ammo=2,
            max_ammo=4,
            ammo_weight=3,
            level_requirements={
                HLLVRole.GRENADIER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def M79(cls) -> "HLLVLoadoutItem":
        return cls(
            id="M79",
            name="M79 ",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.M79,
            type=HLLVLoadoutItemType.VERSATILE,
            weight=5,
            description_tags=[
                "Grenade Launcher",
                "Secondary",
            ],
            base_ammo=3,
            max_ammo=3,
            ammo_weight=3,
            level_requirements={
                HLLVRole.GRENADIER: 0,
                HLLVRole.ENGINEER: 7,
                HLLVRole.SPOTTER: 10,
                HLLVRole.OBSERVER: 10,
            },
        )

    @class_cached_property
    @classmethod
    def MODEL_77E_SHOTGUN(cls) -> "HLLVLoadoutItem":
        return cls(
            id="Model_77E_Shotgun",
            name="Model 77E",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.MODEL_77E,
            type=HLLVLoadoutItemType.VERSATILE,
            weight=3,
            description_tags=[
                "Primary",
                "Shotgun",
                "Pump Action",
            ],
            base_ammo=4,
            max_ammo=8,
            ammo_weight=1,
            level_requirements={
                HLLVRole.ENGINEER: 7,
                HLLVRole.SQUAD_LEADER: 7,
                HLLVRole.SPECIALIST: 7,
                HLLVRole.GRENADIER: 7,
                HLLVRole.PILOT: 7,
                HLLVRole.LOGISTICS_OFFICER: 7,
                HLLVRole.SPOTTER: 7,
                HLLVRole.COMMANDER: 7,
                HLLVRole.OBSERVER: 7,
                HLLVRole.SNIPER: 7,
                HLLVRole.CREWMAN: 7,
                HLLVRole.TANK_COMMANDER: 7,
                HLLVRole.GUNNER: 7,
                HLLVRole.SUPPORT: 7,
                HLLVRole.MACHINE_GUNNER: 7,
            },
        )

    @class_cached_property
    @classmethod
    def N4_RIFLE_LAUNCHER(cls) -> "HLLVLoadoutItem":
        return cls(
            id="N4_Rifle_Launcher",
            name="Type 53 W/ N4 Rifle Launcher",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.TYPE_53_W_N4_RIFLE_LAUNCHER,
            type=HLLVLoadoutItemType.PRIMARY,
            weight=6,
            description_tags=[
                "Primary",
                "Rifle",
                "Semi-Automatic",
                "Grenade Launcher",
            ],
            base_ammo=6,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.SPECIALIST: 10,
                HLLVRole.GRENADIER: 0,
                HLLVRole.RIFLEMAN: 10,
                HLLVRole.ENGINEER: 10,
                HLLVRole.SPOTTER: 10,
                HLLVRole.OBSERVER: 10,
            },
        )

    @class_cached_property
    @classmethod
    def NVAMORTARWRENCH(cls) -> "HLLVLoadoutItem":
        return cls(
            id="NVAMortarWrench",
            name="Wrench",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.WRENCH,
            type=HLLVLoadoutItemType.LOCKED_ITEM,
            weight=1,
            description_tags=[
                "Role Equipment",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.SQUAD_LEADER: 0,
                HLLVRole.COMMANDER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def NVA_AAWRENCH(cls) -> "HLLVLoadoutItem":
        return cls(
            id="NVA_AAWrench",
            name="Anti-Aircraft Gun Wrench",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.ANTI_AIRCRAFT_GUN_WRENCH,
            type=HLLVLoadoutItemType.UTILITY,
            weight=3,
            description_tags=[
                "Equipment",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.MACHINE_GUNNER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def NVA_KNIFE(cls) -> "HLLVLoadoutItem":
        return cls(
            id="NVA_Knife",
            name="Knife",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.KNIFE,
            type=HLLVLoadoutItemType.LOCKED_ITEM,
            weight=1,
            description_tags=[
                "Melee",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.RIFLEMAN: 0,
                HLLVRole.MEDIC: 0,
                HLLVRole.SPOTTER: 0,
                HLLVRole.SPECIALIST: 0,
                HLLVRole.MACHINE_GUNNER: 0,
                HLLVRole.GRENADIER: 0,
                HLLVRole.ENGINEER: 0,
                HLLVRole.SQUAD_LEADER: 0,
                HLLVRole.SNIPER: 0,
                HLLVRole.CREWMAN: 0,
                HLLVRole.TANK_COMMANDER: 0,
                HLLVRole.SUPPORT: 0,
                HLLVRole.OBSERVER: 0,
                HLLVRole.GUNNER: 0,
                HLLVRole.COMMANDER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def NVA_MEDICAMMOBOX(cls) -> "HLLVLoadoutItem":
        return cls(
            id="NVA_MedicAmmoBox",
            name="Medical Supplies",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.MEDICAL_SUPPLIES,
            type=HLLVLoadoutItemType.UTILITY,
            weight=2,
            description_tags=[
                "Equipment",
                "Utility",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.MEDIC: 0,
            },
        )

    @class_cached_property
    @classmethod
    def NVA_MORTARWRENCH(cls) -> "HLLVLoadoutItem":
        return cls(
            id="NVA_MortarWrench",
            name="Wrench",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.WRENCH,
            type=HLLVLoadoutItemType.LOCKED_ITEM,
            weight=1,
            description_tags=[
                "Role Equipment",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.GUNNER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def NVA_WRENCH(cls) -> "HLLVLoadoutItem":
        return cls(
            id="NVA_Wrench",
            name="Wrench",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.WRENCH,
            type=HLLVLoadoutItemType.LOCKED_ITEM,
            weight=1,
            description_tags=[
                "Role Equipment",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.ENGINEER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def RPD(cls) -> "HLLVLoadoutItem":
        return cls(
            id="RPD",
            name="RPD",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.RPD,
            type=HLLVLoadoutItemType.PRIMARY,
            weight=4,
            description_tags=[
                "Primary",
                "Machine Gun",
                "Automatic",
            ],
            base_ammo=4,
            max_ammo=2,
            ammo_weight=2,
            level_requirements={
                HLLVRole.MACHINE_GUNNER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def RPG2(cls) -> "HLLVLoadoutItem":
        return cls(
            id="RPG2",
            name="RPG-02",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.RPG_02,
            type=HLLVLoadoutItemType.VERSATILE,
            weight=6,
            description_tags=[
                "Secondary",
                "Launcher",
            ],
            base_ammo=2,
            max_ammo=4,
            ammo_weight=3,
            level_requirements={
                HLLVRole.GRENADIER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def RUSTORCH(cls) -> "HLLVLoadoutItem":
        return cls(
            id="RUSTorch",
            name="BLOW TORCH",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.BLOW_TORCH,
            type=HLLVLoadoutItemType.UTILITY,
            weight=1,
            description_tags=[
                "Equipment",
                "Utility",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.SPECIALIST: 0,
            },
        )

    @class_cached_property
    @classmethod
    def TM_46(cls) -> "HLLVLoadoutItem":
        return cls(
            id="TM-46",
            name="TM-46 AT Mine",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.TM_46_AT_MINE,
            type=HLLVLoadoutItemType.LETHAL,
            weight=3,
            description_tags=[
                "Equipment",
                "Lethal",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.ENGINEER: 0,
                HLLVRole.GRENADIER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def TM_46X2(cls) -> "HLLVLoadoutItem":
        return cls(
            id="TM-46x2",
            name="TM-46 AT Mine x2",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.TM_46_AT_MINE,
            type=HLLVLoadoutItemType.LETHAL,
            weight=6,
            description_tags=[
                "Equipment",
                "Lethal",
            ],
            base_ammo=2,
            max_ammo=2,
            ammo_weight=1,
            level_requirements={
                HLLVRole.ENGINEER: 3,
                HLLVRole.GRENADIER: 3,
            },
        )

    @class_cached_property
    @classmethod
    def TYPE53_BAYONET(cls) -> "HLLVLoadoutItem":
        return cls(
            id="Type53_Bayonet",
            name="Type 53",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.TYPE_53,
            type=HLLVLoadoutItemType.PRIMARY,
            weight=4,
            description_tags=[
                "Primary",
                "Rifle",
                "Semi-Automatic",
            ],
            base_ammo=4,
            max_ammo=8,
            ammo_weight=1,
            level_requirements={
                HLLVRole.GRENADIER: 4,
                HLLVRole.SPECIALIST: 4,
                HLLVRole.MEDIC: 4,
                HLLVRole.ENGINEER: 4,
                HLLVRole.SQUAD_LEADER: 4,
                HLLVRole.SPOTTER: 4,
                HLLVRole.SUPPORT: 4,
                HLLVRole.GUNNER: 4,
                HLLVRole.RIFLEMAN: 4,
                HLLVRole.OBSERVER: 4,
                HLLVRole.COMMANDER: 4,
            },
        )

    @class_cached_property
    @classmethod
    def TYPE53_PU(cls) -> "HLLVLoadoutItem":
        return cls(
            id="Type53_PU",
            name="Type 53 PU",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.TYPE_53_PU,
            type=HLLVLoadoutItemType.PRIMARY,
            weight=4,
            description_tags=[
                "Primary",
                "Sniper",
                "Bolt Action",
            ],
            base_ammo=4,
            max_ammo=8,
            ammo_weight=1,
            level_requirements={
                HLLVRole.SNIPER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def TYPE54(cls) -> "HLLVLoadoutItem":
        return cls(
            id="Type54",
            name="Type 54",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.TYPE_54,
            type=HLLVLoadoutItemType.VERSATILE,
            weight=2,
            description_tags=[
                "Secondary",
                "Pistol",
                "Semi-Automatic",
            ],
            base_ammo=6,
            max_ammo=8,
            ammo_weight=1,
            level_requirements={
                HLLVRole.COMMANDER: 0,
                HLLVRole.TANK_COMMANDER: 0,
                HLLVRole.CREWMAN: 0,
                HLLVRole.OBSERVER: 0,
                HLLVRole.SUPPORT: 0,
                HLLVRole.GUNNER: 0,
                HLLVRole.SNIPER: 0,
                HLLVRole.SPOTTER: 0,
                HLLVRole.SQUAD_LEADER: 0,
                HLLVRole.RIFLEMAN: 0,
                HLLVRole.MACHINE_GUNNER: 0,
                HLLVRole.MEDIC: 0,
                HLLVRole.SPECIALIST: 0,
                HLLVRole.GRENADIER: 0,
                HLLVRole.ENGINEER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def TYPE56_AK_BAYONET(cls) -> "HLLVLoadoutItem":
        return cls(
            id="Type56_AK_Bayonet",
            name="Type 56 W/ Bayonet",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.TYPE_56_W_BAYONET,
            type=HLLVLoadoutItemType.PRIMARY,
            weight=4,
            description_tags=[
                "Primary",
                "Rifle",
                "Automatic",
                "Semi-Automatic",
            ],
            base_ammo=4,
            max_ammo=8,
            ammo_weight=1,
            level_requirements={
                HLLVRole.RIFLEMAN: 0,
                HLLVRole.MEDIC: 0,
                HLLVRole.SPOTTER: 0,
                HLLVRole.SPECIALIST: 0,
                HLLVRole.GRENADIER: 0,
                HLLVRole.ENGINEER: 0,
                HLLVRole.SQUAD_LEADER: 0,
                HLLVRole.CREWMAN: 3,
                HLLVRole.TANK_COMMANDER: 3,
                HLLVRole.SUPPORT: 0,
                HLLVRole.OBSERVER: 0,
                HLLVRole.GUNNER: 0,
                HLLVRole.COMMANDER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def TYPE67(cls) -> "HLLVLoadoutItem":
        return cls(
            id="Type67",
            name="Type 67",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.TYPE_67,
            type=HLLVLoadoutItemType.LETHAL,
            weight=2,
            description_tags=[
                "Equipment",
                "Lethal",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.RIFLEMAN: 0,
                HLLVRole.MEDIC: 0,
                HLLVRole.SPOTTER: 0,
                HLLVRole.SPECIALIST: 0,
                HLLVRole.MACHINE_GUNNER: 0,
                HLLVRole.GRENADIER: 0,
                HLLVRole.ENGINEER: 0,
                HLLVRole.SQUAD_LEADER: 0,
                HLLVRole.SNIPER: 0,
                HLLVRole.CREWMAN: 0,
                HLLVRole.TANK_COMMANDER: 0,
                HLLVRole.SUPPORT: 0,
                HLLVRole.OBSERVER: 0,
                HLLVRole.GUNNER: 0,
                HLLVRole.COMMANDER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def TYPE67X2(cls) -> "HLLVLoadoutItem":
        return cls(
            id="Type67x2",
            name="Type 67 x2",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.TYPE_67,
            type=HLLVLoadoutItemType.LETHAL,
            weight=4,
            description_tags=[
                "Equipment",
                "Lethal",
            ],
            base_ammo=2,
            max_ammo=2,
            ammo_weight=1,
            level_requirements={
                HLLVRole.RIFLEMAN: 5,
                HLLVRole.MEDIC: 5,
                HLLVRole.SPOTTER: 5,
                HLLVRole.SPECIALIST: 5,
                HLLVRole.MACHINE_GUNNER: 5,
                HLLVRole.GRENADIER: 5,
                HLLVRole.ENGINEER: 5,
                HLLVRole.SQUAD_LEADER: 5,
                HLLVRole.SNIPER: 5,
                HLLVRole.CREWMAN: 5,
                HLLVRole.TANK_COMMANDER: 5,
                HLLVRole.SUPPORT: 5,
                HLLVRole.OBSERVER: 5,
                HLLVRole.GUNNER: 5,
                HLLVRole.COMMANDER: 5,
            },
        )

    @class_cached_property
    @classmethod
    def TYPE67X3(cls) -> "HLLVLoadoutItem":
        return cls(
            id="Type67x3",
            name="Type 67 x3",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.TYPE_67,
            type=HLLVLoadoutItemType.LETHAL,
            weight=6,
            description_tags=[
                "Equipment",
                "Lethal",
            ],
            base_ammo=3,
            max_ammo=3,
            ammo_weight=1,
            level_requirements={
                HLLVRole.RIFLEMAN: 8,
                HLLVRole.SPOTTER: 8,
                HLLVRole.SPECIALIST: 8,
                HLLVRole.MACHINE_GUNNER: 8,
                HLLVRole.GRENADIER: 8,
                HLLVRole.ENGINEER: 8,
                HLLVRole.SNIPER: 8,
                HLLVRole.SUPPORT: 8,
                HLLVRole.OBSERVER: 8,
                HLLVRole.GUNNER: 8,
            },
        )

    @class_cached_property
    @classmethod
    def USLIGHTMORTAR(cls) -> "HLLVLoadoutItem":
        return cls(
            id="USLightMortar",
            name="Light Mortar",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.LIGHT_MORTAR,
            type=HLLVLoadoutItemType.LOCKED_ITEM,
            weight=1,
            description_tags=[],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.GUNNER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def USMORTARWRENCH(cls) -> "HLLVLoadoutItem":
        return cls(
            id="USMortarWrench",
            name="Wrench ",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.WRENCH,
            type=HLLVLoadoutItemType.LOCKED_ITEM,
            weight=1,
            description_tags=[
                "Role Equipment",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.GUNNER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def USTORCH(cls) -> "HLLVLoadoutItem":
        return cls(
            id="USTorch",
            name="BLOW TORCH",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.BLOW_TORCH,
            type=HLLVLoadoutItemType.UTILITY,
            weight=1,
            description_tags=[
                "Equipment",
                "Utility",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.SPECIALIST: 0,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_M21_AT(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_M21_AT",
            name="M21 AT Mine",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.M21_AT_MINE,
            type=HLLVLoadoutItemType.LETHAL,
            weight=3,
            description_tags=[
                "Equipment",
                "Lethal",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=2,
            level_requirements={
                HLLVRole.GRENADIER: 0,
                HLLVRole.ENGINEER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_M21_ATX2(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_M21_ATx2",
            name="M21 AT Mine x2",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.M21_AT_MINE,
            type=HLLVLoadoutItemType.LETHAL,
            weight=6,
            description_tags=[
                "Equipment",
                "Lethal",
            ],
            base_ammo=2,
            max_ammo=2,
            ammo_weight=2,
            level_requirements={
                HLLVRole.GRENADIER: 3,
                HLLVRole.ENGINEER: 3,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_NVAAMMOBOX(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_NVAAmmoBox",
            name="Ammo Box",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.AMMO_BOX,
            type=HLLVLoadoutItemType.UTILITY,
            weight=3,
            description_tags=[
                "Equipment",
                "Utility",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.SUPPORT: 0,
                HLLVRole.SPOTTER: 0,
                HLLVRole.SQUAD_LEADER: 0,
                HLLVRole.ENGINEER: 0,
                HLLVRole.GRENADIER: 0,
                HLLVRole.SPECIALIST: 0,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_NVABANDAGE(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_NVABandage",
            name="Bandage",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.BANDAGE_NVA,
            type=HLLVLoadoutItemType.UTILITY,
            weight=1,
            description_tags=[
                "Equipment",
                "Utility",
            ],
            base_ammo=2,
            max_ammo=20,
            ammo_weight=1,
            level_requirements={
                HLLVRole.RIFLEMAN: 0,
                HLLVRole.MEDIC: 0,
                HLLVRole.SPOTTER: 0,
                HLLVRole.SPECIALIST: 0,
                HLLVRole.MACHINE_GUNNER: 0,
                HLLVRole.GRENADIER: 0,
                HLLVRole.ENGINEER: 0,
                HLLVRole.SQUAD_LEADER: 0,
                HLLVRole.SNIPER: 0,
                HLLVRole.CREWMAN: 0,
                HLLVRole.TANK_COMMANDER: 0,
                HLLVRole.SUPPORT: 0,
                HLLVRole.OBSERVER: 0,
                HLLVRole.GUNNER: 0,
                HLLVRole.COMMANDER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_NVABINOCULARS(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_NVABinoculars",
            name="Binoculars",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.BINOCULARS,
            type=HLLVLoadoutItemType.UTILITY,
            weight=1,
            description_tags=[
                "Role Equipment",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.TANK_COMMANDER: 0,
                HLLVRole.CREWMAN: 0,
                HLLVRole.SPECIALIST: 0,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_NVAFIELDPAD(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_NVAFieldPad",
            name="FIELD PAD",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.FIELD_PAD,
            type=HLLVLoadoutItemType.LOCKED_ITEM,
            weight=1,
            description_tags=[
                "Role Equipment",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.SQUAD_LEADER: 0,
                HLLVRole.TANK_COMMANDER: 0,
                HLLVRole.OBSERVER: 0,
                HLLVRole.SPOTTER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_NVAFIELDPADCOMMANDER(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_NVAFieldPadCommander",
            name="FIELD PAD",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.FIELD_PAD,
            type=HLLVLoadoutItemType.LOCKED_ITEM,
            weight=1,
            description_tags=[],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.COMMANDER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_NVAFLARE(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_NVAFlare",
            name="Chi Com Signal Pistol",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.CHI_COM_SIGNAL_PISTOL,
            type=HLLVLoadoutItemType.UTILITY,
            weight=4,
            description_tags=[
                "Equipment",
                "Utility",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.COMMANDER: 0,
                HLLVRole.OBSERVER: 0,
                HLLVRole.SPECIALIST: 9,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_NVAHEAMMOBOX(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_NVAHEAmmoBox",
            name="HE Ammo Box",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.HE_AMMO_BOX,
            type=HLLVLoadoutItemType.UTILITY,
            weight=4,
            description_tags=[
                "Equipment",
                "Utility",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.SQUAD_LEADER: 0,
                HLLVRole.MACHINE_GUNNER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_NVAHAMMER(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_NVAHammer",
            name="Hammer",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.HAMMER,
            type=HLLVLoadoutItemType.LOCKED_ITEM,
            weight=1,
            description_tags=[
                "Role Equipment",
                "Utility",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.GUNNER: 0,
                HLLVRole.SUPPORT: 0,
                HLLVRole.RIFLEMAN: 0,
                HLLVRole.SQUAD_LEADER: 0,
                HLLVRole.ENGINEER: 0,
                HLLVRole.MACHINE_GUNNER: 0,
                HLLVRole.MEDIC: 0,
                HLLVRole.SPECIALIST: 0,
                HLLVRole.GRENADIER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_NVAMEDICKIT(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_NVAMedicKit",
            name="Revive",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.REVIVE_NVA,
            type=HLLVLoadoutItemType.LOCKED_ITEM,
            weight=1,
            description_tags=[
                "Role Equipment",
                "Utility",
            ],
            base_ammo=20,
            max_ammo=20,
            ammo_weight=1,
            level_requirements={
                HLLVRole.MEDIC: 0,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_NVASATCHEL(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_NVASatchel",
            name="Satchel Charge",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.SATCHEL_CHARGE,
            type=HLLVLoadoutItemType.LETHAL,
            weight=5,
            description_tags=[
                "Equipment",
                "Lethal",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.ENGINEER: 5,
                HLLVRole.GRENADIER: 5,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_NVASUPPLY(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_NVASupply",
            name="Supplies",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.SUPPLIES,
            type=HLLVLoadoutItemType.LOCKED_ITEM,
            weight=1,
            description_tags=[
                "Role Equipment",
                "Utility",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.SPECIALIST: 0,
                HLLVRole.SUPPORT: 0,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_RDG1(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_RDG1",
            name="RDG-1",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.RDG_1,
            type=HLLVLoadoutItemType.UTILITY,
            weight=1,
            description_tags=[
                "Equipment",
                "Utility",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.RIFLEMAN: 0,
                HLLVRole.MEDIC: 0,
                HLLVRole.SPOTTER: 0,
                HLLVRole.SPECIALIST: 0,
                HLLVRole.MACHINE_GUNNER: 0,
                HLLVRole.GRENADIER: 0,
                HLLVRole.ENGINEER: 0,
                HLLVRole.SQUAD_LEADER: 0,
                HLLVRole.SNIPER: 0,
                HLLVRole.CREWMAN: 0,
                HLLVRole.TANK_COMMANDER: 0,
                HLLVRole.SUPPORT: 0,
                HLLVRole.OBSERVER: 0,
                HLLVRole.GUNNER: 0,
                HLLVRole.COMMANDER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_RDG1X2(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_RDG1x2",
            name="RDG-1 x2",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.RDG_1,
            type=HLLVLoadoutItemType.UTILITY,
            weight=3,
            description_tags=[
                "Equipment",
                "Utility",
            ],
            base_ammo=2,
            max_ammo=2,
            ammo_weight=1,
            level_requirements={
                HLLVRole.RIFLEMAN: 3,
                HLLVRole.MEDIC: 0,
                HLLVRole.SPOTTER: 3,
                HLLVRole.SPECIALIST: 3,
                HLLVRole.MACHINE_GUNNER: 3,
                HLLVRole.GRENADIER: 3,
                HLLVRole.ENGINEER: 3,
                HLLVRole.SQUAD_LEADER: 3,
                HLLVRole.SNIPER: 3,
                HLLVRole.CREWMAN: 3,
                HLLVRole.TANK_COMMANDER: 3,
                HLLVRole.SUPPORT: 3,
                HLLVRole.OBSERVER: 3,
                HLLVRole.GUNNER: 3,
                HLLVRole.COMMANDER: 3,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_RDG1X3(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_RDG1x3",
            name="RDG-1 x3",
            faction=HLLVFaction.NVA,
            weapon=HLLVWeapon.RDG_1,
            type=HLLVLoadoutItemType.UTILITY,
            weight=5,
            description_tags=[
                "Equipment",
                "Utility",
            ],
            base_ammo=3,
            max_ammo=3,
            ammo_weight=1,
            level_requirements={
                HLLVRole.RIFLEMAN: 5,
                HLLVRole.MEDIC: 5,
                HLLVRole.SPOTTER: 5,
                HLLVRole.SPECIALIST: 5,
                HLLVRole.MACHINE_GUNNER: 5,
                HLLVRole.GRENADIER: 5,
                HLLVRole.ENGINEER: 5,
                HLLVRole.SQUAD_LEADER: 5,
                HLLVRole.SNIPER: 5,
                HLLVRole.CREWMAN: 5,
                HLLVRole.TANK_COMMANDER: 5,
                HLLVRole.SUPPORT: 5,
                HLLVRole.OBSERVER: 5,
                HLLVRole.GUNNER: 5,
                HLLVRole.COMMANDER: 5,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_TNT(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_TNT",
            name="WFL_TNT",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.TNT,
            type=HLLVLoadoutItemType.LOCKED_ITEM,
            weight=1,
            description_tags=[
                "Equipment",
                "Lethal",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.RIFLEMAN: 0,
                HLLVRole.MEDIC: 0,
                HLLVRole.SPOTTER: 0,
                HLLVRole.SPECIALIST: 0,
                HLLVRole.MACHINE_GUNNER: 0,
                HLLVRole.GRENADIER: 0,
                HLLVRole.ENGINEER: 0,
                HLLVRole.SQUAD_LEADER: 0,
                HLLVRole.SNIPER: 0,
                HLLVRole.CREWMAN: 0,
                HLLVRole.TANK_COMMANDER: 0,
                HLLVRole.SUPPORT: 0,
                HLLVRole.OBSERVER: 0,
                HLLVRole.GUNNER: 0,
                HLLVRole.PILOT: 0,
                HLLVRole.LOGISTICS_OFFICER: 0,
                HLLVRole.COMMANDER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_USAMMONBOX(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_USAmmonbox",
            name="Small Ammunition Box",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.SMALL_AMMUNITION_BOX,
            type=HLLVLoadoutItemType.UTILITY,
            weight=3,
            description_tags=[
                "Equipment",
                "Utility",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.ENGINEER: 0,
                HLLVRole.SPECIALIST: 0,
                HLLVRole.SPOTTER: 0,
                HLLVRole.SUPPORT: 0,
                HLLVRole.SQUAD_LEADER: 0,
                HLLVRole.GRENADIER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_USBANDAGE(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_USBandage",
            name="BANDAGE",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.BANDAGE_US,
            type=HLLVLoadoutItemType.UTILITY,
            weight=1,
            description_tags=[
                "Equipment",
            ],
            base_ammo=2,
            max_ammo=20,
            ammo_weight=1,
            level_requirements={
                HLLVRole.RIFLEMAN: 0,
                HLLVRole.MEDIC: 0,
                HLLVRole.SPOTTER: 0,
                HLLVRole.SPECIALIST: 0,
                HLLVRole.MACHINE_GUNNER: 0,
                HLLVRole.GRENADIER: 0,
                HLLVRole.ENGINEER: 0,
                HLLVRole.SQUAD_LEADER: 0,
                HLLVRole.SNIPER: 0,
                HLLVRole.CREWMAN: 0,
                HLLVRole.TANK_COMMANDER: 0,
                HLLVRole.SUPPORT: 0,
                HLLVRole.OBSERVER: 0,
                HLLVRole.GUNNER: 0,
                HLLVRole.PILOT: 0,
                HLLVRole.LOGISTICS_OFFICER: 0,
                HLLVRole.COMMANDER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_USBINOCULARS(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_USBinoculars",
            name="M3 Binoculars",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.M3_BINOCULARS,
            type=HLLVLoadoutItemType.UTILITY,
            weight=1,
            description_tags=[
                "Role Equipment",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.SPECIALIST: 0,
                HLLVRole.TANK_COMMANDER: 0,
                HLLVRole.CREWMAN: 0,
                HLLVRole.LOGISTICS_OFFICER: 0,
                HLLVRole.PILOT: 0,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_USFIELDPAD(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_USFieldPad",
            name="FIELD PAD",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.FIELD_PAD,
            type=HLLVLoadoutItemType.LOCKED_ITEM,
            weight=1,
            description_tags=[
                "Role Equipment",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.SQUAD_LEADER: 0,
                HLLVRole.SPOTTER: 0,
                HLLVRole.OBSERVER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_USFIELDPADCOMMANDER(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_USFieldPadCommander",
            name="FIELD PAD",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.FIELD_PAD,
            type=HLLVLoadoutItemType.LOCKED_ITEM,
            weight=1,
            description_tags=[
                "Role Equipment",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.COMMANDER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_USHAMMER(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_USHAmmer",
            name="Hammer",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.HAMMER,
            type=HLLVLoadoutItemType.LOCKED_ITEM,
            weight=1,
            description_tags=[
                "Role Equipment",
                "Utility",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.RIFLEMAN: 0,
                HLLVRole.MEDIC: 0,
                HLLVRole.SPOTTER: 0,
                HLLVRole.SPECIALIST: 0,
                HLLVRole.MACHINE_GUNNER: 0,
                HLLVRole.GRENADIER: 0,
                HLLVRole.ENGINEER: 0,
                HLLVRole.SQUAD_LEADER: 0,
                HLLVRole.SNIPER: 0,
                HLLVRole.CREWMAN: 0,
                HLLVRole.TANK_COMMANDER: 0,
                HLLVRole.SUPPORT: 0,
                HLLVRole.OBSERVER: 0,
                HLLVRole.GUNNER: 0,
                HLLVRole.PILOT: 0,
                HLLVRole.LOGISTICS_OFFICER: 0,
                HLLVRole.COMMANDER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_USHEAMMOBOX(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_USHEAmmoBox",
            name="Explosive Ammo Box",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.EXPLOSIVE_AMMO_BOX,
            type=HLLVLoadoutItemType.UTILITY,
            weight=4,
            description_tags=[
                "Equipment",
                "Utility",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.SQUAD_LEADER: 0,
                HLLVRole.MACHINE_GUNNER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_USMEDICAMMOBOX(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_USMedicAmmoBox",
            name="Medical Supplies",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.MEDICAL_SUPPLIES,
            type=HLLVLoadoutItemType.UTILITY,
            weight=2,
            description_tags=[
                "Role Equipment",
                "Utility",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.MEDIC: 0,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_USMEDICKIT(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_USMedicKit",
            name="REVIVE",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.REVIVE_US,
            type=HLLVLoadoutItemType.LOCKED_ITEM,
            weight=1,
            description_tags=[
                "Role Equipment",
                "Utility",
            ],
            base_ammo=20,
            max_ammo=20,
            ammo_weight=1,
            level_requirements={
                HLLVRole.MEDIC: 0,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_USMORTARWRENCH(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_USMortarWrench",
            name="Wrench",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.WRENCH,
            type=HLLVLoadoutItemType.LOCKED_ITEM,
            weight=1,
            description_tags=[
                "Role Equipment",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.GUNNER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_USSUPPLY(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_USSupply",
            name="Supplies",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.SUPPLIES,
            type=HLLVLoadoutItemType.LOCKED_ITEM,
            weight=1,
            description_tags=[
                "Role Equipment",
                "Utility",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.SPECIALIST: 0,
                HLLVRole.SUPPORT: 0,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_USWRENCH(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_USWrench",
            name="Wrench",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.WRENCH,
            type=HLLVLoadoutItemType.LOCKED_ITEM,
            weight=1,
            description_tags=[
                "Role Equipment",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.ENGINEER: 0,
            },
        )

    @class_cached_property
    @classmethod
    def WFL_US_FLARE(cls) -> "HLLVLoadoutItem":
        return cls(
            id="WFL_US_Flare",
            name="AN-M8 Flare",
            faction=HLLVFaction.US,
            weapon=HLLVWeapon.AN_M8_FLARE,
            type=HLLVLoadoutItemType.UTILITY,
            weight=4,
            description_tags=[
                "Equipment",
                "Utility",
            ],
            base_ammo=1,
            max_ammo=1,
            ammo_weight=1,
            level_requirements={
                HLLVRole.SPECIALIST: 9,
                HLLVRole.COMMANDER: 0,
                HLLVRole.OBSERVER: 0,
            },
        )

    ### INJECT "hllv loadout items" END
