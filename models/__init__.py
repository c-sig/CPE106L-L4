"""
Models package for the Pet Clinic Management System.
Exports core domain entities, enumerations, database singleton, and factories.
"""
from .appointment import Appointment, AppointmentStatus
from .database import ClinicDatabase
from .factory import PetFactory
from .owner import Owner
from .pet import Pet, SUPPORTED_PET_TYPES

__all__ = [
    "Owner",
    "Pet",
    "Appointment",
    "AppointmentStatus",
    "ClinicDatabase",
    "PetFactory",
]
