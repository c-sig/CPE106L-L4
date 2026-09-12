"""
Generic Pet model representing an animal patient in the clinic.
Follows Lab3 encapsulation and validation patterns.
"""
import math
from typing import Tuple

SUPPORTED_PET_TYPES: Tuple[str, ...] = ("Dog", "Cat", "Bird", "Rabbit")
SUPPORTED_TYPES: Tuple[str, ...] = SUPPORTED_PET_TYPES


class Pet:
    """
    Represents a pet patient in the clinic management system.

    Attributes:
        _pet_id (str): Unique pet identifier (e.g., 'PET-001').
        _name (str): Pet's given name.
        _pet_type (str): Species ('Dog', 'Cat', 'Bird', 'Rabbit').
        _breed (str): Specific breed or variety (e.g., 'Golden Retriever').
        _age (int): Age in whole years (>= 0).
        _weight (float): Body weight in kilograms (> 0.0).
        _owner_id (str): Identifier of the registered owner.
    """

    def __init__(
        self,
        pet_id: str,
        name: str,
        pet_type: str,
        breed: str,
        age: int,
        weight: float,
        owner_id: str,
    ) -> None:
        """
        Initialize a new Pet instance.

        Args:
            pet_id: Unique identifier for the pet.
            name: Pet's name.
            pet_type: Species ('Dog', 'Cat', 'Bird', 'Rabbit').
            breed: Pet breed or description.
            age: Pet age in whole years (>= 0).
            weight: Pet weight in kg (> 0.0).
            owner_id: Associated owner's ID.

        Raises:
            TypeError: If argument types are invalid.
            ValueError: If string values are empty or bounds/species validation fails.
        """
        if not isinstance(pet_id, str):
            raise TypeError("Pet ID must be a string")
        if not pet_id.strip():
            raise ValueError("Pet ID cannot be empty")
        self._pet_id = pet_id.strip()

        # Set via property setters to enforce all validation rules
        self.name = name
        self.pet_type = pet_type
        self.breed = breed
        self.age = age
        self.weight = weight
        self.owner_id = owner_id

    @property
    def pet_id(self) -> str:
        """Return the unique pet ID (read-only)."""
        return self._pet_id

    @property
    def name(self) -> str:
        """Return the pet's name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """
        Set the pet's name.

        Raises:
            TypeError: If value is not a string.
            ValueError: If value is empty or consists solely of whitespace.
        """
        if not isinstance(value, str):
            raise TypeError("Pet name must be a string")
        if not value.strip():
            raise ValueError("Pet name cannot be empty")
        self._name = value.strip()

    @property
    def pet_type(self) -> str:
        """Return the pet species."""
        return self._pet_type

    @pet_type.setter
    def pet_type(self, value: str) -> None:
        """
        Set and validate the pet species against supported types.

        Raises:
            TypeError: If value is not a string.
            ValueError: If value is not one of Dog, Cat, Bird, Rabbit.
        """
        if not isinstance(value, str):
            raise TypeError("Pet type must be a string")
        cleaned = value.strip().capitalize()
        if cleaned not in SUPPORTED_PET_TYPES:
            raise ValueError(
                f"Invalid pet type '{value}'. Supported types: {', '.join(SUPPORTED_PET_TYPES)}"
            )
        self._pet_type = cleaned

    @property
    def breed(self) -> str:
        """Return the pet's breed."""
        return self._breed

    @breed.setter
    def breed(self, value: str) -> None:
        """
        Set the pet's breed.

        Raises:
            TypeError: If value is not a string.
            ValueError: If value is empty or consists solely of whitespace.
        """
        if not isinstance(value, str):
            raise TypeError("Breed must be a string")
        if not value.strip():
            raise ValueError("Breed cannot be empty")
        self._breed = value.strip()

    @property
    def age(self) -> int:
        """Return the pet's age in whole years."""
        return self._age

    @age.setter
    def age(self, value: int) -> None:
        """
        Set the pet's age.

        Raises:
            TypeError: If value is a boolean or not an integer.
            ValueError: If value is negative.
        """
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("Age must be an integer")
        if value < 0:
            raise ValueError("Age cannot be negative")
        self._age = value

    @property
    def weight(self) -> float:
        """Return the pet's weight in kilograms."""
        return self._weight

    @weight.setter
    def weight(self, value: float) -> None:
        """
        Set the pet's weight.

        Raises:
            TypeError: If value is a boolean or not a numeric type.
            ValueError: If value is not a positive finite number (> 0.0).
        """
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("Weight must be a number")
        num_val = float(value)
        if math.isnan(num_val) or math.isinf(num_val) or num_val <= 0.0:
            raise ValueError("Weight must be greater than zero")
        self._weight = round(num_val, 2)

    @property
    def owner_id(self) -> str:
        """Return the associated owner ID."""
        return self._owner_id

    @owner_id.setter
    def owner_id(self, value: str) -> None:
        """
        Set the associated owner ID.

        Raises:
            TypeError: If value is not a string.
            ValueError: If value is empty or consists solely of whitespace.
        """
        if not isinstance(value, str):
            raise TypeError("Owner ID must be a string")
        if not value.strip():
            raise ValueError("Owner ID cannot be empty")
        self._owner_id = value.strip()

    def get_info(self) -> str:
        """Return formatted detailed string representation of the pet."""
        return (
            f"[{self._pet_id}] {self._name} ({self._pet_type} - {self._breed}) | "
            f"Age: {self._age} yrs | Weight: {self._weight:.1f} kg | Owner: {self._owner_id}"
        )

    def get_details(self) -> str:
        """Return concise technical details string."""
        return f"{self._pet_type} - {self._breed}, {self._age} yrs, {self._weight:.1f} kg"

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return f"{self._name} ({self._pet_type}, ID: {self._pet_id})"

    def __repr__(self) -> str:
        """Return developer-friendly debug representation."""
        return (
            f"Pet(pet_id='{self._pet_id}', name='{self._name}', pet_type='{self._pet_type}', "
            f"breed='{self._breed}', age={self._age}, weight={self._weight}, owner_id='{self._owner_id}')"
        )
