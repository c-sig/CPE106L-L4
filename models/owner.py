"""
Owner model representing a registered pet owner in the clinic.
Follows Lab3 encapsulation and validation patterns.
"""
import re


class Owner:
    """
    Represents a pet owner in the clinic management system.

    Attributes:
        _owner_id (str): Unique owner identifier (e.g., 'OWN-001').
        _name (str): Full legal name of the owner.
        _contact_number (str): Contact telephone / mobile number.
    """

    def __init__(self, owner_id: str, name: str, contact_number: str) -> None:
        """
        Initialize an Owner instance.

        Args:
            owner_id: Unique identifier for the owner.
            name: Full name of the owner.
            contact_number: Contact telephone or mobile number.

        Raises:
            TypeError: If any argument is not a string.
            ValueError: If owner_id is empty or validation fails for fields.
        """
        if not isinstance(owner_id, str):
            raise TypeError("Owner ID must be a string")
        if not owner_id.strip():
            raise ValueError("Owner ID cannot be empty")
        self._owner_id = owner_id.strip()

        # Set through property setters to enforce validation rules
        self.name = name
        self.contact_number = contact_number

    @property
    def owner_id(self) -> str:
        """Return the unique owner ID (read-only)."""
        return self._owner_id

    @property
    def name(self) -> str:
        """Return the owner's full name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """
        Set the owner's full name.

        Raises:
            TypeError: If value is not a string.
            ValueError: If value is empty or consists solely of whitespace.
        """
        if not isinstance(value, str):
            raise TypeError("Owner name must be a string")
        if not value.strip():
            raise ValueError("Owner name cannot be empty")
        self._name = value.strip()

    @property
    def contact_number(self) -> str:
        """Return the owner's contact number."""
        return self._contact_number

    @contact_number.setter
    def contact_number(self, value: str) -> None:
        """
        Set the owner's contact number.

        Raises:
            TypeError: If value is not a string.
            ValueError: If value is empty, contains invalid characters, or has invalid digit length.
        """
        if not isinstance(value, str):
            raise TypeError("Contact number must be a string")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Contact number cannot be empty")

        if not re.match(r"^[0-9+\-() .]+$", cleaned):
            raise ValueError("Contact number contains invalid characters")

        digits = [c for c in cleaned if c.isdigit()]
        if len(digits) < 7 or len(digits) > 15:
            raise ValueError(
                f"Contact number must contain between 7 and 15 digits (got {len(digits)})"
            )

        self._contact_number = cleaned

    @property
    def phone(self) -> str:
        """Alias property for contact_number (Lab3 compatibility)."""
        return self._contact_number

    @phone.setter
    def phone(self, value: str) -> None:
        """Alias setter for contact_number."""
        self.contact_number = value

    def get_info(self) -> str:
        """Return formatted detailed single-line string representation."""
        return f"[{self._owner_id}] {self._name} | Contact: {self._contact_number}"

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return f"{self._name} ({self._owner_id})"

    def __repr__(self) -> str:
        """Return developer-friendly debug representation."""
        return f"Owner(owner_id='{self._owner_id}', name='{self._name}', contact_number='{self._contact_number}')"
