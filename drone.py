#!/usr/bin/env python3
"""
Module defining the Drone class and its state management.
"""

from typing import Optional


class Drone:
    """Represents an autonomous drone within the simulation network."""

    def __init__(self, id_num: int, start_zone_name: str) -> None:
        self.id_num: int = id_num
        self.current_zone: str = start_zone_name
        self.target_zone: Optional[str] = None
        self.turns_to_arrive: int = 0

    @property
    def name(self) -> str:
        """Returns the formatted drone name string (e.g., 'D1')."""
        return f"D{self.id_num}"

    @property
    def is_in_flight(self) -> bool:
        """Checks if the drone is traversing a restricted connection."""
        return self.target_zone is not None and self.turns_to_arrive > 0
