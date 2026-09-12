"""
ClinicDatabase singleton managing all owners, pets, and appointments.
Follows Lab3 architectural patterns for in-memory data store with test isolation.
"""
from typing import Dict, List, Optional, Union

from .appointment import Appointment, AppointmentStatus
from .owner import Owner
from .pet import Pet


class ClinicDatabase:
    """
    Singleton database managing owners, pets, and appointments in memory.

    Guarantees that only a single instance exists across the application.
    """

    _instance: Optional["ClinicDatabase"] = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs) -> "ClinicDatabase":
        """Control instance creation to enforce the Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(ClinicDatabase, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize database storage only once upon first instantiation."""
        if not self._initialized:
            self._owners: Dict[str, Owner] = {}
            self._pets: Dict[str, Pet] = {}
            self._appointments: Dict[str, Appointment] = {}
            self._initialized = True

    # -------------------------------------------------------------------------
    # Owner Operations
    # -------------------------------------------------------------------------
    def add_owner(self, owner: Owner) -> None:
        """
        Add a new Owner to the database.

        Raises:
            TypeError: If owner is not an Owner instance.
            ValueError: If an owner with the same ID already exists.
        """
        if not isinstance(owner, Owner):
            raise TypeError("Expected Owner instance")
        if owner.owner_id in self._owners:
            raise ValueError(f"Owner with ID '{owner.owner_id}' already exists")
        self._owners[owner.owner_id] = owner

    def get_owner(self, owner_id: str) -> Optional[Owner]:
        """Retrieve an owner by ID, or None if not found."""
        return self._owners.get(owner_id)

    def get_all_owners(self) -> List[Owner]:
        """Return a defensive copy list of all registered owners."""
        return list(self._owners.values())

    def remove_owner(self, owner_id: str) -> bool:
        """
        Remove an owner by ID.

        Returns:
            bool: True if removed, False if not found.
        """
        if owner_id in self._owners:
            del self._owners[owner_id]
            return True
        return False

    # -------------------------------------------------------------------------
    # Pet Operations
    # -------------------------------------------------------------------------
    def add_pet(self, pet: Pet) -> None:
        """
        Add a new Pet to the database.

        Raises:
            TypeError: If pet is not a Pet instance.
            ValueError: If pet ID already exists or associated owner is not registered.
        """
        if not isinstance(pet, Pet):
            raise TypeError("Expected Pet instance")
        if pet.pet_id in self._pets:
            raise ValueError(f"Pet with ID '{pet.pet_id}' already exists")
        if pet.owner_id not in self._owners:
            raise ValueError(
                f"Cannot add pet: Owner with ID '{pet.owner_id}' does not exist"
            )
        self._pets[pet.pet_id] = pet

    def get_pet(self, pet_id: str) -> Optional[Pet]:
        """Retrieve a pet by ID, or None if not found."""
        return self._pets.get(pet_id)

    def get_pets_by_owner(self, owner_id: str) -> List[Pet]:
        """Retrieve all pets belonging to a specific owner."""
        return [pet for pet in self._pets.values() if pet.owner_id == owner_id]

    def get_all_pets(self) -> List[Pet]:
        """Return a defensive copy list of all registered pets."""
        return list(self._pets.values())

    def remove_pet(self, pet_id: str) -> bool:
        """
        Remove a pet by ID.

        Returns:
            bool: True if removed, False if not found.
        """
        if pet_id in self._pets:
            del self._pets[pet_id]
            return True
        return False

    # -------------------------------------------------------------------------
    # Appointment Operations
    # -------------------------------------------------------------------------
    def schedule_appointment(self, appointment: Appointment) -> None:
        """
        Schedule and register a new Appointment in the database.

        Raises:
            TypeError: If appointment is not an Appointment instance.
            ValueError: If appointment ID already exists or referenced pet/owner is missing.
        """
        if not isinstance(appointment, Appointment):
            raise TypeError("Expected Appointment instance")
        if appointment.appointment_id in self._appointments:
            raise ValueError(
                f"Appointment with ID '{appointment.appointment_id}' already exists"
            )
        if appointment.pet.pet_id not in self._pets:
            raise ValueError(
                f"Cannot schedule: Pet '{appointment.pet.pet_id}' is not in the database"
            )
        if appointment.owner.owner_id not in self._owners:
            raise ValueError(
                f"Cannot schedule: Owner '{appointment.owner.owner_id}' is not in the database"
            )
        self._appointments[appointment.appointment_id] = appointment

    # Alias for schedule_appointment
    add_appointment = schedule_appointment

    def get_appointment(self, appointment_id: str) -> Optional[Appointment]:
        """Retrieve an appointment by ID, or None if not found."""
        return self._appointments.get(appointment_id)

    def get_appointments_by_pet(self, pet_id: str) -> List[Appointment]:
        """Retrieve all appointments scheduled for a specific pet."""
        return [
            apt for apt in self._appointments.values() if apt.pet.pet_id == pet_id
        ]

    def get_appointments_by_owner(self, owner_id: str) -> List[Appointment]:
        """Retrieve all appointments scheduled for a specific owner."""
        return [
            apt for apt in self._appointments.values() if apt.owner.owner_id == owner_id
        ]

    def get_all_appointments(self) -> List[Appointment]:
        """Return a defensive copy list of all scheduled appointments."""
        return list(self._appointments.values())

    def cancel_appointment(self, appointment_id: str) -> bool:
        """
        Cancel an appointment by transitioning its status to CANCELLED.

        Returns:
            bool: True if appointment was found and cancelled, False otherwise.
        """
        apt = self._appointments.get(appointment_id)
        if apt is None:
            return False
        apt.cancel()
        return True

    def complete_appointment(self, appointment_id: str) -> bool:
        """
        Mark an appointment as COMPLETED.

        Returns:
            bool: True if appointment was found and completed, False otherwise.
        """
        apt = self._appointments.get(appointment_id)
        if apt is None:
            return False
        apt.complete()
        return True

    def update_appointment_status(
        self, appointment_id: str, status: Union[AppointmentStatus, str]
    ) -> bool:
        """
        Update the status of an appointment.

        Returns:
            bool: True if updated, False if appointment not found.
        """
        apt = self._appointments.get(appointment_id)
        if apt is None:
            return False
        apt.status = status
        return True

    def remove_appointment(self, appointment_id: str) -> bool:
        """
        Remove an appointment record completely.

        Returns:
            bool: True if removed, False if not found.
        """
        if appointment_id in self._appointments:
            del self._appointments[appointment_id]
            return True
        return False

    # -------------------------------------------------------------------------
    # Maintenance & Analytics
    # -------------------------------------------------------------------------
    def clear_all(self) -> None:
        """
        Clear all records from the database.

        Used to reset database state between test runs while preserving the singleton identity.
        """
        self._owners.clear()
        self._pets.clear()
        self._appointments.clear()

    def clear(self) -> None:
        """Alias for clear_all()."""
        self.clear_all()

    def get_statistics(self) -> dict:
        """
        Compute and return clinic summary statistics.

        Returns:
            dict containing:
                - total_owners (int)
                - total_pets (int)
                - pets_by_type (dict[str, int])
                - total_appointments (int)
                - appointments_by_status (dict[str, int])
        """
        pets_by_type: Dict[str, int] = {}
        for pet in self._pets.values():
            pets_by_type[pet.pet_type] = pets_by_type.get(pet.pet_type, 0) + 1

        appointments_by_status: Dict[str, int] = {}
        for apt in self._appointments.values():
            status_label = apt.status.value
            appointments_by_status[status_label] = (
                appointments_by_status.get(status_label, 0) + 1
            )

        return {
            "total_owners": len(self._owners),
            "total_pets": len(self._pets),
            "pets_by_type": pets_by_type,
            "total_appointments": len(self._appointments),
            "appointments_by_status": appointments_by_status,
        }
