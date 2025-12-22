from enum import Enum
from typing import Any

from .base import Base


class Priority(Enum):
    """Priority levels for requirement tags."""

    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"

    def __str__(self):
        return self.value


class RequirementTag(Base):
    """
    Represents a RequirementTag declaration inside a Packtype package.

    A RequirementTag marks an element with a defined priority level
    (P0-P3) and optional description. Created when parsing `requirement`
    declarations.
    """

    _PT_ATTRIBUTES: dict[str, tuple[Any, list[Any]]] = {
        "priority": (Priority.P0, list(Priority)),
    }

    def __init__(self, name: str, priority: Priority, description: str | None = None):
        super().__init__()
        self.name = name
        self.priority = priority
        self.description = description

    def __repr__(self) -> str:
        """Compact debug-friendly representation."""
        if self.description:
            return f"<RequirementTag {self.name}: {self.priority.value} — {self.description}>"
        return f"<RequirementTag {self.name}: {self.priority.value}>"

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.name} ({self.priority.value})"

    @property
    def __doc__(self) -> str | None:
        """Expose the description as a docstring-like attribute."""
        return self.description
