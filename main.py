"""
Main entry point for the Pet Clinic Management System (Lab 4).
Pre-loads comprehensive sample clinical data and launches the PetClinicApp GUI.
Recycles structure and architectural conventions from Lab3 Food Delivery System.
"""
from typing import Optional

from models import (
    Owner,
    PetFactory,
    Appointment,
    AppointmentStatus,
    ClinicDatabase,
)
from app import PetClinicApp


def initialize_sample_data(database: Optional[ClinicDatabase] = None) -> ClinicDatabase:
    """
    Initialize and populate the ClinicDatabase singleton with comprehensive sample records:
      - 3+ registered Owners
      - 5 registered Pets covering all 4 supported types (Dog, Cat, Bird, Rabbit) via PetFactory
      - 3 scheduled appointments with varying statuses (Scheduled, Completed, Cancelled)

    Args:
        database: Optional ClinicDatabase instance. Defaults to the singleton.

    Returns:
        ClinicDatabase: The populated singleton database instance.
    """
    db = database if database is not None else ClinicDatabase()
    # Reset database state in case of prior invocations for test idempotency
    db.clear_all()

    # -------------------------------------------------------------------------
    # 1. Register Sample Owners (3 owners)
    # -------------------------------------------------------------------------
    owner1 = Owner(
        owner_id="OWN-001",
        name="Alice Johnson",
        contact_number="555-0142",
    )
    owner2 = Owner(
        owner_id="OWN-002",
        name="Bob Smith",
        contact_number="555-0288",
    )
    owner3 = Owner(
        owner_id="OWN-003",
        name="Carol Davis",
        contact_number="555-0377",
    )

    db.add_owner(owner1)
    db.add_owner(owner2)
    db.add_owner(owner3)

    # -------------------------------------------------------------------------
    # 2. Register Sample Pets covering all 4 supported types (Dog, Cat, Bird, Rabbit)
    #    Created strictly using PetFactory.create_pet(...)
    # -------------------------------------------------------------------------
    # Pet 1: Dog (owned by Alice Johnson)
    pet1 = PetFactory.create_pet(
        pet_id="PET-001",
        name="Buddy",
        pet_type="Dog",
        breed="Golden Retriever",
        age=3,
        weight=28.5,
        owner_id=owner1.owner_id,
    )
    # Pet 2: Cat (owned by Bob Smith)
    pet2 = PetFactory.create_pet(
        pet_id="PET-002",
        name="Luna",
        pet_type="Cat",
        breed="Siamese",
        age=2,
        weight=4.2,
        owner_id=owner2.owner_id,
    )
    # Pet 3: Bird (owned by Carol Davis)
    pet3 = PetFactory.create_pet(
        pet_id="PET-003",
        name="Pip",
        pet_type="Bird",
        breed="Cockatiel",
        age=1,
        weight=0.1,
        owner_id=owner3.owner_id,
    )
    # Pet 4: Rabbit (owned by Alice Johnson)
    pet4 = PetFactory.create_pet(
        pet_id="PET-004",
        name="Thumper",
        pet_type="Rabbit",
        breed="Holland Lop",
        age=2,
        weight=1.8,
        owner_id=owner1.owner_id,
    )
    # Pet 5: Dog (owned by Bob Smith) - multi-pet ownership
    pet5 = PetFactory.create_pet(
        pet_id="PET-005",
        name="Bella",
        pet_type="Dog",
        breed="Beagle",
        age=4,
        weight=11.2,
        owner_id=owner2.owner_id,
    )

    db.add_pet(pet1)
    db.add_pet(pet2)
    db.add_pet(pet3)
    db.add_pet(pet4)
    db.add_pet(pet5)

    # -------------------------------------------------------------------------
    # 3. Register Sample Appointments (3 appointments with varying statuses)
    # -------------------------------------------------------------------------
    apt1 = Appointment(
        appointment_id="APT-001",
        pet=pet1,
        owner=owner1,
        date="2026-09-15",
        time="10:00 AM",
        reason="Annual Wellness Checkup & Rabies Vaccination",
        status=AppointmentStatus.SCHEDULED,
    )
    apt2 = Appointment(
        appointment_id="APT-002",
        pet=pet2,
        owner=owner2,
        date="2026-09-10",
        time="02:30 PM",
        reason="Dental Cleaning & Tartar Examination",
        status=AppointmentStatus.COMPLETED,
    )
    apt3 = Appointment(
        appointment_id="APT-003",
        pet=pet4,
        owner=owner1,
        date="2026-09-18",
        time="11:15 AM",
        reason="Routine Nail Trim and Digestive Assessment",
        status=AppointmentStatus.CANCELLED,
    )

    db.schedule_appointment(apt1)
    db.schedule_appointment(apt2)
    db.schedule_appointment(apt3)

    return db


def main() -> None:
    """Entry point: initialize sample records and launch Tkinter GUI."""
    db = initialize_sample_data()
    app = PetClinicApp(db)
    app.mainloop()


if __name__ == "__main__":
    main()
