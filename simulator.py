#!/usr/bin/env python3

from drone import Drone
from map_data import MapData


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
