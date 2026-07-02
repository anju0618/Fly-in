#!/usr/bin/env python3

from drone import Drone
from map_data import MapData


class InvalidMoveError(Exception):
    """ドローンが繋がっていないゾーンに移動しようとしたときのエラー"""
    pass


class CapacityExceededError(Exception):
    """max_dronesを超えて進入しようとしたときのエラー"""
    pass


class Simulator:
    def __init__(self, map_data: MapData) -> None:
        self.map_data = map_data
        self.drones: list[Drone] = []
        self.zone_occupancy = {
                name: 0 for name in self.map_data.zones
        }
        self.current_turn: int = 1

        start_name = self.map_data.start_hub.name
        self.zone_occupancy[start_name] = self.map_data.nb_drones
        for i in range(1, self.map_data.nb_drones + 1):
            drone = Drone(
                    i,
                    self.map_data.start_hub.name
                    )
            self.drones.append(drone)

    def run_turn(self, moves: dict[int, str]) -> None:

        self.current_turn += 1

        for drone_id, target_zone in moves.items():
            current_zone = self.drones[drone_id - 1].current_zone
            self.zone_occupancy[current_zone] -= 1

        for drone_id, target_zone in moves.items():
            current_zone = self.drones[drone_id - 1].current_zone
            valid_destinations = [
                name for name, _ in self.map_data.graph[current_zone]
                ]

            if target_zone in valid_destinations:
                max_drones = self.map_data.zones[target_zone].max_drones
                if self.zone_occupancy[target_zone] >= max_drones:
                    raise CapacityExceededError(f"{target_zone} is full.")

                else:
                    self.zone_occupancy[target_zone] += 1
                    self.drones[drone_id - 1].current_zone = target_zone

    def is_finished(self) -> bool:
        goal_name = self.map_data.goal_hub.name
        return all(d.current_zone == goal_name for d in self.drones)

    def run(self) -> None:
        while not self.is_finished():
            moves = pathfinder.compute_moves(self)

            if moves:
                turn_output = " ".join(f"D{d}-{z}" for d, z in moves.items())
                print(turn_output)

            self.run_turn(moves)
