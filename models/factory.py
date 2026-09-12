"""
Factory for creating Pet instances with species validation.
Follows Lab3 factory pattern conventions.
"""
from typing import List, Union

from .pet import Pet, SUPPORTED_PET_TYPES


class PetFactory:
    """
    Factory class providing standardized creation methods for Pet entities.
    """

    SUPPORTED_TYPES: List[str] = list(SUPPORTED_PET_TYPES)

    @classmethod
    def get_supported_types(cls) -> List[str]:
        """Return a defensive copy of all supported pet species."""
        return list(cls.SUPPORTED_TYPES)

    @classmethod
    def create_pet(
        cls,
        pet_id: str,
        name: str,
        pet_type: str,
        breed: str,
        age: Union[int, str],
        weight: Union[float, int, str],
        owner_id: str,
    ) -> Pet:
        """
        Create and return a new validated Pet instance.

        Args:
            pet_id: Unique identifier for the pet.
            name: Pet name.
            pet_type: Species ('Dog', 'Cat', 'Bird', 'Rabbit').
            breed: Pet breed or description.
            age: Pet age in years (integer >= 0, or numeric string).
            weight: Pet weight in kg (float > 0, or numeric string).
            owner_id: ID of the registered owner.

        Returns:
            Pet: A newly instantiated and validated Pet instance.

        Raises:
            ValueError: If pet_type is unsupported or any field validation fails.
            TypeError: If types for any arguments are incorrect.
        """
        if not isinstance(pet_type, str):
            raise TypeError("Pet type must be a string")

        normalized_type = pet_type.strip().capitalize()
        if normalized_type not in cls.SUPPORTED_TYPES:
            raise ValueError(
                f"Unsupported pet type '{pet_type}'. Supported types: {', '.join(cls.SUPPORTED_TYPES)}"
            )

        # Support string numeric coercion if called from Tkinter form entries
        parsed_age = age
        if isinstance(age, str):
            try:
                parsed_age = int(age.strip())
            except ValueError as err:
                raise ValueError(f"Age must be a valid integer, got '{age}'") from err

        parsed_weight = weight
        if isinstance(weight, str):
            try:
                parsed_weight = float(weight.strip())
            except ValueError as err:
                raise ValueError(
                    f"Weight must be a valid number, got '{weight}'"
                ) from err

        return Pet(
            pet_id=pet_id,
            name=name,
            pet_type=normalized_type,
            breed=breed,
            age=parsed_age,
            weight=parsed_weight,
            owner_id=owner_id,
        )
