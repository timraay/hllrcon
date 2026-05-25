# ruff: noqa: N802
from enum import StrEnum
from typing import TYPE_CHECKING, Literal, TypeAlias

from pydantic import BaseModel

from hllrcon.data._utils import IndexedBaseModel, class_cached_property

if TYPE_CHECKING:
    from hllrcon.data.factions import HLLVFaction
    from hllrcon.data.loadouts import HLLVLoadoutItem
    from hllrcon.data.weapons import HLLVWeapon


class RoleType(StrEnum):
    INFANTRY = "Infantry"
    ARMOR = "Armor"
    ARTILLERY = "Artillery"
    MORTAR = "Mortar"
    RECON = "Recon"
    HELICOPTER = "Helicopter"
    COMMANDER = "Commander"


class _Role(IndexedBaseModel[int]):
    id: int
    name: str
    pretty_name: str
    type: RoleType
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
        """Whether the role is associated with infantry units."""
        return self.type == RoleType.INFANTRY

    @property
    def is_tanker(self) -> bool:
        """Whether the role is associated with armor units."""
        return self.type == RoleType.ARMOR

    @property
    def is_artillery(self) -> bool:
        """Whether the role is associated with artillery units."""
        return self.type == RoleType.ARTILLERY

    @property
    def is_mortar(self) -> bool:
        """Whether the role is associated with mortar units."""
        # TODO: Update docstring
        return self.type == RoleType.MORTAR

    @property
    def is_recon(self) -> bool:
        """Whether the role is associated with recon units."""
        return self.type == RoleType.RECON

    @property
    def is_helicopter(self) -> bool:
        """Whether the role is associated with helicopter units."""
        return self.type == RoleType.HELICOPTER

    @staticmethod
    def clamp_level(level: int) -> int:
        """Clamp a role level to the valid range of 1 to 10 inclusive."""
        if level < 1:
            return 1
        if level > 10:
            return 10
        return level


class HLLRole(_Role):
    if TYPE_CHECKING:

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

        @property
        def is_tanker(self) -> bool:
            """Whether the role is associated with armor units.

            Roles included are:
            - Tank Commander
            - Crewman
            """

        @property
        def is_artillery(self) -> bool:
            """Whether the role is associated with artillery units.

            Roles included are:
            - Artillery Observer
            - Operator
            - Gunner
            """

        @property
        def is_mortar(self) -> Literal[False]:
            """Whether the role is associated with mortar units.

            Since HLL does not have dedicated mortar units, this is always false.
            """

        @property
        def is_recon(self) -> bool:
            """Whether the role is associated with recon units.

            Roles included are:
            - Spotter
            - Sniper
            """

        @property
        def is_helicopter(self) -> Literal[False]:
            """Whether the role is associated with helicopter units.

            Since HLL does not have dedicated helicopter units, this is always false.
            """

    @class_cached_property
    @classmethod
    def RIFLEMAN(cls) -> "HLLRole":
        return cls(
            id=0,
            name="Rifleman",
            pretty_name="Rifleman",
            type=RoleType.INFANTRY,
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
            type=RoleType.INFANTRY,
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
            type=RoleType.INFANTRY,
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
            type=RoleType.INFANTRY,
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
            type=RoleType.RECON,
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
            type=RoleType.INFANTRY,
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
            type=RoleType.INFANTRY,
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
            type=RoleType.INFANTRY,
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
            type=RoleType.INFANTRY,
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
            type=RoleType.INFANTRY,
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
            type=RoleType.RECON,
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
            type=RoleType.ARMOR,
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
            type=RoleType.ARMOR,
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
            type=RoleType.COMMANDER,
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
            type=RoleType.ARTILLERY,
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
            type=RoleType.ARTILLERY,
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
            type=RoleType.ARTILLERY,
            is_squad_leader=False,
            kill_combat_score=6,
            assist_combat_score=4,
        )


class HLLVRoleProgression(BaseModel, frozen=True):
    level: int
    max_weight: int
    secondary_slot_unlocked: bool
    extra_ammo_unlocked: bool
    lethal_slots: int
    utility_slots: int


class HLLVRole(_Role):
    progression: list[HLLVRoleProgression]

    if TYPE_CHECKING:
        is_squad_leader: bool
        """Whether this role is exclusive to the squad leader.

        Roles included are:
        - Commander
        - Squad Leader
        - Tank Commander
        - Spotter
        - Observer
        - Logistics Officer
        """

        @property
        def is_infantry(self) -> bool:
            """Whether the role is associated with infantry units.

            Roles included are:
            - Squad Leader
            - Rifleman
            - Medic
            - Specialist
            - Machine Gunner
            - Grenadier
            - Engineer
            """

        @property
        def is_tanker(self) -> bool:
            """Whether the role is associated with armor units.

            Roles included are:
            - Tank Commander
            - Crewman
            """

        @property
        def is_artillery(self) -> Literal[False]:
            """Whether the role is associated with artillery units.

            Since HLLV does not have dedicated artillery units, this is always false.
            """

        @property
        def is_mortar(self) -> bool:
            """Whether the role is associated with mortar units.

            Roles included are:
            - Observer
            - Support
            - Gunner
            """

        @property
        def is_recon(self) -> bool:
            """Whether the role is associated with recon units.

            Roles included are:
            - Spotter
            - Sniper
            """

        @property
        def is_helicopter(self) -> bool:
            """Whether the role is associated with helicopter units.

            Roles included are:
            - Logistics Officer
            - Pilot
            """

    def get_available_capacity(self, level: int) -> HLLVRoleProgression:
        """Get a role's available capacity at a given level.

        Parameters
        ----------
        level : int
            The role level to get the unlocks for. Must be between 1 and 10 inclusive.

        Returns
        -------
        HLLVRoleProgression
            The unlocks available at the given level.

        """
        return self.progression[self.clamp_level(level) - 1]

    def get_available_items(
        self,
        level: int,
        faction: "HLLVFaction",
    ) -> set["HLLVLoadoutItem"]:
        """Get the loadout items available to a role at a given level.

        Parameters
        ----------
        level : int
            The role level to get the unlocks for. Must be between 1 and 10 inclusive.
        faction : HLLVFaction
            The faction to get the unlocks for.

        Returns
        -------
        set[HLLVLoadoutItem]
            The loadout items available to the role at the given level.

        """
        from hllrcon.data.loadouts import HLLVLoadoutItem  # noqa: PLC0415

        clamped_level = self.clamp_level(level)

        return {
            item
            for item in HLLVLoadoutItem.all()
            if (
                item.faction is faction
                and self in item.level_requirements
                and item.level_requirements[self] <= clamped_level
            )
        }

    def get_available_weapons(
        self,
        level: int,
        faction: "HLLVFaction",
    ) -> set["HLLVWeapon"]:
        """Get the weapons available to a role at a given level.

        Parameters
        ----------
        level : int
            The role level to get the unlocks for. Must be between 1 and 10 inclusive.
        faction : HLLVFaction
            The faction to get the unlocks for.

        Returns
        -------
        set[HLLVWeapon]
            The weapons available to the role at the given level.

        """
        return {item.weapon for item in self.get_available_items(level, faction)}

    @class_cached_property
    @classmethod
    def RIFLEMAN(cls) -> "HLLVRole":
        return cls(
            id=0,
            name="Rifleman",
            pretty_name="Rifleman",
            type=RoleType.INFANTRY,
            is_squad_leader=False,
            kill_combat_score=3,
            assist_combat_score=2,
            ### INJECT "hllv progression Rifleman" START
            progression=[
                HLLVRoleProgression(
                    level=1,
                    max_weight=6,
                    secondary_slot_unlocked=False,
                    extra_ammo_unlocked=False,
                    lethal_slots=0,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=2,
                    max_weight=7,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=False,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=3,
                    max_weight=8,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=4,
                    max_weight=9,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=5,
                    max_weight=10,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=6,
                    max_weight=11,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=7,
                    max_weight=12,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=8,
                    max_weight=13,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=9,
                    max_weight=14,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=10,
                    max_weight=15,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=2,
                ),
            ],
            ### INJECT "hllv progression Rifleman" END
        )

    @class_cached_property
    @classmethod
    def MEDIC(cls) -> "HLLVRole":
        return cls(
            id=3,
            name="Medic",
            pretty_name="Medic",
            type=RoleType.INFANTRY,
            is_squad_leader=False,
            kill_combat_score=6,
            assist_combat_score=4,
            ### INJECT "hllv progression Medic" START
            progression=[
                HLLVRoleProgression(
                    level=1,
                    max_weight=6,
                    secondary_slot_unlocked=False,
                    extra_ammo_unlocked=False,
                    lethal_slots=0,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=2,
                    max_weight=7,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=False,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=3,
                    max_weight=8,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=4,
                    max_weight=9,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=5,
                    max_weight=10,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=3,
                ),
                HLLVRoleProgression(
                    level=6,
                    max_weight=11,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=3,
                ),
                HLLVRoleProgression(
                    level=7,
                    max_weight=12,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=4,
                ),
                HLLVRoleProgression(
                    level=8,
                    max_weight=13,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=4,
                ),
                HLLVRoleProgression(
                    level=9,
                    max_weight=14,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=4,
                ),
                HLLVRoleProgression(
                    level=10,
                    max_weight=15,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=4,
                ),
            ],
            ### INJECT "hllv progression Medic" END
        )

    @class_cached_property
    @classmethod
    def SPOTTER(cls) -> "HLLVRole":
        return cls(
            id=4,
            name="Spotter",
            pretty_name="Spotter",
            type=RoleType.RECON,
            is_squad_leader=True,
            kill_combat_score=6,
            assist_combat_score=4,
            ### INJECT "hllv progression Spotter" START
            progression=[
                HLLVRoleProgression(
                    level=1,
                    max_weight=6,
                    secondary_slot_unlocked=False,
                    extra_ammo_unlocked=False,
                    lethal_slots=0,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=2,
                    max_weight=7,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=False,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=3,
                    max_weight=8,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=4,
                    max_weight=9,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=5,
                    max_weight=10,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=3,
                ),
                HLLVRoleProgression(
                    level=6,
                    max_weight=11,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=3,
                ),
                HLLVRoleProgression(
                    level=7,
                    max_weight=12,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=4,
                ),
                HLLVRoleProgression(
                    level=8,
                    max_weight=13,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=4,
                ),
                HLLVRoleProgression(
                    level=9,
                    max_weight=14,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=4,
                ),
                HLLVRoleProgression(
                    level=10,
                    max_weight=15,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=4,
                ),
            ],
            ### INJECT "hllv progression Spotter" END
        )

    @class_cached_property
    @classmethod
    def SPECIALIST(cls) -> "HLLVRole":
        return cls(
            id=5,
            name="Specialist",
            pretty_name="Specialist",
            type=RoleType.INFANTRY,
            is_squad_leader=False,
            kill_combat_score=6,
            assist_combat_score=4,
            ### INJECT "hllv progression Specialist" START
            progression=[
                HLLVRoleProgression(
                    level=1,
                    max_weight=6,
                    secondary_slot_unlocked=False,
                    extra_ammo_unlocked=False,
                    lethal_slots=0,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=2,
                    max_weight=7,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=False,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=3,
                    max_weight=8,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=4,
                    max_weight=9,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=5,
                    max_weight=10,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=3,
                ),
                HLLVRoleProgression(
                    level=6,
                    max_weight=11,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=3,
                ),
                HLLVRoleProgression(
                    level=7,
                    max_weight=12,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=4,
                ),
                HLLVRoleProgression(
                    level=8,
                    max_weight=13,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=4,
                ),
                HLLVRoleProgression(
                    level=9,
                    max_weight=14,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=4,
                ),
                HLLVRoleProgression(
                    level=10,
                    max_weight=15,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=4,
                ),
            ],
            ### INJECT "hllv progression Specialist" END
        )

    @class_cached_property
    @classmethod
    def MACHINE_GUNNER(cls) -> "HLLVRole":
        return cls(
            id=6,
            name="HeavyMachineGunner",
            pretty_name="Machine Gunner",
            type=RoleType.INFANTRY,
            is_squad_leader=False,
            kill_combat_score=9,
            assist_combat_score=6,
            ### INJECT "hllv progression HeavyMachineGunner" START
            progression=[
                HLLVRoleProgression(
                    level=1,
                    max_weight=6,
                    secondary_slot_unlocked=False,
                    extra_ammo_unlocked=False,
                    lethal_slots=1,
                    utility_slots=0,
                ),
                HLLVRoleProgression(
                    level=2,
                    max_weight=7,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=False,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=3,
                    max_weight=8,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=4,
                    max_weight=9,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=5,
                    max_weight=10,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=3,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=6,
                    max_weight=11,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=3,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=7,
                    max_weight=12,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=4,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=8,
                    max_weight=13,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=4,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=9,
                    max_weight=14,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=4,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=10,
                    max_weight=15,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=4,
                    utility_slots=2,
                ),
            ],
            ### INJECT "hllv progression HeavyMachineGunner" END
        )

    @class_cached_property
    @classmethod
    def GRENADIER(cls) -> "HLLVRole":
        return cls(
            id=7,
            name="Grenadier",
            pretty_name="Grenadier",
            type=RoleType.INFANTRY,
            is_squad_leader=False,
            kill_combat_score=9,
            assist_combat_score=6,
            ### INJECT "hllv progression Grenadier" START
            progression=[
                HLLVRoleProgression(
                    level=1,
                    max_weight=6,
                    secondary_slot_unlocked=False,
                    extra_ammo_unlocked=False,
                    lethal_slots=1,
                    utility_slots=0,
                ),
                HLLVRoleProgression(
                    level=2,
                    max_weight=7,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=False,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=3,
                    max_weight=8,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=4,
                    max_weight=9,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=5,
                    max_weight=10,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=3,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=6,
                    max_weight=11,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=3,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=7,
                    max_weight=12,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=4,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=8,
                    max_weight=13,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=4,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=9,
                    max_weight=14,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=4,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=10,
                    max_weight=15,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=4,
                    utility_slots=2,
                ),
            ],
            ### INJECT "hllv progression Grenadier" END
        )

    @class_cached_property
    @classmethod
    def ENGINEER(cls) -> "HLLVRole":
        return cls(
            id=8,
            name="Engineer",
            pretty_name="Engineer",
            type=RoleType.INFANTRY,
            is_squad_leader=False,
            kill_combat_score=9,
            assist_combat_score=6,
            ### INJECT "hllv progression Engineer" START
            progression=[
                HLLVRoleProgression(
                    level=1,
                    max_weight=6,
                    secondary_slot_unlocked=False,
                    extra_ammo_unlocked=False,
                    lethal_slots=1,
                    utility_slots=0,
                ),
                HLLVRoleProgression(
                    level=2,
                    max_weight=7,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=False,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=3,
                    max_weight=8,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=4,
                    max_weight=9,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=5,
                    max_weight=10,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=3,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=6,
                    max_weight=11,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=3,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=7,
                    max_weight=12,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=4,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=8,
                    max_weight=13,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=4,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=9,
                    max_weight=14,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=4,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=10,
                    max_weight=15,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=4,
                    utility_slots=2,
                ),
            ],
            ### INJECT "hllv progression Engineer" END
        )

    @class_cached_property
    @classmethod
    def SQUAD_LEADER(cls) -> "HLLVRole":
        return cls(
            id=9,
            name="SquadLeader",
            pretty_name="Squad Leader",
            type=RoleType.INFANTRY,
            is_squad_leader=True,
            kill_combat_score=9,
            assist_combat_score=6,
            ### INJECT "hllv progression SquadLeader" START
            progression=[
                HLLVRoleProgression(
                    level=1,
                    max_weight=6,
                    secondary_slot_unlocked=False,
                    extra_ammo_unlocked=False,
                    lethal_slots=0,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=2,
                    max_weight=7,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=False,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=3,
                    max_weight=8,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=4,
                    max_weight=9,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=5,
                    max_weight=10,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=3,
                ),
                HLLVRoleProgression(
                    level=6,
                    max_weight=11,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=3,
                ),
                HLLVRoleProgression(
                    level=7,
                    max_weight=12,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=4,
                ),
                HLLVRoleProgression(
                    level=8,
                    max_weight=13,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=4,
                ),
                HLLVRoleProgression(
                    level=9,
                    max_weight=14,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=4,
                ),
                HLLVRoleProgression(
                    level=10,
                    max_weight=15,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=4,
                ),
            ],
            ### INJECT "hllv progression SquadLeader" END
        )

    @class_cached_property
    @classmethod
    def SNIPER(cls) -> "HLLVRole":
        return cls(
            id=10,
            name="Sniper",
            pretty_name="Sniper",
            type=RoleType.RECON,
            is_squad_leader=False,
            kill_combat_score=6,
            assist_combat_score=4,
            ### INJECT "hllv progression Sniper" START
            progression=[
                HLLVRoleProgression(
                    level=1,
                    max_weight=6,
                    secondary_slot_unlocked=False,
                    extra_ammo_unlocked=False,
                    lethal_slots=1,
                    utility_slots=0,
                ),
                HLLVRoleProgression(
                    level=2,
                    max_weight=7,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=False,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=3,
                    max_weight=8,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=4,
                    max_weight=9,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=5,
                    max_weight=10,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=3,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=6,
                    max_weight=11,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=3,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=7,
                    max_weight=12,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=4,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=8,
                    max_weight=13,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=4,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=9,
                    max_weight=14,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=4,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=10,
                    max_weight=15,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=4,
                    utility_slots=2,
                ),
            ],
            ### INJECT "hllv progression Sniper" END
        )

    @class_cached_property
    @classmethod
    def CREWMAN(cls) -> "HLLVRole":
        return cls(
            id=11,
            name="Crewman",
            pretty_name="Crewman",
            type=RoleType.ARMOR,
            is_squad_leader=False,
            kill_combat_score=3,
            assist_combat_score=2,
            ### INJECT "hllv progression Crewman" START
            progression=[
                HLLVRoleProgression(
                    level=1,
                    max_weight=6,
                    secondary_slot_unlocked=False,
                    extra_ammo_unlocked=False,
                    lethal_slots=0,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=2,
                    max_weight=7,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=False,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=3,
                    max_weight=8,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=4,
                    max_weight=9,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=5,
                    max_weight=10,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=6,
                    max_weight=11,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=7,
                    max_weight=12,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=8,
                    max_weight=13,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=9,
                    max_weight=14,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=10,
                    max_weight=15,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=2,
                ),
            ],
            ### INJECT "hllv progression Crewman" END
        )

    @class_cached_property
    @classmethod
    def TANK_COMMANDER(cls) -> "HLLVRole":
        return cls(
            id=12,
            name="TankCommander",
            pretty_name="Tank Commander",
            type=RoleType.ARMOR,
            is_squad_leader=True,
            kill_combat_score=9,
            assist_combat_score=6,
            ### INJECT "hllv progression TankCommander" START
            progression=[
                HLLVRoleProgression(
                    level=1,
                    max_weight=6,
                    secondary_slot_unlocked=False,
                    extra_ammo_unlocked=False,
                    lethal_slots=0,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=2,
                    max_weight=7,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=False,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=3,
                    max_weight=8,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=4,
                    max_weight=9,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=5,
                    max_weight=10,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=6,
                    max_weight=11,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=7,
                    max_weight=12,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=8,
                    max_weight=13,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=9,
                    max_weight=14,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=10,
                    max_weight=15,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=2,
                ),
            ],
            ### INJECT "hllv progression TankCommander" END
        )

    @class_cached_property
    @classmethod
    def SUPPORT(cls) -> "HLLVRole":
        return cls(
            id=13,
            name="MortarSupport",
            pretty_name="Support",
            type=RoleType.MORTAR,
            is_squad_leader=False,
            kill_combat_score=12,  # TODO: Update
            assist_combat_score=8,
            ### INJECT "hllv progression MortarSupport" START
            progression=[
                HLLVRoleProgression(
                    level=1,
                    max_weight=6,
                    secondary_slot_unlocked=False,
                    extra_ammo_unlocked=False,
                    lethal_slots=0,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=2,
                    max_weight=7,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=False,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=3,
                    max_weight=8,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=4,
                    max_weight=9,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=5,
                    max_weight=10,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=3,
                ),
                HLLVRoleProgression(
                    level=6,
                    max_weight=11,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=3,
                ),
                HLLVRoleProgression(
                    level=7,
                    max_weight=12,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=4,
                ),
                HLLVRoleProgression(
                    level=8,
                    max_weight=13,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=4,
                ),
                HLLVRoleProgression(
                    level=9,
                    max_weight=14,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=4,
                ),
                HLLVRoleProgression(
                    level=10,
                    max_weight=15,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=4,
                ),
            ],
            ### INJECT "hllv progression MortarSupport" END
        )

    @class_cached_property
    @classmethod
    def OBSERVER(cls) -> "HLLVRole":
        return cls(
            id=14,
            name="MortarObserver",
            pretty_name="Observer",
            type=RoleType.MORTAR,
            is_squad_leader=True,
            kill_combat_score=9,
            assist_combat_score=6,
            ### INJECT "hllv progression MortarObserver" START
            progression=[
                HLLVRoleProgression(
                    level=1,
                    max_weight=6,
                    secondary_slot_unlocked=False,
                    extra_ammo_unlocked=False,
                    lethal_slots=1,
                    utility_slots=0,
                ),
                HLLVRoleProgression(
                    level=2,
                    max_weight=7,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=False,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=3,
                    max_weight=8,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=4,
                    max_weight=9,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=5,
                    max_weight=10,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=3,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=6,
                    max_weight=11,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=3,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=7,
                    max_weight=12,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=4,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=8,
                    max_weight=13,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=4,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=9,
                    max_weight=14,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=4,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=10,
                    max_weight=15,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=4,
                    utility_slots=2,
                ),
            ],
            ### INJECT "hllv progression MortarObserver" END
        )

    @class_cached_property
    @classmethod
    def GUNNER(cls) -> "HLLVRole":
        return cls(
            id=15,
            name="MortarGunner",
            pretty_name="Gunner",
            type=RoleType.MORTAR,
            is_squad_leader=False,
            kill_combat_score=9,
            assist_combat_score=6,
            ### INJECT "hllv progression MortarGunner" START
            progression=[
                HLLVRoleProgression(
                    level=1,
                    max_weight=6,
                    secondary_slot_unlocked=False,
                    extra_ammo_unlocked=False,
                    lethal_slots=0,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=2,
                    max_weight=7,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=False,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=3,
                    max_weight=8,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=4,
                    max_weight=9,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=5,
                    max_weight=10,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=3,
                ),
                HLLVRoleProgression(
                    level=6,
                    max_weight=11,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=3,
                ),
                HLLVRoleProgression(
                    level=7,
                    max_weight=12,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=4,
                ),
                HLLVRoleProgression(
                    level=8,
                    max_weight=13,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=4,
                ),
                HLLVRoleProgression(
                    level=9,
                    max_weight=14,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=4,
                ),
                HLLVRoleProgression(
                    level=10,
                    max_weight=15,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=4,
                ),
            ],
            ### INJECT "hllv progression MortarGunner" END
        )

    @class_cached_property
    @classmethod
    def PILOT(cls) -> "HLLVRole":
        return cls(
            id=16,
            name="HelicopterPilot",
            pretty_name="Pilot",
            type=RoleType.HELICOPTER,
            is_squad_leader=False,
            kill_combat_score=6,
            assist_combat_score=4,
            ### INJECT "hllv progression HelicopterPilot" START
            progression=[
                HLLVRoleProgression(
                    level=1,
                    max_weight=6,
                    secondary_slot_unlocked=False,
                    extra_ammo_unlocked=False,
                    lethal_slots=0,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=2,
                    max_weight=7,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=False,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=3,
                    max_weight=8,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=4,
                    max_weight=9,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=5,
                    max_weight=10,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=6,
                    max_weight=11,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=7,
                    max_weight=12,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=8,
                    max_weight=13,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=9,
                    max_weight=14,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=10,
                    max_weight=15,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=2,
                ),
            ],
            ### INJECT "hllv progression HelicopterPilot" END
        )

    @class_cached_property
    @classmethod
    def LOGISTICS_OFFICER(cls) -> "HLLVRole":
        return cls(
            id=17,
            name="HelicopterLogisticsOfficer",
            pretty_name="Logistics Officer",
            type=RoleType.HELICOPTER,
            is_squad_leader=True,
            kill_combat_score=9,
            assist_combat_score=6,
            ### INJECT "hllv progression HelicopterLogisticsOfficer" START
            progression=[
                HLLVRoleProgression(
                    level=1,
                    max_weight=6,
                    secondary_slot_unlocked=False,
                    extra_ammo_unlocked=False,
                    lethal_slots=0,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=2,
                    max_weight=7,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=False,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=3,
                    max_weight=8,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=4,
                    max_weight=9,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=5,
                    max_weight=10,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=6,
                    max_weight=11,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=7,
                    max_weight=12,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=8,
                    max_weight=13,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=9,
                    max_weight=14,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=10,
                    max_weight=15,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=2,
                ),
            ],
            ### INJECT "hllv progression HelicopterLogisticsOfficer" END
        )

    @class_cached_property
    @classmethod
    def COMMANDER(cls) -> "HLLVRole":
        return cls(
            id=20,
            name="ArmyCommander",
            pretty_name="Commander",
            type=RoleType.COMMANDER,
            is_squad_leader=True,
            kill_combat_score=12,
            assist_combat_score=8,
            ### INJECT "hllv progression ArmyCommander" START
            progression=[
                HLLVRoleProgression(
                    level=1,
                    max_weight=6,
                    secondary_slot_unlocked=False,
                    extra_ammo_unlocked=False,
                    lethal_slots=0,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=2,
                    max_weight=7,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=False,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=3,
                    max_weight=8,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=4,
                    max_weight=9,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=1,
                ),
                HLLVRoleProgression(
                    level=5,
                    max_weight=10,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=6,
                    max_weight=11,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=1,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=7,
                    max_weight=12,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=8,
                    max_weight=13,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=9,
                    max_weight=14,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=2,
                ),
                HLLVRoleProgression(
                    level=10,
                    max_weight=15,
                    secondary_slot_unlocked=True,
                    extra_ammo_unlocked=True,
                    lethal_slots=2,
                    utility_slots=2,
                ),
            ],
            ### INJECT "hllv progression ArmyCommander" END
        )

    @class_cached_property
    @classmethod
    def ARMY_COMMANDER(cls) -> "HLLVRole":
        return cls.COMMANDER


AnyRole: TypeAlias = HLLRole | HLLVRole
