from enum import StrEnum

from hllrcon.data.roles import HLLRole, HLLVRole


class EPlayerRole(StrEnum):
    RIFLEMAN = "EPlayerRole::Rifleman"
    ASSAULT = "EPlayerRole::Assault"
    AUTOMATIC_RIFLEMAN = "EPlayerRole::AutomaticRifleman"
    MEDIC = "EPlayerRole::Medic"
    SPOTTER = "EPlayerRole::Spotter"
    SPECIALIST = "EPlayerRole::Specialist"
    MACHINE_GUNNER = "EPlayerRole::HeavyMachineGunner"
    ANTI_TANK = "EPlayerRole::AntiTank"
    GRENADIER = "EPlayerRole::Grenadier"
    ENGINEER = "EPlayerRole::Engineer"
    SQUAD_LEADER = "EPlayerRole::SquadLeader"
    SNIPER = "EPlayerRole::Sniper"
    CREWMAN = "EPlayerRole::Crewman"
    TANK_COMMANDER = "EPlayerRole::TankCommander"
    SUPPORT = "EPlayerRole::MortarSupport"
    OBSERVER = "EPlayerRole::MortarObserver"
    GUNNER = "EPlayerRole::MortarGunner"
    PILOT = "EPlayerRole::HelicopterPilot"
    LOGISTICS_OFFICER = "EPlayerRole::HelicopterLogisticsOfficer"
    FLIGHT_ENGINEER = "EPlayerRole::HelicopterFlightEngineer"
    HELI_MEDIC = "EPlayerRole::HelicopterMedic"
    COMMANDER = "EPlayerRole::ArmyCommander"

    def get_role_name(self) -> str:
        return self.value.split("::")[1]

    def to_hll_role(self) -> "HLLRole":
        for role in HLLRole.all():
            if role.name == self.get_role_name():
                return role
        msg = f"No matching HLLRole found for {self}."
        raise ValueError(msg)

    def to_hllv_role(self) -> "HLLVRole":
        for role in HLLVRole.all():
            if role.name == self.get_role_name():
                return role
        msg = f"No matching HLLVRole found for {self}."
        raise ValueError(msg)
