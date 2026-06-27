#!/usr/bin/env python3
"""
Module defining zone types and zone configurations for the drone simulation.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class ZoneType(str, Enum):
    """Enumeration of zone types whithin the network.

    Attributes:
        NORMAL: Standard zone with a 1-turn movement const.
        BLOCKED: Inaccessible zone. Drones must not enter or pass through.
        RESTRICTED: Sensitive or dangerous zone with a 2-turn movement cost.
        PRIORITY: Preferred zone favored in pathfinding with a 1-turn cost.
    """
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


@dataclass
class Zone:
    """Represents a zone (node) in the network graph.

    Attributes:
        name: The unique identifier of the zone.
        x: The X coordinate of the zone.
        y: The Y coordinate of the zone.
        zone_type: The type of the zone determining its movement cost.
        max_drones: The maximum number of drones
            allowed in this zone simultaneously.
        colour: An optional colour used for visual representation.
    """
    name: str
    x: int
    y: int
    zone_type: ZoneType = ZoneType.NORMAL
    max_drones: int = 1
    colour: Optional[str] = None
