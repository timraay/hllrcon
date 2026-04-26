# ruff: noqa: N802
from enum import StrEnum
from typing import Generic, TypeAlias, TypeVar

from hllrcon.data._utils import IndexedBaseModel, class_cached_property

RoleTypeT = TypeVar("RoleTypeT", bound=StrEnum)


class HLLRoleType(StrEnum):
    INFANTRY = "Infantry"
    ARMOR = "Armor"
    ARTILLERY = "Artillery"
    RECON = "Recon"
    COMMANDER = "Commander"


class HLLVRoleType(StrEnum):
    INFANTRY = "Infantry"
    ARMOR = "Armor"
    MORTAR = "Mortar"
    RECON = "Recon"
    HELICOPTER = "Helicopter"
    COMMANDER = "Commander"


RoleType: TypeAlias = HLLRoleType | HLLVRoleType


class _Role(IndexedBaseModel[int], Generic[RoleTypeT]):
    id: int
    name: str
    pretty_name: str
    type: RoleTypeT
    is_squad_leader: bool
    """Whether this role is exclusive to the squad leader.

    Roles included are:
    - Commander
    - Officer
    - Tank Commander
    - Spotter
    """
    kill_combat_score: int
    """The Combat Effectiveness score gained when killing a player with this role."""
    assist_combat_score: int
    """The Combat Effectiveness score gained when assisting in the kill of a player with
    this role. Assists are gained when a player you downed gets killed by another."""

    @property
    def is_infantry(self) -> bool:
        """Whether the role is associated with infantry units.

        Roles included are:
        - Officer
        - Rifleman
        - Assault
        - Automatic Rifleman
        - Medic
        - Support
        - Machine Gunner
        - Anti-Tank
        - Engineer
        """
        return self.type in (HLLRoleType.INFANTRY, HLLVRoleType.INFANTRY)

    @property
    def is_tanker(self) -> bool:
        """Whether the role is associated with armor units.

        Roles included are:
        - Tank Commander
        - Crewman
        """
        return self.type in (HLLRoleType.ARMOR, HLLVRoleType.ARMOR)

    @property
    def is_artillery(self) -> bool:
        """Whether the role is associated with artillery units.

        Roles included are:
        - Artillery Observer
        - Operator
        - Gunner
        """
        return self.type == HLLRoleType.ARTILLERY

    @property
    def is_mortar(self) -> bool:
        """Whether the role is associated with mortar units.

        Roles included are:
        - Mortar Observer
        - Operator
        - Gunner
        """
        # TODO: Update docstring
        return self.type == HLLVRoleType.MORTAR

    @property
    def is_recon(self) -> bool:
        """Whether the role is associated with recon units.

        Roles included are:
        - Spotter
        - Sniper
        """
        return self.type in (HLLRoleType.RECON, HLLVRoleType.RECON)


class HLLRole(_Role[HLLRoleType]):
    @class_cached_property
    @classmethod
    def RIFLEMAN(cls) -> "HLLRole":
        return cls(
            id=0,
            name="Rifleman",
            pretty_name="Rifleman",
            type=HLLRoleType.INFANTRY,
            is_squad_leader=False,
            kill_combat_score=3,
            assist_combat_score=2,
        )

    @class_cached_property
    @classmethod
    def ASSAULT(cls) -> "HLLRole":
        return cls(
            id=1,
            name="Assault",
            pretty_name="Assault",
            type=HLLRoleType.INFANTRY,
            is_squad_leader=False,
            kill_combat_score=6,
            assist_combat_score=4,
        )

    @class_cached_property
    @classmethod
    def AUTOMATIC_RIFLEMAN(cls) -> "HLLRole":
        return cls(
            id=2,
            name="AutomaticRifleman",
            pretty_name="Automatic Rifleman",
            type=HLLRoleType.INFANTRY,
            is_squad_leader=False,
            kill_combat_score=6,
            assist_combat_score=4,
        )

    @class_cached_property
    @classmethod
    def MEDIC(cls) -> "HLLRole":
        return cls(
            id=3,
            name="Medic",
            pretty_name="Medic",
            type=HLLRoleType.INFANTRY,
            is_squad_leader=False,
            kill_combat_score=6,
            assist_combat_score=4,
        )

    @class_cached_property
    @classmethod
    def SPOTTER(cls) -> "HLLRole":
        return cls(
            id=4,
            name="Spotter",
            pretty_name="Spotter",
            type=HLLRoleType.RECON,
            is_squad_leader=True,
            kill_combat_score=6,
            assist_combat_score=4,
        )

    @class_cached_property
    @classmethod
    def SUPPORT(cls) -> "HLLRole":
        return cls(
            id=5,
            name="Support",
            pretty_name="Support",
            type=HLLRoleType.INFANTRY,
            is_squad_leader=False,
            kill_combat_score=6,
            assist_combat_score=4,
        )

    @class_cached_property
    @classmethod
    def MACHINE_GUNNER(cls) -> "HLLRole":
        return cls(
            id=6,
            name="HeavyMachineGunner",
            pretty_name="Machine Gunner",
            type=HLLRoleType.INFANTRY,
            is_squad_leader=False,
            kill_combat_score=9,
            assist_combat_score=6,
        )

    @class_cached_property
    @classmethod
    def ANTI_TANK(cls) -> "HLLRole":
        return cls(
            id=7,
            name="AntiTank",
            pretty_name="Anti-Tank",
            type=HLLRoleType.INFANTRY,
            is_squad_leader=False,
            kill_combat_score=9,
            assist_combat_score=6,
        )

    @class_cached_property
    @classmethod
    def ENGINEER(cls) -> "HLLRole":
        return cls(
            id=8,
            name="Engineer",
            pretty_name="Engineer",
            type=HLLRoleType.INFANTRY,
            is_squad_leader=False,
            kill_combat_score=9,
            assist_combat_score=6,
        )

    @class_cached_property
    @classmethod
    def OFFICER(cls) -> "HLLRole":
        return cls(
            id=9,
            name="Officer",
            pretty_name="Officer",
            type=HLLRoleType.INFANTRY,
            is_squad_leader=True,
            kill_combat_score=9,
            assist_combat_score=6,
        )

    @class_cached_property
    @classmethod
    def SNIPER(cls) -> "HLLRole":
        return cls(
            id=10,
            name="Sniper",
            pretty_name="Sniper",
            type=HLLRoleType.RECON,
            is_squad_leader=False,
            kill_combat_score=6,
            assist_combat_score=4,
        )

    @class_cached_property
    @classmethod
    def CREWMAN(cls) -> "HLLRole":
        return cls(
            id=11,
            name="Crewman",
            pretty_name="Crewman",
            type=HLLRoleType.ARMOR,
            is_squad_leader=False,
            kill_combat_score=3,
            assist_combat_score=2,
        )

    @class_cached_property
    @classmethod
    def TANK_COMMANDER(cls) -> "HLLRole":
        return cls(
            id=12,
            name="TankCommander",
            pretty_name="Tank Commander",
            type=HLLRoleType.ARMOR,
            is_squad_leader=True,
            kill_combat_score=9,
            assist_combat_score=6,
        )

    @class_cached_property
    @classmethod
    def COMMANDER(cls) -> "HLLRole":
        return cls(
            id=13,
            name="ArmyCommander",
            pretty_name="Commander",
            type=HLLRoleType.COMMANDER,
            is_squad_leader=True,
            kill_combat_score=12,
            assist_combat_score=8,
        )

    @class_cached_property
    @classmethod
    def ARMY_COMMANDER(cls) -> "HLLRole":
        return cls.COMMANDER

    @class_cached_property
    @classmethod
    def ARTILLERY_OBSERVER(cls) -> "HLLRole":
        return cls(
            id=14,
            name="ArtilleryObserver",
            pretty_name="Artillery Observer",
            type=HLLRoleType.ARTILLERY,
            is_squad_leader=True,
            kill_combat_score=9,
            assist_combat_score=6,
        )

    @class_cached_property
    @classmethod
    def OPERATOR(cls) -> "HLLRole":
        return cls(
            id=15,
            name="Operator",
            pretty_name="Operator",
            type=HLLRoleType.ARTILLERY,
            is_squad_leader=False,
            kill_combat_score=9,
            assist_combat_score=6,
        )

    @class_cached_property
    @classmethod
    def GUNNER(cls) -> "HLLRole":
        return cls(
            id=16,
            name="Gunner",
            pretty_name="Gunner",
            type=HLLRoleType.ARTILLERY,
            is_squad_leader=False,
            kill_combat_score=6,
            assist_combat_score=4,
        )


class HLLVRole(_Role):
    # TODO: Add roles
    pass


Role: TypeAlias = HLLRole | HLLVRole
