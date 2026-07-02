#!/usr/bin/env python3

from map_data import MapData
from collections import deque

class Pathfinder:
    def __init__(self, map_data: MapData) -> None:
        self.map_data = map_data
        self.residual_graph: dict[str, dict[str, int]] = {}

    def _add_edge(self, u: str, v: str, capacity: int) -> None:
        """残余グラフに容量付きの有向エッジ（順方向と逆方向）を追加する"""
        if u not in self.residual_graph:
            self.residual_graph[u] = {}
        if v not in self.residual_graph:
            self.residual_graph[v] = {}

        self.residual_graph[u][v] = capacity
        if u not in self.residual_graph[v]:
            self.residual_graph[v][u] = 0

    def build_network(self, max_time: int) -> None:
        """max_timeまでの時間グラフを構築"""
        inf_capacity = self.map_data.nb_drones

        for t in range(max_time + 1):

            for zone_name, zone in self.map_data.zones.items():
                in_node = f"{zone_name}_t{t}_in"
                out_node = f"zone_name_t{t}_out"
