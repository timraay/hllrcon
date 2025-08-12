# ruff: noqa: N802

from enum import StrEnum

from hllrcon.data._utils import IndexedBaseModel, class_cached_property


class RoleType(StrEnum):
    INFANTRY = "Infantry"
    ARMOR = "Armor"
    RECON = "Recon"
    COMMANDER = "Commander"


class Role(IndexedBaseModel[int]):
    name: str
    pretty_name: str
    type: RoleType
    is_squad_leader: bool
    """Whether the player is a squad leader. This also includes the Commander."""

    @class_cached_property
    @classmethod
    def RIFLEMAN(cls) -> "Role":
        return cls(
            id=0,
            name="Rifleman",
            pretty_name="Rifleman",
            type=RoleType.INFANTRY,
            is_squad_leader=False,
        )

    @class_cached_property
    @classmethod
    def ASSAULT(cls) -> "Role":
        return cls(
            id=1,
            name="Assault",
            pretty_name="Assault",
            type=RoleType.INFANTRY,
            is_squad_leader=False,
        )

    @class_cached_property
    @classmethod
    def AUTOMATIC_RIFLEMAN(cls) -> "Role":
        return cls(
            id=2,
            name="AutomaticRifleman",
            pretty_name="Automatic Rifleman",
            type=RoleType.INFANTRY,
            is_squad_leader=False,
        )

    @class_cached_property
    @classmethod
    def MEDIC(cls) -> "Role":
        return cls(
            id=3,
            name="Medic",
            pretty_name="Medic",
            type=RoleType.INFANTRY,
            is_squad_leader=False,
        )

    @class_cached_property
    @classmethod
    def SPOTTER(cls) -> "Role":
        return cls(
            id=4,
            name="Spotter",
            pretty_name="Spotter",
            type=RoleType.RECON,
            is_squad_leader=True,
        )

    @class_cached_property
    @classmethod
    def SUPPORT(cls) -> "Role":
        return cls(
            id=5,
            name="Support",
            pretty_name="Support",
            type=RoleType.INFANTRY,
            is_squad_leader=False,
        )

    @class_cached_property
    @classmethod
    def MACHINE_GUNNER(cls) -> "Role":
        return cls(
            id=6,
            name="HeavyMachineGunner",
            pretty_name="Machine Gunner",
            type=RoleType.INFANTRY,
            is_squad_leader=False,
        )

    @class_cached_property
    @classmethod
    def ANTI_TANK(cls) -> "Role":
        return cls(
            id=7,
            name="AntiTank",
            pretty_name="Anti-Tank",
            type=RoleType.INFANTRY,
            is_squad_leader=False,
        )

    @class_cached_property
    @classmethod
    def ENGINEER(cls) -> "Role":
        return cls(
            id=8,
            name="Engineer",
            pretty_name="Engineer",
            type=RoleType.INFANTRY,
            is_squad_leader=False,
        )

    @class_cached_property
    @classmethod
    def OFFICER(cls) -> "Role":
        return cls(
            id=9,
            name="Officer",
            pretty_name="Officer",
            type=RoleType.INFANTRY,
            is_squad_leader=True,
        )

    @class_cached_property
    @classmethod
    def SNIPER(cls) -> "Role":
        return cls(
            id=10,
            name="Sniper",
            pretty_name="Sniper",
            type=RoleType.RECON,
            is_squad_leader=False,
        )

    @class_cached_property
    @classmethod
    def CREWMAN(cls) -> "Role":
        return cls(
            id=11,
            name="Crewman",
            pretty_name="Crewman",
            type=RoleType.ARMOR,
            is_squad_leader=False,
        )

    @class_cached_property
    @classmethod
    def TANK_COMMANDER(cls) -> "Role":
        return cls(
            id=12,
            name="TankCommander",
            pretty_name="Tank Commander",
            type=RoleType.ARMOR,
            is_squad_leader=True,
        )

    @class_cached_property
    @classmethod
    def COMMANDER(cls) -> "Role":
        return cls(
            id=13,
            name="ArmyCommander",
            pretty_name="Army Commander",
            type=RoleType.COMMANDER,
            is_squad_leader=True,
        )
