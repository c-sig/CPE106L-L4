"""
Comprehensive Unit Test Suite for Pet Clinic Management System (Lab 4).

Follows unittest.TestCase class-based approach matching CPE106L Lab4 requirements.
Tests all required scenarios:
  1. Register Pet Owner (test_register_owner)
  2. Add Pet Record via PetFactory (test_add_pet_via_factory)
  3. Schedule Appointment (test_schedule_appointment)
  4. Cancel Appointment (test_cancel_appointment)
  5. Validate Singleton Instance (test_singleton_clinic_database)
Along with comprehensive edge cases:
  - Input validation (negative age, zero/negative weight, non-whitelisted species, invalid contact formats)
  - Referential integrity (unregistered owner, pet owner mismatch)
  - Lifecycle state transitions and duplicate prevention
  - Sample data initialization verification
"""
import math
import unittest

from main import initialize_sample_data
from models import (
    Appointment,
    AppointmentStatus,
    ClinicDatabase,
    Owner,
    Pet,
    PetFactory,
    SUPPORTED_PET_TYPES,
)


class TestPetClinicSystem(unittest.TestCase):
    """
    Comprehensive test case suite verifying domain models, factories,
    referential integrity, validation, and singleton database operations.
    """

    def setUp(self) -> None:
        """Ensure clean test isolation by resetting the singleton database state."""
        self.db = ClinicDatabase()
        self.db.clear_all()

    def tearDown(self) -> None:
        """Clean up database state after each test execution."""
        self.db.clear_all()

    # =========================================================================
    # Required Scenario 1: Register Pet Owner
    # =========================================================================
    def test_register_owner(self) -> None:
        """
        Test creating and registering an Owner in ClinicDatabase.
        Verifies:
          - Initial attributes and properties (owner_id, name, contact_number, phone alias)
          - Registration in ClinicDatabase
          - Retrieval by owner_id and get_all_owners()
          - Non-existent ID returns None
          - Validation rules: empty name, invalid contact number, type checks
          - Duplicate owner_id registration prevention
          - Property setters and string representations
        """
        # 1. Create and verify valid Owner
        owner = Owner(
            owner_id="OWN-001",
            name="Alice Johnson",
            contact_number="555-0142",
        )
        self.assertEqual(owner.owner_id, "OWN-001")
        self.assertEqual(owner.name, "Alice Johnson")
        self.assertEqual(owner.contact_number, "555-0142")
        self.assertEqual(owner.phone, "555-0142")

        # 2. Register into ClinicDatabase
        self.db.add_owner(owner)

        # 3. Retrieval by ID
        retrieved = self.db.get_owner("OWN-001")
        self.assertIsNotNone(retrieved)
        self.assertIs(retrieved, owner)
        self.assertEqual(retrieved.owner_id, "OWN-001")
        self.assertEqual(retrieved.name, "Alice Johnson")
        self.assertEqual(retrieved.contact_number, "555-0142")

        # 4. Non-existent owner lookup
        self.assertIsNone(self.db.get_owner("NON-EXISTENT-ID"))

        # 5. List all owners
        all_owners = self.db.get_all_owners()
        self.assertEqual(len(all_owners), 1)
        self.assertIn(owner, all_owners)

        # 6. Duplicate owner_id prevention
        duplicate_owner = Owner(
            owner_id="OWN-001",
            name="Alice Imposter",
            contact_number="555-9999",
        )
        with self.assertRaises(ValueError) as ctx:
            self.db.add_owner(duplicate_owner)
        self.assertIn("already exists", str(ctx.exception))

        # 7. Type validation on add_owner
        with self.assertRaises(TypeError):
            self.db.add_owner("NotAnOwnerObject")  # type: ignore

        # 8. Name validation
        with self.assertRaises(ValueError):
            Owner("OWN-002", "", "555-0142")
        with self.assertRaises(ValueError):
            Owner("OWN-002", "   ", "555-0142")
        with self.assertRaises(TypeError):
            Owner("OWN-002", 12345, "555-0142")  # type: ignore

        # 9. Phone validation
        with self.assertRaises(ValueError):
            Owner("OWN-002", "Bob", "")
        with self.assertRaises(ValueError):
            Owner("OWN-002", "Bob", "phone-with-letters")
        with self.assertRaises(ValueError):
            Owner("OWN-002", "Bob", "12345")  # < 7 digits
        with self.assertRaises(ValueError):
            Owner("OWN-002", "Bob", "1234567890123456")  # > 15 digits
        with self.assertRaises(TypeError):
            Owner("OWN-002", "Bob", 5550142)  # type: ignore

        # 10. Property setters update values correctly
        owner.name = "Alice J. Smith"
        self.assertEqual(owner.name, "Alice J. Smith")
        owner.phone = "555-9876"
        self.assertEqual(owner.contact_number, "555-9876")
        self.assertEqual(owner.phone, "555-9876")

        # 11. String formatting checks
        self.assertIn("OWN-001", owner.get_info())
        self.assertIn("Alice J. Smith", owner.get_info())
        self.assertIn("555-9876", owner.get_info())
        self.assertIn("OWN-001", str(owner))
        self.assertIn("OWN-001", repr(owner))

    # =========================================================================
    # Required Scenario 2: Add Pet Record via PetFactory
    # =========================================================================
    def test_add_pet_via_factory(self) -> None:
        """
        Test creating Pet records via PetFactory.create_pet() for all 4 supported types.
        Verifies:
          - Successful creation of Dog, Cat, Bird, and Rabbit
          - Attribute initialization and normalization
          - Owner association linking
          - Addition and retrieval in ClinicDatabase
          - Database filtering by owner ID
          - Rejection of unsupported species (e.g., Snake, Dragon, Fish)
          - Duplicate pet_id prevention
        """
        # Register prerequisite owner
        owner = Owner("OWN-001", "Bob Smith", "555-0288")
        self.db.add_owner(owner)

        # Supported types inspection
        supported = PetFactory.get_supported_types()
        self.assertEqual(supported, ["Dog", "Cat", "Bird", "Rabbit"])

        # 1. Create all 4 supported pet types
        dog = PetFactory.create_pet(
            pet_id="PET-001",
            name="Buddy",
            pet_type="Dog",
            breed="Golden Retriever",
            age=3,
            weight=28.5,
            owner_id=owner.owner_id,
        )
        cat = PetFactory.create_pet(
            pet_id="PET-002",
            name="Luna",
            pet_type="Cat",
            breed="Siamese",
            age=2,
            weight=4.2,
            owner_id=owner.owner_id,
        )
        bird = PetFactory.create_pet(
            pet_id="PET-003",
            name="Pip",
            pet_type="Bird",
            breed="Cockatiel",
            age=1,
            weight=0.1,
            owner_id=owner.owner_id,
        )
        rabbit = PetFactory.create_pet(
            pet_id="PET-004",
            name="Thumper",
            pet_type="Rabbit",
            breed="Holland Lop",
            age=2,
            weight=1.8,
            owner_id=owner.owner_id,
        )

        pets = [dog, cat, bird, rabbit]
        expected_types = ["Dog", "Cat", "Bird", "Rabbit"]

        for pet, exp_type in zip(pets, expected_types):
            self.assertIsInstance(pet, Pet)
            self.assertEqual(pet.pet_type, exp_type)
            self.assertEqual(pet.owner_id, owner.owner_id)
            self.db.add_pet(pet)

        # 2. Database verification
        all_pets = self.db.get_all_pets()
        self.assertEqual(len(all_pets), 4)

        for pet in pets:
            retrieved = self.db.get_pet(pet.pet_id)
            self.assertIs(retrieved, pet)

        # Non-existent pet lookup
        self.assertIsNone(self.db.get_pet("PET-NONEXISTENT"))

        # Filter pets by owner
        owner_pets = self.db.get_pets_by_owner(owner.owner_id)
        self.assertEqual(len(owner_pets), 4)
        self.assertEqual(self.db.get_pets_by_owner("NON-EXISTENT-OWNER"), [])

        # 3. Species normalization (case insensitivity)
        pet_case = PetFactory.create_pet(
            pet_id="PET-005",
            name="Max",
            pet_type="  dOg  ",
            breed="Labrador",
            age=4,
            weight=30.0,
            owner_id=owner.owner_id,
        )
        self.assertEqual(pet_case.pet_type, "Dog")
        self.db.add_pet(pet_case)

        # 4. Duplicate pet_id rejection
        dup_pet = PetFactory.create_pet(
            pet_id="PET-001",
            name="Buddy Clone",
            pet_type="Dog",
            breed="Poodle",
            age=1,
            weight=10.0,
            owner_id=owner.owner_id,
        )
        with self.assertRaises(ValueError) as ctx:
            self.db.add_pet(dup_pet)
        self.assertIn("already exists", str(ctx.exception))

        # 5. Rejection of unsupported species
        invalid_species = ["Snake", "Fish", "Dragon", "Hamster", "Lizard", ""]
        for species in invalid_species:
            with self.assertRaises(ValueError):
                PetFactory.create_pet(
                    pet_id=f"PET-INV-{species}",
                    name="InvalidPet",
                    pet_type=species,
                    breed="Unknown",
                    age=1,
                    weight=1.0,
                    owner_id=owner.owner_id,
                )

        # Non-string pet type
        with self.assertRaises(TypeError):
            PetFactory.create_pet(
                pet_id="PET-INV-TYPE",
                name="InvalidPet",
                pet_type=999,  # type: ignore
                breed="Unknown",
                age=1,
                weight=1.0,
                owner_id=owner.owner_id,
            )

    # =========================================================================
    # Required Scenario 3: Schedule Appointment
    # =========================================================================
    def test_schedule_appointment(self) -> None:
        """
        Test scheduling appointments in ClinicDatabase linking Pet and Owner.
        Verifies:
          - Successful creation and link verification
          - Date, time, reason, and status (default SCHEDULED)
          - Database registration and retrieval by appointment_id
          - Query appointments by pet and by owner
          - Duplicate appointment_id prevention
          - Rejection of invalid types
        """
        # Prerequisites
        owner = Owner("OWN-001", "Carol Davis", "555-0377")
        self.db.add_owner(owner)

        pet = PetFactory.create_pet(
            pet_id="PET-001",
            name="Pip",
            pet_type="Bird",
            breed="Cockatiel",
            age=1,
            weight=0.1,
            owner_id=owner.owner_id,
        )
        self.db.add_pet(pet)

        # 1. Create Appointment
        apt = Appointment(
            appointment_id="APT-001",
            pet=pet,
            owner=owner,
            date="2026-09-15",
            time="10:00 AM",
            reason="Annual Wellness Checkup & Feather Inspection",
        )

        # Verify initial properties
        self.assertEqual(apt.appointment_id, "APT-001")
        self.assertIs(apt.pet, pet)
        self.assertEqual(apt.pet_id, "PET-001")
        self.assertIs(apt.owner, owner)
        self.assertEqual(apt.owner_id, "OWN-001")
        self.assertEqual(apt.date, "2026-09-15")
        self.assertEqual(apt.time, "10:00 AM")
        self.assertEqual(apt.reason, "Annual Wellness Checkup & Feather Inspection")
        self.assertEqual(apt.status, AppointmentStatus.SCHEDULED)

        # 2. Schedule in ClinicDatabase
        self.db.schedule_appointment(apt)

        # 3. Retrieve from ClinicDatabase
        retrieved = self.db.get_appointment("APT-001")
        self.assertIsNotNone(retrieved)
        self.assertIs(retrieved, apt)
        self.assertEqual(retrieved.status, AppointmentStatus.SCHEDULED)

        # Non-existent appointment lookup
        self.assertIsNone(self.db.get_appointment("APT-NONEXISTENT"))

        # 4. Query by Pet and Owner
        pet_apts = self.db.get_appointments_by_pet(pet.pet_id)
        self.assertEqual(len(pet_apts), 1)
        self.assertIs(pet_apts[0], apt)

        owner_apts = self.db.get_appointments_by_owner(owner.owner_id)
        self.assertEqual(len(owner_apts), 1)
        self.assertIs(owner_apts[0], apt)

        all_apts = self.db.get_all_appointments()
        self.assertEqual(len(all_apts), 1)
        self.assertIn(apt, all_apts)

        # 5. Duplicate appointment_id rejection
        dup_apt = Appointment(
            appointment_id="APT-001",
            pet=pet,
            owner=owner,
            date="2026-09-20",
            time="11:00 AM",
            reason="Duplicate booking attempt",
        )
        with self.assertRaises(ValueError) as ctx:
            self.db.schedule_appointment(dup_apt)
        self.assertIn("already exists", str(ctx.exception))

        # 6. Type check on schedule_appointment
        with self.assertRaises(TypeError):
            self.db.schedule_appointment("NotAnAppointment")  # type: ignore

    # =========================================================================
    # Required Scenario 4: Cancel Appointment
    # =========================================================================
    def test_cancel_appointment(self) -> None:
        """
        Test cancelling an appointment and verifying state lifecycle.
        Verifies:
          - Status transitions to CANCELLED via model cancel() and database cancel_appointment()
          - Completed appointments cannot be cancelled
          - Cancelled appointments cannot be completed
          - Cancelling a non-existent appointment ID returns False
        """
        # Prerequisites
        owner = Owner("OWN-001", "Alice Johnson", "555-0142")
        self.db.add_owner(owner)

        pet = PetFactory.create_pet(
            pet_id="PET-001",
            name="Buddy",
            pet_type="Dog",
            breed="Golden Retriever",
            age=3,
            weight=28.5,
            owner_id=owner.owner_id,
        )
        self.db.add_pet(pet)

        # 1. Cancel a SCHEDULED appointment via database method
        apt1 = Appointment(
            appointment_id="APT-001",
            pet=pet,
            owner=owner,
            date="2026-09-15",
            time="10:00 AM",
            reason="Routine Checkup",
        )
        self.db.schedule_appointment(apt1)
        self.assertEqual(apt1.status, AppointmentStatus.SCHEDULED)

        success = self.db.cancel_appointment("APT-001")
        self.assertTrue(success)
        self.assertEqual(apt1.status, AppointmentStatus.CANCELLED)

        # 2. Cancelling an already cancelled appointment remains CANCELLED
        apt1.cancel()
        self.assertEqual(apt1.status, AppointmentStatus.CANCELLED)

        # 3. Completed appointments cannot be cancelled
        apt2 = Appointment(
            appointment_id="APT-002",
            pet=pet,
            owner=owner,
            date="2026-09-16",
            time="02:00 PM",
            reason="Vaccination",
        )
        self.db.schedule_appointment(apt2)
        apt2.complete()
        self.assertEqual(apt2.status, AppointmentStatus.COMPLETED)

        with self.assertRaises(ValueError) as ctx:
            apt2.cancel()
        self.assertIn("already been completed", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            self.db.cancel_appointment("APT-002")
        self.assertIn("already been completed", str(ctx.exception))

        # 4. Cancelled appointment cannot transition to completed
        with self.assertRaises(ValueError) as ctx:
            apt1.complete()
        self.assertIn("has been cancelled", str(ctx.exception))

        # 5. Cancelling non-existent appointment returns False
        self.assertFalse(self.db.cancel_appointment("APT-DOES-NOT-EXIST"))

    # =========================================================================
    # Required Scenario 5: Validate Singleton ClinicDatabase
    # =========================================================================
    def test_singleton_clinic_database(self) -> None:
        """
        Test that ClinicDatabase enforces a strict Singleton design pattern.
        Verifies:
          - Multiple calls return the exact same instance (db1 is db2 == True)
          - State modifications in one reference are immediately reflected in the other
          - clear_all() purges collections while preserving singleton identity
        """
        db1 = ClinicDatabase()
        db2 = ClinicDatabase()

        # 1. Identity assertion
        self.assertIs(db1, db2)
        self.assertTrue(db1 is db2)

        # 2. Data persistence across instances
        owner = Owner("OWN-001", "David Clark", "555-0999")
        db1.add_owner(owner)

        self.assertEqual(len(db2.get_all_owners()), 1)
        self.assertIs(db2.get_owner("OWN-001"), owner)

        pet = PetFactory.create_pet(
            pet_id="PET-001",
            name="Charlie",
            pet_type="Rabbit",
            breed="Mini Rex",
            age=1,
            weight=1.5,
            owner_id=owner.owner_id,
        )
        db2.add_pet(pet)

        self.assertEqual(len(db1.get_all_pets()), 1)
        self.assertIs(db1.get_pet("PET-001"), pet)

        # 3. clear_all() resets state while preserving identity
        db1.clear_all()

        self.assertEqual(len(db2.get_all_owners()), 0)
        self.assertEqual(len(db2.get_all_pets()), 0)
        self.assertEqual(len(db2.get_all_appointments()), 0)
        self.assertIs(db1, db2)
        self.assertTrue(db1 is db2)

    # =========================================================================
    # Additional Comprehensive Tests: Validation Edge Cases
    # =========================================================================
    def test_validation_edge_cases(self) -> None:
        """
        Test input boundary conditions and validation edge cases:
          - Pet negative age and non-integer age rejection
          - Pet zero, negative, NaN, Inf, and non-numeric weight rejection
          - Non-whitelisted pet species in both Pet and PetFactory
          - Owner contact number format boundaries
          - Empty and whitespace string rejections for identifiers and names
        """
        # 1. Negative age
        with self.assertRaises(ValueError):
            Pet("P-1", "Rover", "Dog", "Beagle", -1, 10.0, "O-1")
        with self.assertRaises(ValueError):
            PetFactory.create_pet("P-1", "Rover", "Dog", "Beagle", -5, 10.0, "O-1")

        # Non-integer age (float, boolean, None)
        with self.assertRaises(TypeError):
            Pet("P-1", "Rover", "Dog", "Beagle", 2.5, 10.0, "O-1")  # type: ignore
        with self.assertRaises(TypeError):
            Pet("P-1", "Rover", "Dog", "Beagle", True, 10.0, "O-1")  # type: ignore
        with self.assertRaises(TypeError):
            Pet("P-1", "Rover", "Dog", "Beagle", None, 10.0, "O-1")  # type: ignore

        # 2. Zero or negative weight
        with self.assertRaises(ValueError):
            Pet("P-1", "Rover", "Dog", "Beagle", 2, 0.0, "O-1")
        with self.assertRaises(ValueError):
            Pet("P-1", "Rover", "Dog", "Beagle", 2, -0.5, "O-1")
        with self.assertRaises(ValueError):
            PetFactory.create_pet("P-1", "Rover", "Dog", "Beagle", 2, 0.0, "O-1")
        with self.assertRaises(ValueError):
            PetFactory.create_pet("P-1", "Rover", "Dog", "Beagle", 2, -10.0, "O-1")

        # NaN / Inf weight
        with self.assertRaises(ValueError):
            Pet("P-1", "Rover", "Dog", "Beagle", 2, float("nan"), "O-1")
        with self.assertRaises(ValueError):
            Pet("P-1", "Rover", "Dog", "Beagle", 2, float("inf"), "O-1")

        # Non-numeric weight
        with self.assertRaises(TypeError):
            Pet("P-1", "Rover", "Dog", "Beagle", 2, "heavy", "O-1")  # type: ignore
        with self.assertRaises(TypeError):
            Pet("P-1", "Rover", "Dog", "Beagle", 2, True, "O-1")  # type: ignore

        # 3. Non-whitelisted species
        for invalid_sp in ["Hamster", "Ferret", "Horse", "Turtle"]:
            with self.assertRaises(ValueError):
                Pet("P-1", "Tiny", invalid_sp, "Standard", 1, 1.0, "O-1")
            with self.assertRaises(ValueError):
                PetFactory.create_pet("P-1", "Tiny", invalid_sp, "Standard", 1, 1.0, "O-1")

        # 4. Invalid contact numbers
        with self.assertRaises(ValueError):
            Owner("O-1", "John", "no-digits-here")
        with self.assertRaises(ValueError):
            Owner("O-1", "John", "123456")  # 6 digits (< 7)
        with self.assertRaises(ValueError):
            Owner("O-1", "John", "1234567890123456")  # 16 digits (> 15)

        # 5. Empty and whitespace-only strings
        with self.assertRaises(ValueError):
            Owner("", "John", "555-0142")
        with self.assertRaises(ValueError):
            Owner("   ", "John", "555-0142")
        with self.assertRaises(ValueError):
            Owner("O-1", "   ", "555-0142")
        with self.assertRaises(ValueError):
            Pet("", "Rover", "Dog", "Beagle", 2, 10.0, "O-1")
        with self.assertRaises(ValueError):
            Pet("P-1", "   ", "Dog", "Beagle", 2, 10.0, "O-1")
        with self.assertRaises(ValueError):
            Pet("P-1", "Rover", "Dog", "   ", 2, 10.0, "O-1")
        with self.assertRaises(ValueError):
            Pet("P-1", "Rover", "Dog", "Beagle", 2, 10.0, "   ")

    # =========================================================================
    # Additional Comprehensive Tests: Referential Integrity
    # =========================================================================
    def test_referential_integrity(self) -> None:
        """
        Test referential integrity constraints across models and database:
          - Cannot add a pet whose owner is not registered in the database
          - Cannot create an appointment where pet owner does not match appointment owner
          - Cannot schedule an appointment where pet is not in the database
          - Cannot schedule an appointment where owner is not in the database
        """
        owner1 = Owner("OWN-001", "Alice Johnson", "555-0142")
        owner2 = Owner("OWN-002", "Bob Smith", "555-0288")
        self.db.add_owner(owner1)
        self.db.add_owner(owner2)

        pet1 = PetFactory.create_pet(
            pet_id="PET-001",
            name="Buddy",
            pet_type="Dog",
            breed="Retriever",
            age=3,
            weight=25.0,
            owner_id=owner1.owner_id,
        )

        # 1. Unregistered owner cannot have pets added to database
        orphan_pet = PetFactory.create_pet(
            pet_id="PET-ORPHAN",
            name="Orphan",
            pet_type="Cat",
            breed="Domestic",
            age=1,
            weight=3.5,
            owner_id="UNREGISTERED-OWNER",
        )
        with self.assertRaises(ValueError) as ctx:
            self.db.add_pet(orphan_pet)
        self.assertIn("does not exist", str(ctx.exception))

        # Add pet1 for owner1
        self.db.add_pet(pet1)

        # 2. Appointment cannot link pet to a different owner
        with self.assertRaises(ValueError) as ctx:
            Appointment(
                appointment_id="APT-MISMATCH",
                pet=pet1,
                owner=owner2,  # Pet belongs to owner1, not owner2!
                date="2026-09-15",
                time="10:00 AM",
                reason="Checkup",
            )
        self.assertIn("does not belong to owner", str(ctx.exception))

        # 3. Appointment setter prevents pet/owner mismatch
        valid_apt = Appointment(
            appointment_id="APT-001",
            pet=pet1,
            owner=owner1,
            date="2026-09-15",
            time="10:00 AM",
            reason="Checkup",
        )
        with self.assertRaises(ValueError):
            valid_apt.owner = owner2  # Mismatch with pet1.owner_id

        pet2 = PetFactory.create_pet(
            pet_id="PET-002",
            name="Luna",
            pet_type="Cat",
            breed="Siamese",
            age=2,
            weight=4.0,
            owner_id=owner2.owner_id,
        )
        with self.assertRaises(ValueError):
            valid_apt.pet = pet2  # Mismatch with owner1

        # 4. Scheduling appointment with un-persisted pet or owner
        unregistered_pet = PetFactory.create_pet(
            pet_id="PET-NOT-IN-DB",
            name="Ghost",
            pet_type="Bird",
            breed="Parrot",
            age=1,
            weight=0.5,
            owner_id=owner1.owner_id,
        )
        apt_unregistered_pet = Appointment(
            appointment_id="APT-GHOST",
            pet=unregistered_pet,
            owner=owner1,
            date="2026-09-15",
            time="10:00 AM",
            reason="Checkup",
        )
        with self.assertRaises(ValueError) as ctx:
            self.db.schedule_appointment(apt_unregistered_pet)
        self.assertIn("is not in the database", str(ctx.exception))

        unregistered_owner = Owner("OWN-GHOST", "Ghost Owner", "555-0999")
        ghost_pet = PetFactory.create_pet(
            pet_id="PET-GHOST2",
            name="Phantom",
            pet_type="Cat",
            breed="Tabby",
            age=2,
            weight=4.0,
            owner_id=unregistered_owner.owner_id,
        )
        # Manually register ghost_pet by temporarily bypassing owner check isn't allowed,
        # but let's test appointment registration where owner is missing from DB:
        self.db.add_owner(unregistered_owner)
        self.db.add_pet(ghost_pet)
        self.db.remove_owner(unregistered_owner.owner_id)

        apt_ghost_owner = Appointment(
            appointment_id="APT-GHOST2",
            pet=ghost_pet,
            owner=unregistered_owner,
            date="2026-09-15",
            time="10:00 AM",
            reason="Checkup",
        )
        with self.assertRaises(ValueError) as ctx:
            self.db.schedule_appointment(apt_ghost_owner)
        self.assertIn("is not in the database", str(ctx.exception))

    # =========================================================================
    # Additional Comprehensive Tests: Sample Data Validation
    # =========================================================================
    def test_sample_data_validation(self) -> None:
        """
        Test initialize_sample_data() from main.py.
        Verifies:
          - Creates >= 3 registered owners
          - Creates >= 4 registered pets covering all 4 supported types (Dog, Cat, Bird, Rabbit)
          - Creates >= 2 scheduled/recorded appointments
          - Database statistics reflect correct totals and type breakdowns
        """
        db = initialize_sample_data()

        # 1. Owner counts
        owners = db.get_all_owners()
        self.assertGreaterEqual(
            len(owners), 3, f"Expected at least 3 owners, got {len(owners)}"
        )

        # 2. Pet counts and species diversity
        pets = db.get_all_pets()
        self.assertGreaterEqual(
            len(pets), 4, f"Expected at least 4 pets, got {len(pets)}"
        )

        species_found = {pet.pet_type for pet in pets}
        for req_species in ("Dog", "Cat", "Bird", "Rabbit"):
            self.assertIn(
                req_species,
                species_found,
                f"Required species '{req_species}' missing from sample pets",
            )

        # 3. Appointment counts and statuses
        appointments = db.get_all_appointments()
        self.assertGreaterEqual(
            len(appointments),
            2,
            f"Expected at least 2 appointments, got {len(appointments)}",
        )

        statuses_found = {apt.status for apt in appointments}
        self.assertIn(AppointmentStatus.SCHEDULED, statuses_found)

        # 4. Statistics method verification
        stats = db.get_statistics()
        self.assertGreaterEqual(stats["total_owners"], 3)
        self.assertGreaterEqual(stats["total_pets"], 4)
        self.assertGreaterEqual(stats["total_appointments"], 2)

        for req_species in ("Dog", "Cat", "Bird", "Rabbit"):
            self.assertIn(req_species, stats["pets_by_type"])
            self.assertGreaterEqual(stats["pets_by_type"][req_species], 1)

    # =========================================================================
    # Additional Comprehensive Tests: Appointment Status & State Transitions
    # =========================================================================
    def test_appointment_status_transitions(self) -> None:
        """
        Test valid and invalid appointment status transitions and string parsing.
        """
        owner = Owner("OWN-001", "Emma Watson", "555-0812")
        self.db.add_owner(owner)

        pet = PetFactory.create_pet(
            pet_id="PET-001",
            name="Otis",
            pet_type="Dog",
            breed="Pug",
            age=5,
            weight=8.2,
            owner_id=owner.owner_id,
        )
        self.db.add_pet(pet)

        apt = Appointment(
            appointment_id="APT-001",
            pet=pet,
            owner=owner,
            date="2026-09-18",
            time="03:00 PM",
            reason="Checkup",
            status="Scheduled",
        )
        self.assertEqual(apt.status, AppointmentStatus.SCHEDULED)

        # Complete appointment
        apt.complete()
        self.assertEqual(apt.status, AppointmentStatus.COMPLETED)

        # String assignment to status property
        apt2 = Appointment(
            appointment_id="APT-002",
            pet=pet,
            owner=owner,
            date="2026-09-19",
            time="09:00 AM",
            reason="Dental",
            status="Completed",
        )
        self.assertEqual(apt2.status, AppointmentStatus.COMPLETED)

        apt3 = Appointment(
            appointment_id="APT-003",
            pet=pet,
            owner=owner,
            date="2026-09-20",
            time="10:00 AM",
            reason="Grooming",
            status="Cancelled",
        )
        self.assertEqual(apt3.status, AppointmentStatus.CANCELLED)

        # Invalid status string
        with self.assertRaises(ValueError):
            apt.status = "UnknownStatus"

        # Invalid status type
        with self.assertRaises(TypeError):
            apt.status = 12345  # type: ignore

    # =========================================================================
    # Additional Comprehensive Tests: Database Removal & Maintenance
    # =========================================================================
    def test_database_removal_operations(self) -> None:
        """
        Test record removal methods on ClinicDatabase:
          - remove_owner()
          - remove_pet()
          - remove_appointment()
        """
        owner = Owner("OWN-001", "Frank Miller", "555-0456")
        self.db.add_owner(owner)

        pet = PetFactory.create_pet(
            pet_id="PET-001",
            name="Barnaby",
            pet_type="Cat",
            breed="British Shorthair",
            age=4,
            weight=5.5,
            owner_id=owner.owner_id,
        )
        self.db.add_pet(pet)

        apt = Appointment(
            appointment_id="APT-001",
            pet=pet,
            owner=owner,
            date="2026-09-22",
            time="11:30 AM",
            reason="Vaccination",
        )
        self.db.schedule_appointment(apt)

        # Remove appointment
        self.assertTrue(self.db.remove_appointment("APT-001"))
        self.assertFalse(self.db.remove_appointment("APT-001"))
        self.assertIsNone(self.db.get_appointment("APT-001"))

        # Remove pet
        self.assertTrue(self.db.remove_pet("PET-001"))
        self.assertFalse(self.db.remove_pet("PET-001"))
        self.assertIsNone(self.db.get_pet("PET-001"))

        # Remove owner
        self.assertTrue(self.db.remove_owner("OWN-001"))
        self.assertFalse(self.db.remove_owner("OWN-001"))
        self.assertIsNone(self.db.get_owner("OWN-001"))

    # =========================================================================
    # Additional Comprehensive Tests: Factory String Coercion
    # =========================================================================
    def test_pet_factory_type_coercion(self) -> None:
        """
        Test PetFactory coerced string numeric inputs for GUI compatibility:
          - String age ('3') parsed to int
          - String weight ('12.5') parsed to float
          - Invalid non-numeric strings raise ValueError
        """
        pet = PetFactory.create_pet(
            pet_id="PET-COERCE",
            name="CoercePet",
            pet_type="Dog",
            breed="Mixed",
            age=" 4 ",
            weight=" 14.75 ",
            owner_id="OWN-001",
        )
        self.assertIsInstance(pet.age, int)
        self.assertEqual(pet.age, 4)
        self.assertIsInstance(pet.weight, float)
        self.assertEqual(pet.weight, 14.75)

        # Invalid string age
        with self.assertRaises(ValueError):
            PetFactory.create_pet(
                pet_id="PET-BAD-AGE",
                name="BadAge",
                pet_type="Dog",
                breed="Mixed",
                age="four",
                weight=10.0,
                owner_id="OWN-001",
            )

        # Invalid string weight
        with self.assertRaises(ValueError):
            PetFactory.create_pet(
                pet_id="PET-BAD-WT",
                name="BadWeight",
                pet_type="Dog",
                breed="Mixed",
                age=4,
                weight="ten_point_five",
                owner_id="OWN-001",
            )

    # =========================================================================
    # Additional Comprehensive Tests: String Representations
    # =========================================================================
    def test_model_string_representations(self) -> None:
        """
        Test get_info(), get_details(), get_summary(), __str__(), and __repr__()
        on all domain models.
        """
        owner = Owner("OWN-001", "Grace Hopper", "555-1952")
        pet = PetFactory.create_pet(
            pet_id="PET-001",
            name="Nanosecond",
            pet_type="Cat",
            breed="Calico",
            age=2,
            weight=3.8,
            owner_id="OWN-001",
        )
        apt = Appointment(
            appointment_id="APT-001",
            pet=pet,
            owner=owner,
            date="2026-09-25",
            time="04:00 PM",
            reason="Checkup",
        )

        # Owner representations
        self.assertIn("OWN-001", owner.get_info())
        self.assertIn("Grace Hopper", str(owner))
        self.assertIn("Owner(", repr(owner))

        # Pet representations
        self.assertIn("PET-001", pet.get_info())
        self.assertIn("Calico", pet.get_details())
        self.assertIn("Nanosecond", str(pet))
        self.assertIn("Pet(", repr(pet))

        # Appointment representations
        self.assertIn("APT-001", apt.get_info())
        self.assertIn("Appointment ID:", apt.get_summary())
        self.assertIn("Appointment #APT-001", str(apt))
        self.assertIn("Appointment(", repr(apt))


if __name__ == "__main__":
    unittest.main()
