# mypy: disable-error-code="prop-decorator"
# ruff: noqa: N802

from enum import StrEnum
from functools import cached_property
from typing import Annotated, NamedTuple, Self

from pydantic import BaseModel, Field, field_serializer

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
    weapon: Annotated[HLLWeapon, model_serializer(str)]
    """The weapon corresponding to this item."""
    ammo: int = 1
    """The amount of this item. For small arms, refers to the number of magazines."""


class HLLLoadout(IndexedBaseModel[HLLLoadoutId]):
    name: str
    faction: Annotated[
        HLLFaction,
        model_serializer(int),
    ]
    role: Annotated[
        HLLRole,
        model_serializer(int),
    ]
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=13,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMALL_AMMUNITION_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WALTHER_P38,
                    ammo=10,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M24_STIELHANDGRANATE,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.GEWEHR_43,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXPLOSIVE_AMMO_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.GEWEHR_43,
                    ammo=10,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.GEWEHR_43,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=3,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.STG44,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SATCHEL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.STG44,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=10,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.FG42,
                    ammo=5,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WALTHER_P38,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MORPHINE_AMPOULE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.LUGER_P08,
                    ammo=16,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MORPHINE_AMPOULE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MEDICAL_SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.S_MINE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMALL_AMMUNITION_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.DIENSTGLAS_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=10,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.DIENSTGLAS_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FLARE_GUN,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMALL_AMMUNITION_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXPLOSIVE_AMMO_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.FLAMMENWERFER_41,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WALTHER_P38,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MG34,
                    ammo=10,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WALTHER_P38,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MG42,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.LUGER_P08,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PANZERSCHRECK,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PAK_40,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SATCHEL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TELLERMINE_43,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.S_MINE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TELLERMINE_43,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.S_MINE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SATCHEL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.LUGER_P08,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.DIENSTGLAS_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.GEWEHR_43,
                    ammo=10,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WALTHER_P38,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.DIENSTGLAS_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=13,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=3,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=3,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.DIENSTGLAS_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K_X8,
                    ammo=19,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WALTHER_P38,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.FG42_X4,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.S_MINE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.WALTHER_P38,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXTERIOR_CUSTOMIZATION,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.WALTHER_P38,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXTERIOR_CUSTOMIZATION,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.WALTHER_P38,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXTERIOR_CUSTOMIZATION,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.LUGER_P08,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.DIENSTGLAS_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXTERIOR_CUSTOMIZATION,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.LUGER_P08,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.DIENSTGLAS_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXTERIOR_CUSTOMIZATION,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.LUGER_P08,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.DIENSTGLAS_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.GEWEHR_43,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WALTHER_P38,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.DIENSTGLAS_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.DIENSTGLAS_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FLARE_GUN,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=10,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WALTHER_P38,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.S_MINE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.DIENSTGLAS_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FLARE_GUN,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.S_MINE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TELLERMINE_43,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.S_MINE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=2,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXPLOSIVE_AMMO_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1_GARAND,
                    ammo=19,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MK2_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMALL_AMMUNITION_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1_CARBINE,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MK2_GRENADE,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M18_SMOKE_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1A1_THOMPSON,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MK2_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M18_SMOKE_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M97_TRENCH_GUN,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MK2_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M18_SMOKE_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1A1_THOMPSON,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MK2_GRENADE,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M18_SMOKE_GRENADE,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_GREASE_GUN,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MK2_GRENADE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M18_SMOKE_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SATCHEL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1918A2_BAR,
                    ammo=10,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MK2_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1A1_THOMPSON,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M18_SMOKE_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1_CARBINE,
                    ammo=3,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.COLT_M1911,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M18_SMOKE_GRENADE,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MORPHINE_SYRETTE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.COLT_M1911,
                    ammo=16,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M18_SMOKE_GRENADE,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MORPHINE_SYRETTE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MEDICAL_SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1A1_THOMPSON,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MK2_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M2_AP_MINE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMALL_AMMUNITION_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WESTINGHOUSE_M3_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1_CARBINE,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M18_SMOKE_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WESTINGHOUSE_M3_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FLARE_GUN,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1_GARAND,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MK2_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_GREASE_GUN,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMALL_AMMUNITION_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXPLOSIVE_AMMO_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M2_FLAMETHROWER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.COLT_M1911,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M18_SMOKE_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.BROWNING_M1919,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.COLT_M1911,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1918A2_BAR,
                    ammo=14,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1_GARAND,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BAZOOKA,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MK2_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1_GARAND,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MK2_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH_57MM_M1,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1A1_THOMPSON,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MK2_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SATCHEL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1A1_AT_MINE,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1_CARBINE,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M2_AP_MINE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1A1_AT_MINE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M97_TRENCH_GUN,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M2_AP_MINE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M18_SMOKE_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SATCHEL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_GREASE_GUN,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MK2_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M18_SMOKE_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1A1_THOMPSON,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.COLT_M1911,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MK2_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M18_SMOKE_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WESTINGHOUSE_M3_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1_CARBINE,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.COLT_M1911,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MK2_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M18_SMOKE_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WESTINGHOUSE_M3_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1_GARAND,
                    ammo=19,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MK2_GRENADE,
                    ammo=3,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M18_SMOKE_GRENADE,
                    ammo=3,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WESTINGHOUSE_M3_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1903_SPRINGFIELD,
                    ammo=17,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.COLT_M1911,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MK2_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1903_SPRINGFIELD,
                    ammo=17,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M18_SMOKE_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M2_AP_MINE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.COLT_M1911,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXTERIOR_CUSTOMIZATION,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.COLT_M1911,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M18_SMOKE_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXTERIOR_CUSTOMIZATION,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.COLT_M1911,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXTERIOR_CUSTOMIZATION,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1A1_THOMPSON,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.COLT_M1911,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WESTINGHOUSE_M3_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXTERIOR_CUSTOMIZATION,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.COLT_M1911,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WESTINGHOUSE_M3_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXTERIOR_CUSTOMIZATION,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1A1_THOMPSON,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.COLT_M1911,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M18_SMOKE_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WESTINGHOUSE_M3_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1_GARAND,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.COLT_M1911,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M18_SMOKE_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WESTINGHOUSE_M3_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1A1_THOMPSON,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MK2_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WESTINGHOUSE_M3_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FLARE_GUN,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1_CARBINE,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.COLT_M1911,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M18_SMOKE_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M2_AP_MINE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WESTINGHOUSE_M3_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FLARE_GUN,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1_CARBINE,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M2_AP_MINE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1A1_AT_MINE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M97_TRENCH_GUN,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M2_AP_MINE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M18_SMOKE_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1_GARAND,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MK2_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_GREASE_GUN,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M18_SMOKE_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXPLOSIVE_AMMO_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M3_KNIFE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MOSIN_NAGANT_1891,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RG_42_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMALL_AMMUNITION_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MOSIN_NAGANT_M38,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RG_42_GRENADE,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RDG_2_SMOKE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXPLOSIVE_AMMO_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MOSIN_NAGANT_M38,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MOLOTOV,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXPLOSIVE_AMMO_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.PPSH_41,
                    ammo=14,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RG_42_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RDG_2_SMOKE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.PPSH_41_W_DRUM,
                    ammo=5,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RG_42_GRENADE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SVT40,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RG_42_GRENADE,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RDG_2_SMOKE,
                    ammo=3,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.PPSH_41_W_DRUM,
                    ammo=5,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MOLOTOV,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SATCHEL_CHARGE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.PPSH_41_W_DRUM,
                    ammo=5,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RG_42_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.PPSH_41_W_DRUM,
                    ammo=5,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MOLOTOV,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MOSIN_NAGANT_91_30,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NAGANT_M1895,
                    ammo=7,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RDG_2_SMOKE,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.REVIVE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.NAGANT_M1895,
                    ammo=18,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RDG_2_SMOKE,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.REVIVE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MEDICAL_SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.PPSH_41,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RG_42_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.POMZ_AP_MINE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMALL_AMMUNITION_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RKKA_8_40,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SVT40,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RDG_2_SMOKE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RKKA_8_40,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FLARE_GUN,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MOSIN_NAGANT_91_30,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RG_42_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SVT40,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMALL_AMMUNITION_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXPLOSIVE_AMMO_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MOSIN_NAGANT_M38,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NAGANT_M1895,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MOLOTOV,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.DP_27,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NAGANT_M1895,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MOSIN_NAGANT_91_30,
                    ammo=16,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PTRS_41,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RG_42_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MOSIN_NAGANT_91_30,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RG_42_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.ZIS_2,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.PPSH_41,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RG_42_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SATCHEL_CHARGE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TM_35_AT_MINE,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.PPSH_41,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BAZOOKA,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RG_42_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MOSIN_NAGANT_91_30,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.POMZ_AP_MINE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TM_35_AT_MINE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MOSIN_NAGANT_91_30,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.POMZ_AP_MINE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RDG_2_SMOKE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SATCHEL_CHARGE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.PPSH_41,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TOKAREV_TT33,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RG_42_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RDG_2_SMOKE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RKKA_8_40,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SVT40,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TOKAREV_TT33,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RG_42_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RDG_2_SMOKE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RKKA_8_40,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.PPSH_41_W_DRUM,
                    ammo=5,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RG_42_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RDG_2_SMOKE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RKKA_8_40,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SCOPED_MOSIN_NAGANT_91_30,
                    ammo=17,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NAGANT_M1895,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RG_42_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SCOPED_SVT40,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.NAGANT_M1895,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXTERIOR_CUSTOMIZATION,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.NAGANT_M1895,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RDG_2_SMOKE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXTERIOR_CUSTOMIZATION,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.NAGANT_M1895,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXTERIOR_CUSTOMIZATION,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.PPSH_41,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NAGANT_M1895,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RKKA_8_40,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXTERIOR_CUSTOMIZATION,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.TOKAREV_TT33,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RKKA_8_40,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXTERIOR_CUSTOMIZATION,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.PPSH_41,
                    ammo=10,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NAGANT_M1895,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RDG_2_SMOKE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RKKA_8_40,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.PPSH_41,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RG_42_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RKKA_8_40,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FLARE_GUN,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SVT40,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TOKAREV_TT33,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RDG_2_SMOKE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.POMZ_AP_MINE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RKKA_8_40,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FLARE_GUN,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MOSIN_NAGANT_M38,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.POMZ_AP_MINE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TM_35_AT_MINE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MOSIN_NAGANT_91_30,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.POMZ_AP_MINE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RDG_2_SMOKE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MOSIN_NAGANT_M38,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RG_42_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SVT40,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.RDG_2_SMOKE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXPLOSIVE_AMMO_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MPL_50_SPADE,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMALL_AMMUNITION_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXPLOSIVE_AMMO_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.STEN_GUN_MK_V,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1928A1_THOMPSON,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1928A1_THOMPSON,
                    ammo=5,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SATCHEL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.BREN_GUN,
                    ammo=10,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1928A1_THOMPSON,
                    ammo=5,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MORPHINE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=21,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MORPHINE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MEDICAL_SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.STEN_GUN_MK_V,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AP_SHRAPNEL_MINE_MK_II,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMALL_AMMUNITION_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_2_MK_5_FLARE_PISTOL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMALL_AMMUNITION_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXPLOSIVE_AMMO_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.FLAMETHROWER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.LEWIS_GUN,
                    ammo=10,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.BREN_GUN,
                    ammo=14,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PIAT,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.ORDNANCE_QF_6_POUNDER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.STEN_GUN_MK_V,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_82_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SATCHEL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AT_MINE_GS_MK_V,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AP_SHRAPNEL_MINE_MK_II,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BOYS_ANTI_TANK_RIFLE,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AP_SHRAPNEL_MINE_MK_II,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AT_MINE_GS_MK_V,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AP_SHRAPNEL_MINE_MK_II,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SATCHEL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.STEN_GUN_MK_V,
                    ammo=5,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_82_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.STEN_GUN_MK_V,
                    ammo=5,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=3,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=3,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I_SNIPER,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I_SNIPER,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AP_SHRAPNEL_MINE_MK_II,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.STEN_GUN_MK_II,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1928A1_THOMPSON,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.STEN_GUN_MK_II,
                    ammo=5,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_2_MK_5_FLARE_PISTOL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AP_SHRAPNEL_MINE_MK_II,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_2_MK_5_FLARE_PISTOL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AP_SHRAPNEL_MINE_MK_II,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AT_MINE_GS_MK_V,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.STEN_GUN_MK_II,
                    ammo=5,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AP_SHRAPNEL_MINE_MK_II,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=2,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.STEN_GUN_MK_II,
                    ammo=5,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXPLOSIVE_AMMO_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=13,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMALL_AMMUNITION_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WALTHER_P38,
                    ammo=10,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M24_STIELHANDGRANATE,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXPLOSIVE_AMMO_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=3,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SATCHEL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=10,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=10,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WALTHER_P38,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MORPHINE_AMPOULE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.LUGER_P08,
                    ammo=16,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MORPHINE_AMPOULE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MEDICAL_SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.S_MINE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMALL_AMMUNITION_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.DIENSTGLAS_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=10,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.DIENSTGLAS_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FLARE_GUN,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMALL_AMMUNITION_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXPLOSIVE_AMMO_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.FLAMMENWERFER_41,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WALTHER_P38,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MG34,
                    ammo=10,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WALTHER_P38,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MG42,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.LUGER_P08,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PANZERSCHRECK,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PAK_40,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SATCHEL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TELLERMINE_43,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.S_MINE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TELLERMINE_43,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.S_MINE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SATCHEL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.LUGER_P08,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.DIENSTGLAS_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WALTHER_P38,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.DIENSTGLAS_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=3,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=3,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.DIENSTGLAS_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K_X8,
                    ammo=19,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WALTHER_P38,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K_X8,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.S_MINE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.WALTHER_P38,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.WALTHER_P38,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.WALTHER_P38,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.LUGER_P08,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.DIENSTGLAS_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.LUGER_P08,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.DIENSTGLAS_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.LUGER_P08,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.DIENSTGLAS_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WALTHER_P38,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.DIENSTGLAS_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.DIENSTGLAS_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FLARE_GUN,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=10,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WALTHER_P38,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.S_MINE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.DIENSTGLAS_6_30,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FLARE_GUN,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.S_MINE,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TELLERMINE_43,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.S_MINE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.KARABINER_98K,
                    ammo=12,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.M43_STIELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=2,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.MP40,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NB39_NEBELHANDGRANATE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXPLOSIVE_AMMO_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FELDSPATEN,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMALL_AMMUNITION_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXPLOSIVE_AMMO_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.STEN_GUN_MK_II,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1928A1_THOMPSON,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1928A1_THOMPSON,
                    ammo=5,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SATCHEL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.BREN_GUN,
                    ammo=10,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1928A1_THOMPSON,
                    ammo=5,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MORPHINE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=21,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MORPHINE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MEDICAL_SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1928A1_THOMPSON,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AP_SHRAPNEL_MINE_MK_II,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMALL_AMMUNITION_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_2_MK_5_FLARE_PISTOL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMALL_AMMUNITION_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXPLOSIVE_AMMO_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.FLAMETHROWER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.LEWIS_GUN,
                    ammo=10,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.BREN_GUN,
                    ammo=14,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PIAT,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.ORDNANCE_QF_6_POUNDER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1928A1_THOMPSON,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AP_SHRAPNEL_MINE_MK_II,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AT_MINE_GS_MK_V,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SATCHEL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BOYS_ANTI_TANK_RIFLE,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AP_SHRAPNEL_MINE_MK_II,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AT_MINE_GS_MK_V,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AP_SHRAPNEL_MINE_MK_II,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SATCHEL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.STEN_GUN_MK_II,
                    ammo=5,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1928A1_THOMPSON,
                    ammo=5,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=3,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=3,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I_SNIPER,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I_SNIPER,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AP_SHRAPNEL_MINE_MK_II,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXTERIOR_CUSTOMIZATION,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXTERIOR_CUSTOMIZATION,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXTERIOR_CUSTOMIZATION,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.STEN_GUN_MK_II,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXTERIOR_CUSTOMIZATION,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXTERIOR_CUSTOMIZATION,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.M1928A1_THOMPSON,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.STEN_GUN_MK_II,
                    ammo=5,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_2_MK_5_FLARE_PISTOL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WEBLEY_MK_VI,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AP_SHRAPNEL_MINE_MK_II,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_2_MK_5_FLARE_PISTOL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AP_SHRAPNEL_MINE_MK_II,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AT_MINE_GS_MK_V,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.BREN_GUN,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AP_SHRAPNEL_MINE_MK_II,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=2,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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
                HLLLoadoutItem(
                    weapon=HLLWeapon.STEN_GUN_MK_II,
                    ammo=5,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXPLOSIVE_AMMO_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_RIFLEMAN_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CAN,
            role=HLLRole.RIFLEMAN,
            requires_level=1,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMALL_AMMUNITION_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_RIFLEMAN_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.CAN,
            role=HLLRole.RIFLEMAN,
            requires_level=3,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_RIFLEMAN_TROOPER(cls) -> "HLLLoadout":
        return cls(
            name="Trooper",
            faction=HLLFaction.CAN,
            role=HLLRole.RIFLEMAN,
            requires_level=6,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXPLOSIVE_AMMO_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_ASSAULT_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CAN,
            role=HLLRole.ASSAULT,
            requires_level=1,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.STEN_GUN_MK_II,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_ASSAULT_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.CAN,
            role=HLLRole.ASSAULT,
            requires_level=3,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.LANCHESTER,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_ASSAULT_GRENADIER(cls) -> "HLLLoadout":
        return cls(
            name="Grenadier",
            faction=HLLFaction.CAN,
            role=HLLRole.ASSAULT,
            requires_level=6,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_ASSAULT_RAIDER(cls) -> "HLLLoadout":
        return cls(
            name="Raider",
            faction=HLLFaction.CAN,
            role=HLLRole.ASSAULT,
            requires_level=9,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.LANCHESTER,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SATCHEL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_AUTOMATIC_RIFLEMAN_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CAN,
            role=HLLRole.AUTOMATIC_RIFLEMAN,
            requires_level=1,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.BREN_GUN,
                    ammo=10,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_AUTOMATIC_RIFLEMAN_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.CAN,
            role=HLLRole.AUTOMATIC_RIFLEMAN,
            requires_level=3,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.STEN_GUN_MK_II,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_MEDIC_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CAN,
            role=HLLRole.MEDIC,
            requires_level=1,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.ENFIELD_NO_2_MK_I,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MORPHINE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_MEDIC_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.CAN,
            role=HLLRole.MEDIC,
            requires_level=3,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.FN_INGLIS_NO_2_MK_I,
                    ammo=21,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MORPHINE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=20,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MEDICAL_SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_SPOTTER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CAN,
            role=HLLRole.SPOTTER,
            requires_level=1,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.LANCHESTER,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AP_SHRAPNEL_MINE_MK_II,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMALL_AMMUNITION_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_SPOTTER_SCOUT(cls) -> "HLLLoadout":
        return cls(
            name="Scout",
            faction=HLLFaction.CAN,
            role=HLLRole.SPOTTER,
            requires_level=3,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_2_MK_5_FLARE_PISTOL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_SUPPORT_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CAN,
            role=HLLRole.SUPPORT,
            requires_level=1,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_SUPPORT_AMMO_CARRIER(cls) -> "HLLLoadout":
        return cls(
            name="Ammo Carrier",
            faction=HLLFaction.CAN,
            role=HLLRole.SUPPORT,
            requires_level=3,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMALL_AMMUNITION_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXPLOSIVE_AMMO_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_SUPPORT_FLAMER(cls) -> "HLLLoadout":
        return cls(
            name="Flamer",
            faction=HLLFaction.CAN,
            role=HLLRole.SUPPORT,
            requires_level=8,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.FLAMETHROWER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FN_INGLIS_NO_2_MK_I,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_MACHINE_GUNNER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CAN,
            role=HLLRole.MACHINE_GUNNER,
            requires_level=1,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.BREN_GUN,
                    ammo=14,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FN_INGLIS_NO_2_MK_I,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_ANTI_TANK_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CAN,
            role=HLLRole.ANTI_TANK,
            requires_level=1,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PIAT,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_ANTI_TANK_GUN_CREW(cls) -> "HLLLoadout":
        return cls(
            name="Gun Crew",
            faction=HLLFaction.CAN,
            role=HLLRole.ANTI_TANK,
            requires_level=3,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.ORDNANCE_QF_6_POUNDER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_ANTI_TANK_AMBUSHER(cls) -> "HLLLoadout":
        return cls(
            name="Ambusher",
            faction=HLLFaction.CAN,
            role=HLLRole.ANTI_TANK,
            requires_level=6,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.STEN_GUN_MK_II,
                    ammo=8,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_82_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AP_SHRAPNEL_MINE_MK_II,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AT_MINE_GS_MK_V,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SATCHEL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_ENGINEER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CAN,
            role=HLLRole.ENGINEER,
            requires_level=1,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AP_SHRAPNEL_MINE_MK_II,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AT_MINE_GS_MK_V,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_ENGINEER_SAPPER(cls) -> "HLLLoadout":
        return cls(
            name="Sapper",
            faction=HLLFaction.CAN,
            role=HLLRole.ENGINEER,
            requires_level=3,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AP_SHRAPNEL_MINE_MK_II,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SATCHEL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_ENGINEER_FIELD_ENGINEER(cls) -> "HLLLoadout":
        return cls(
            name="Field Engineer",
            faction=HLLFaction.CAN,
            role=HLLRole.ENGINEER,
            requires_level=6,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.STEN_GUN_MK_II,
                    ammo=5,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_82_GRENADE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_OFFICER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CAN,
            role=HLLRole.OFFICER,
            requires_level=1,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.STEN_GUN_MK_II,
                    ammo=5,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.ENFIELD_NO_2_MK_I,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_OFFICER_POINT_MAN(cls) -> "HLLLoadout":
        return cls(
            name="Point Man",
            faction=HLLFaction.CAN,
            role=HLLRole.OFFICER,
            requires_level=3,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FN_INGLIS_NO_2_MK_I,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_OFFICER_NCO(cls) -> "HLLLoadout":
        return cls(
            name="NCO",
            faction=HLLFaction.CAN,
            role=HLLRole.OFFICER,
            requires_level=6,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.SMLE_NO_1_MK_III,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=3,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=3,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_SNIPER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CAN,
            role=HLLRole.SNIPER,
            requires_level=1,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I_SNIPER,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FN_INGLIS_NO_2_MK_I,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_SNIPER_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.CAN,
            role=HLLRole.SNIPER,
            requires_level=3,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I_SNIPER,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AP_SHRAPNEL_MINE_MK_II,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_CREWMAN_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CAN,
            role=HLLRole.CREWMAN,
            requires_level=1,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.ENFIELD_NO_2_MK_I,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_CREWMAN_MECHANIC(cls) -> "HLLLoadout":
        return cls(
            name="Mechanic",
            faction=HLLFaction.CAN,
            role=HLLRole.CREWMAN,
            requires_level=3,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.ENFIELD_NO_2_MK_I,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_CREWMAN_TECHNICIAN(cls) -> "HLLLoadout":
        return cls(
            name="Technician",
            faction=HLLFaction.CAN,
            role=HLLRole.CREWMAN,
            requires_level=7,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.ENFIELD_NO_2_MK_I,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_TANK_COMMANDER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CAN,
            role=HLLRole.TANK_COMMANDER,
            requires_level=1,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.STEN_GUN_MK_II,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.ENFIELD_NO_2_MK_I,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_TANK_COMMANDER_MECHANIC(cls) -> "HLLLoadout":
        return cls(
            name="Mechanic",
            faction=HLLFaction.CAN,
            role=HLLRole.TANK_COMMANDER,
            requires_level=3,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.ENFIELD_NO_2_MK_I,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_COMMANDER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CAN,
            role=HLLRole.COMMANDER,
            requires_level=1,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.ENFIELD_NO_2_MK_I,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_COMMANDER_VETERAN(cls) -> "HLLLoadout":
        return cls(
            name="Veteran",
            faction=HLLFaction.CAN,
            role=HLLRole.COMMANDER,
            requires_level=3,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.STEN_GUN_MK_II,
                    ammo=5,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FN_INGLIS_NO_2_MK_I,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_ARTILLERY_OBSERVER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CAN,
            role=HLLRole.ARTILLERY_OBSERVER,
            requires_level=1,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.STEN_GUN_MK_II,
                    ammo=5,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_2_MK_5_FLARE_PISTOL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_ARTILLERY_OBSERVER_JUNIOR_SERGEANT(cls) -> "HLLLoadout":
        return cls(
            name="Junior Sergeant",
            faction=HLLFaction.CAN,
            role=HLLRole.ARTILLERY_OBSERVER,
            requires_level=3,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.ENFIELD_NO_2_MK_I,
                    ammo=4,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WATCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AP_SHRAPNEL_MINE_MK_II,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.PRISM_NO_2_MK_II_X6,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_2_MK_5_FLARE_PISTOL,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_OPERATOR_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CAN,
            role=HLLRole.OPERATOR,
            requires_level=1,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.WRENCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AP_SHRAPNEL_MINE_MK_II,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AT_MINE_GS_MK_V,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_OPERATOR_PIONEER(cls) -> "HLLLoadout":
        return cls(
            name="Pioneer",
            faction=HLLFaction.CAN,
            role=HLLRole.OPERATOR,
            requires_level=3,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.STEN_GUN_MK_II,
                    ammo=5,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.AP_SHRAPNEL_MINE_MK_II,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.TORCH,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_GUNNER_STANDARD_ISSUE(cls) -> "HLLLoadout":
        return cls(
            name="Standard Issue",
            faction=HLLFaction.CAN,
            role=HLLRole.GUNNER,
            requires_level=1,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.RIFLE_NO_4_MK_I,
                    ammo=6,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.MILLS_BOMB,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
            ],
        )

    @class_cached_property
    @classmethod
    def CAN_GUNNER_AMMO_CARRIER(cls) -> "HLLLoadout":
        return cls(
            name="Ammo Carrier",
            faction=HLLFaction.CAN,
            role=HLLRole.GUNNER,
            requires_level=3,
            items=[
                HLLLoadoutItem(
                    weapon=HLLWeapon.STEN_GUN_MK_II,
                    ammo=5,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.BANDAGE,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.NO_77,
                    ammo=2,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.SUPPLIES,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.EXPLOSIVE_AMMO_BOX,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.HAMMER,
                    ammo=1,
                ),
                HLLLoadoutItem(
                    weapon=HLLWeapon.FAIRBAIRN_SYKES,
                    ammo=1,
                ),
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


class HLLVLoadoutItemLevelRequirementsSerializedEntry(BaseModel, frozen=True):
    role: Annotated[HLLVRole, model_serializer(int)]
    level: int


class HLLVLoadoutItem(IndexedBaseModel[str]):
    id: str
    name: str
    faction: Annotated[HLLVFaction, model_serializer(int)]
    weapon: Annotated[HLLVWeapon, model_serializer(str)]
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

    @field_serializer(
        "level_requirements",
        return_type=list[HLLVLoadoutItemLevelRequirementsSerializedEntry],
    )
    def serialize_level_requirements(
        self,
        value: dict[HLLVRole, int],
    ) -> list[HLLVLoadoutItemLevelRequirementsSerializedEntry]:
        return [
            HLLVLoadoutItemLevelRequirementsSerializedEntry(
                role=role,
                level=level,
            )
            for role, level in value.items()
        ]

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
