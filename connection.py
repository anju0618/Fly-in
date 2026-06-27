#!/usr/bin/env python3
"""
Module defining connections between zones in the drone simulation.
"""

from dataclasses import dataclass


@dataclass
class Connection:
    """Represents a bidirectional connection (edge) between two zones."""
    zone1: str
    zone2: str
    max_link_capacity: int = 1
