#!/usr/bin/env python3
"""Simulation engine module for navigating drones through network zones.

This module handles the state representation of
the drone fleet, turn mechanics,
and strict validation of movement and capacity constraints.
"""

from drone import Drone
from map_data import MapData
from typing import Any


class InvalidMoveError(Exception):
    """Exception raised when a drone attempts an invalid movement."""
    pass


class CapacityExceededError(Exception):
    """Exception raised when a zone or connection capacity is exceeded."""
    pass


class Simulator:
    """Manages the state and turn execution of the drone simulation."""

    def __init__(self, map_data: MapData) -> None:
        """Initializes the simulation state with parsed map configuration.

        Args:
            map_data: The complete configuration data of the parsed map.
        """
        self.map_data = map_data
        self.drones: list[Drone] = []
        self.zone_occupancy = {
            name: 0 for name in self.map_data.zones
        }
        self.current_turn: int = 1
        self.link_capacities = {}
        for conn in self.map_data.connections:
            pair = tuple(sorted([conn.zone1, conn.zone2]))
            self.link_capacities[pair] = conn.max_link_capacity

        start_name = self.map_data.start_hub.name
        self.zone_occupancy[start_name] = self.map_data.nb_drones
        for i in range(1, self.map_data.nb_drones + 1):
            drone = Drone(i, self.map_data.start_hub.name)
            self.drones.append(drone)

    def run_turn(self, moves: dict[int, str]) -> None:
        """Executes a single simulation turn with the provided movements.

        Args:
            moves: A dictionary mapping drone IDs to their target locations.

        Raises:
            CapacityExceededError: If a zone or connection
                                    exceeds max capacity.
        """
        self.current_turn += 1

        connection_usage: dict[tuple[str, str], int] = {}
        for drone_id, target_zone in moves.items():
            current_zone = self.drones[drone_id - 1].current_zone

            u, v = None, None
            if "-" in target_zone:
                u, v = target_zone.split("-", 1)
            elif "-" not in current_zone:  # 通常または優先ゾーンへの移動
                u, v = current_zone, target_zone

            if u and v:
                pair = (min(u, v), max(u, v))
                if pair in self.link_capacities:
                    connection_usage[pair] = connection_usage.get(pair, 0) + 1
                    if connection_usage[pair] > self.link_capacities[pair]:
                        raise CapacityExceededError(
                            f"Connection {u}-{v} capacity exceeded "
                            f"({connection_usage[pair]}/"
                            f"{self.link_capacities[pair]})."
                        )

        # --- パス2: 出発するドローンの容量先行解放 ---
        for drone_id, target_zone in moves.items():
            current_zone = self.drones[drone_id - 1].current_zone
            if "-" not in current_zone:
                self.zone_occupancy[current_zone] -= 1

        for drone_id, target_zone in moves.items():
            current_zone = self.drones[drone_id - 1].current_zone

            if "-" in current_zone:
                self.zone_occupancy[target_zone] += 1
                self.drones[drone_id - 1].current_zone = target_zone
                continue

            if "-" in target_zone:
                self.drones[drone_id - 1].current_zone = target_zone
                continue

            valid_destinations = [
                name for name, _ in self.map_data.graph[current_zone]
            ]

            if target_zone in valid_destinations:
                is_special = target_zone in (
                    self.map_data.start_hub.name,
                    self.map_data.end_hub.name,
                )
                max_drones = self.map_data.zones[target_zone].max_drones
                has_space = self.zone_occupancy[target_zone] < max_drones

                if not is_special and not has_space:
                    raise CapacityExceededError(f"Zone {target_zone} is full.")
                else:
                    self.zone_occupancy[target_zone] += 1
                    self.drones[drone_id - 1].current_zone = target_zone

    def is_finished(self) -> bool:
        """
        Checks whether all drones have successfully arrived at the end hub.
        """
        end_name = self.map_data.end_hub.name
        return all(d.current_zone == end_name for d in self.drones)

    def run(self, pathfinder: Any, show_capacity: bool = False) -> None:
        while not self.is_finished():
            moves = pathfinder.compute_moves(self)
            if moves:
                turn_output = " ".join(f"D{d}-{z}" for d, z in moves.items())
                print(turn_output)
            self.run_turn(moves)
            if show_capacity:
                print(f"--- Turn {self.current_turn - 1} Capacity Info ---")

                counts: dict[str, int] = {}
                for d in self.drones:
                    counts[d.current_zone] = counts.get(d.current_zone, 0) + 1

                for z_name, zone in self.map_data.zones.items():
                    if z_name in (
                        self.map_data.start_hub.name,
                        self.map_data.end_hub.name
                    ):
                        continue

                    c = counts.get(z_name, 0)
                    print(f"Zone {z_name}: {c}/{zone.max_drones} drones")

                for conn in self.map_data.connections:
                    c_name = f"{conn.zone1}-{conn.zone2}"
                    r_name = f"{conn.zone2}-{conn.zone1}"
                    c_count = counts.get(c_name, 0) + counts.get(r_name, 0)
                    m_cap = conn.max_link_capacity
                    print(
                        f"Connection {c_name}: "
                        f"{c_count}/{m_cap} capacity used"
                    )
