"""
Appointment model and status enumeration for scheduling clinic visits.
Follows Lab3 encapsulation and validation patterns.
"""
from enum import Enum
from typing import Union

from .owner import Owner
from .pet import Pet


class AppointmentStatus(Enum):
    """Enumeration of possible appointment lifecycle states."""
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class Appointment:
    """
    Represents a scheduled clinic appointment linking a Pet and an Owner.

    Attributes:
        _appointment_id (str): Unique appointment identifier (e.g., 'APT-001').
        _pet (Pet): The Pet instance undergoing examination.
        _owner (Owner): The Owner instance responsible for the pet.
        _date (str): Scheduled date (e.g., '2026-09-15').
        _time (str): Scheduled time (e.g., '10:00 AM').
        _reason (str): Reason for the visit / clinical complaint.
        _status (AppointmentStatus): Current status of the appointment.
    """

    def __init__(
        self,
        appointment_id: str,
        pet: Pet,
        owner: Owner,
        date: str,
        time: str,
        reason: str,
        status: Union[AppointmentStatus, str] = AppointmentStatus.SCHEDULED,
    ) -> None:
        """
        Initialize an Appointment instance.

        Args:
            appointment_id: Unique identifier for the appointment.
            pet: Pet object for the appointment.
            owner: Owner object associated with the pet.
            date: Scheduled date string.
            time: Scheduled time string.
            reason: Clinical reason or description of appointment.
            status: AppointmentStatus enum or string value (default: SCHEDULED).

        Raises:
            TypeError: If pet or owner are not the correct types.
            ValueError: If pet does not belong to owner or if string validation fails.
        """
        if not isinstance(appointment_id, str):
            raise TypeError("Appointment ID must be a string")
        if not appointment_id.strip():
            raise ValueError("Appointment ID cannot be empty")
        self._appointment_id = appointment_id.strip()

        if not isinstance(pet, Pet):
            raise TypeError("Expected Pet instance")
        if not isinstance(owner, Owner):
            raise TypeError("Expected Owner instance")

        # Referential cross-check: pet must belong to owner
        if pet.owner_id != owner.owner_id:
            raise ValueError(
                f"Pet '{pet.name}' (Owner ID: {pet.owner_id}) does not belong to owner '{owner.name}' ({owner.owner_id})"
            )

        self._pet = pet
        self._owner = owner

        # Route assignments through property setters for validation
        self.date = date
        self.time = time
        self.reason = reason
        self.status = status

    @property
    def appointment_id(self) -> str:
        """Return the unique appointment ID (read-only)."""
        return self._appointment_id

    @property
    def pet(self) -> Pet:
        """Return the linked Pet instance."""
        return self._pet

    @pet.setter
    def pet(self, value: Pet) -> None:
        """
        Update the linked Pet instance.

        Raises:
            TypeError: If value is not a Pet instance.
            ValueError: If new pet does not belong to current owner.
        """
        if not isinstance(value, Pet):
            raise TypeError("Expected Pet instance")
        if value.owner_id != self._owner.owner_id:
            raise ValueError("New pet does not belong to the current appointment owner")
        self._pet = value

    @property
    def pet_id(self) -> str:
        """Convenience property returning the linked pet's ID."""
        return self._pet.pet_id

    @property
    def owner(self) -> Owner:
        """Return the linked Owner instance."""
        return self._owner

    @owner.setter
    def owner(self, value: Owner) -> None:
        """
        Update the linked Owner instance.

        Raises:
            TypeError: If value is not an Owner instance.
            ValueError: If new owner does not match the appointment pet's owner ID.
        """
        if not isinstance(value, Owner):
            raise TypeError("Expected Owner instance")
        if self._pet.owner_id != value.owner_id:
            raise ValueError("New owner does not match the appointment pet's owner ID")
        self._owner = value

    @property
    def owner_id(self) -> str:
        """Convenience property returning the linked owner's ID."""
        return self._owner.owner_id

    @property
    def date(self) -> str:
        """Return the scheduled appointment date."""
        return self._date

    @date.setter
    def date(self, value: str) -> None:
        """
        Set the scheduled appointment date.

        Raises:
            TypeError: If value is not a string.
            ValueError: If value is empty or consists solely of whitespace.
        """
        if not isinstance(value, str):
            raise TypeError("Date must be a string")
        if not value.strip():
            raise ValueError("Date cannot be empty")
        self._date = value.strip()

    @property
    def time(self) -> str:
        """Return the scheduled appointment time."""
        return self._time

    @time.setter
    def time(self, value: str) -> None:
        """
        Set the scheduled appointment time.

        Raises:
            TypeError: If value is not a string.
            ValueError: If value is empty or consists solely of whitespace.
        """
        if not isinstance(value, str):
            raise TypeError("Time must be a string")
        if not value.strip():
            raise ValueError("Time cannot be empty")
        self._time = value.strip()

    @property
    def reason(self) -> str:
        """Return the reason for the appointment."""
        return self._reason

    @reason.setter
    def reason(self, value: str) -> None:
        """
        Set the reason for the appointment.

        Raises:
            TypeError: If value is not a string.
            ValueError: If value is empty or consists solely of whitespace.
        """
        if not isinstance(value, str):
            raise TypeError("Reason must be a string")
        if not value.strip():
            raise ValueError("Reason cannot be empty")
        self._reason = value.strip()

    @property
    def status(self) -> AppointmentStatus:
        """Return the current AppointmentStatus enum member."""
        return self._status

    @status.setter
    def status(self, value: Union[AppointmentStatus, str]) -> None:
        """
        Set the appointment status.

        Args:
            value: An AppointmentStatus enum member or corresponding string.

        Raises:
            TypeError: If value is neither an AppointmentStatus nor a string.
            ValueError: If string value does not match any AppointmentStatus member,
                        or if forbidden transition is attempted.
        """
        if isinstance(value, AppointmentStatus):
            new_status = value
        elif isinstance(value, str):
            cleaned = value.strip()
            matched = False
            for member in AppointmentStatus:
                if (
                    member.value.lower() == cleaned.lower()
                    or member.name.lower() == cleaned.lower()
                ):
                    new_status = member
                    matched = True
                    break
            if not matched:
                raise ValueError(
                    f"Invalid status '{value}'. Valid statuses: {[m.value for m in AppointmentStatus]}"
                )
        else:
            raise TypeError(
                "Status must be an AppointmentStatus enum member or valid status string"
            )

        self._status = new_status

    def cancel(self) -> None:
        """
        Transition the appointment status to CANCELLED.

        Raises:
            ValueError: If appointment is already completed.
        """
        if self._status == AppointmentStatus.COMPLETED:
            raise ValueError("Cannot cancel an appointment that has already been completed")
        self._status = AppointmentStatus.CANCELLED

    def complete(self) -> None:
        """
        Transition the appointment status to COMPLETED.

        Raises:
            ValueError: If appointment has been cancelled.
        """
        if self._status == AppointmentStatus.CANCELLED:
            raise ValueError("Cannot complete an appointment that has been cancelled")
        self._status = AppointmentStatus.COMPLETED

    def mark_completed(self) -> None:
        """Administratively set status to COMPLETED."""
        self._status = AppointmentStatus.COMPLETED

    def get_info(self) -> str:
        """Return formatted detailed single-line string representation."""
        return (
            f"[{self._appointment_id}] {self._date} {self._time} | "
            f"Pet: {self._pet.name} ({self._pet.pet_type}) | Owner: {self._owner.name} | "
            f"Status: {self._status.value} | Reason: {self._reason}"
        )

    def get_summary(self) -> str:
        """Return a structured multi-line clinical summary."""
        lines = [
            f"Appointment ID: {self._appointment_id}",
            f"Date & Time:    {self._date} at {self._time}",
            f"Status:         {self._status.value}",
            f"Owner:          {self._owner.name} (Contact: {self._owner.contact_number})",
            f"Pet:            {self._pet.name} ({self._pet.pet_type}, {self._pet.breed}, {self._pet.age} yrs, {self._pet.weight:.1f} kg)",
            f"Reason:         {self._reason}",
        ]
        return "\n".join(lines)

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return (
            f"Appointment #{self._appointment_id} - {self._pet.name} with {self._owner.name} "
            f"on {self._date} at {self._time} ({self._status.value})"
        )

    def __repr__(self) -> str:
        """Return developer-friendly debug representation."""
        return (
            f"Appointment(appointment_id='{self._appointment_id}', pet_id='{self._pet.pet_id}', "
            f"owner_id='{self._owner.owner_id}', date='{self._date}', time='{self._time}', "
            f"status='{self._status.value}')"
        )
