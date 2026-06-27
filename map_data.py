#!/usr/bin/env python3
"""
Module defining the container for the parsed map data.
"""

from dataclasses import dataclass, field
from connection import Connection
from zone import Zone


@dataclass
class MapData:
    """Holds the complete parsed map configuration for the drone simulation.

    Attributes:
        nb_drones: The total number of drones in the simulation.
        start_hub: The designated starting zone for all drones.
        end_hub: The target destination zone for all drones.
        zones: A dictionary mapping zone names to their Zone objects.
        connections: A list of all unique bidirectional connections.
        graph: An adjacency list mapping a zone name to a list of connected
            neighbor zone names and their corresponding connection data.
    """
    nb_drones: int
    start_hub: Zone
    end_hub: Zone
    zones: dict[str, Zone] = field(default_factory=dict)
    connections: list[Connection] = field(default_factory=list)
    graph: dict[str, list[tuple[str, Connection]]] = field(
        default_factory=dict, init=False
    )

    def __post_init__(self) -> None:
        """Precomputes the adjacency list representation of the graph."""

        self.graph = {name: [] for name in self.zones}
        for conn in self.connections:
            if conn.zone1 in self.graph and conn.zone2 in self.graph:
                self.graph[conn.zone1].append((conn.zone2, conn))
                self.graph[conn.zone2].append((conn.zone1, conn))
