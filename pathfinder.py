#!/usr/bin/env python3
"""Pathfinding algorithm module using a Time-Expanded Network Flow approach.

This module models the temporal network layers to optimize schedules,
maximizing throughput while strictly respecting all spatial capacities.
"""

from collections import deque
from map_data import MapData
from typing import Any


class InvalidMoveError(Exception):
    """Exception raised for invalid multi-agent path movements."""

    pass


class CapacityExceededError(Exception):
    """Exception raised when network limits are breached during flow."""

    pass


class Pathfinder:
    """Computes conflict-free routing schedules using network flow."""

    def __init__(self, map_data: MapData) -> None:
        """Initializes the pathfinder with the structural map configuration.

        Args:
            map_data: The parsed map network details.
        """
        self.map_data = map_data
        self.residual_graph: dict[str, dict[str, int]] = {}
        self.schedule: dict[int, dict[int, str]] = {}

    def _add_edge(self, u: str, v: str, capacity: int) -> None:
        """Adds a directed edge and its backward counterpart to the graph.

        Args:
            u: The source node name string.
            v: The destination node name string.
            capacity: The structural capability limit of the link.
        """
        if u not in self.residual_graph:
            self.residual_graph[u] = {}
        if v not in self.residual_graph:
            self.residual_graph[v] = {}
        self.residual_graph[u][v] = capacity
        if u not in self.residual_graph[v]:
            self.residual_graph[v][u] = 0

    def build_network(self, max_time: int) -> None:
        """Constructs the time-expanded graph layers up to max_time.

        Args:
            max_time: The maximum length of the time horizons.
        """
        self.residual_graph.clear()
        inf_capacity = self.map_data.nb_drones

        for t in range(max_time + 1):
            for zone_name, zone in self.map_data.zones.items():
                in_node = f"{zone_name}_t{t}_in"
                out_node = f"{zone_name}_t{t}_out"

                is_special = zone_name in (
                    self.map_data.start_hub.name,
                    self.map_data.end_hub.name,
                )
                capacity = inf_capacity if is_special else zone.max_drones
                self._add_edge(in_node, out_node, capacity)

                if t < max_time:
                    next_in = f"{zone_name}_t{t+1}_in"
                    self._add_edge(out_node, next_in, capacity)

            for u_name, edges in self.map_data.graph.items():
                for v_name, connection in edges:
                    v_zone = self.map_data.zones[v_name]
                    if v_zone.zone_type == "blocked":
                        continue

                    cost = 2 if v_zone.zone_type == "restricted" else 1

                    if t + cost <= max_time:
                        out_node = f"{u_name}_t{t}_out"
                        in_node = f"{v_name}_t{t+cost}_in"
                        self._add_edge(
                            out_node, in_node, connection.max_link_capacity
                        )

    def _bfs(self, src: str, sink: str, parent: dict[str, str]) -> bool:
        """Performs a Breadth-First Search to find an augmenting flow path.

        Args:
            src: The overall virtual network source point.
            sink: The final destination sink node.
            parent: A tracing storage to reconstruct the path sequence.

        Returns:
            True if an augmenting route is successfully reached, else False.
        """
        visited = {src}
        queue = deque([src])

        while queue:
            u = queue.popleft()
            for v, cap in self.residual_graph[u].items():
                if v not in visited and cap > 0:
                    parent[v] = u
                    if v == sink:
                        return True
                    visited.add(v)
                    queue.append(v)
        return False

    def edmonds_karp(self, src: str, sink: str) -> int:
        """Calculates the maximum possible flow from source to sink.

        Args:
            src: The dynamic virtual source node name.
            sink: The dynamic virtual target sink node name.

        Returns:
            The optimized total flow volume successfully routed.
        """
        max_flow = 0
        parent: dict[str, str] = {}

        while self._bfs(src, sink, parent):
            path_flow = float("inf")
            v = sink
            while v != src:
                u = parent[v]
                path_flow = min(path_flow, self.residual_graph[u][v])
                v = parent[v]

            v = sink
            while v != src:
                u = parent[v]
                self.residual_graph[u][v] -= int(path_flow)
                self.residual_graph[v][u] += int(path_flow)
                v = parent[v]

            max_flow += int(path_flow)
            parent.clear()

        return max_flow

    def solve(self) -> dict[int, dict[int, str]]:
        """Identifies the optimal turn horizon and recovers the routing paths.

        Returns:
            The complete multi-agent scheduling dictionary.
        """
        nb_drones = self.map_data.nb_drones
        start_name = self.map_data.start_hub.name
        end_name = self.map_data.end_hub.name

        total_turns = 1
        max_limit = 200
        while total_turns <= max_limit:
            self.build_network(total_turns)

            self._add_edge("SUPER_SRC", f"{start_name}_t0_in", nb_drones)
            for t in range(total_turns + 1):
                end_out = f"{end_name}_t{t}_out"
                self._add_edge(end_out, "SUPER_SINK", nb_drones)

            flow = self.edmonds_karp("SUPER_SRC", "SUPER_SINK")
            if flow == nb_drones:
                break
            total_turns += 1
        else:
            import sys
            print(
                "Error: Spatial graph is disconnected or end_hub is unreachable.",
                file=sys.stderr
            )
            sys.exit(1)

        flow_graph: dict[str, dict[str, int]] = {}
        for u in self.residual_graph:
            flow_graph[u] = {}
            for v in self.residual_graph[u]:
                if self.residual_graph[v].get(u, 0) > 0:
                    flow_graph[u][v] = self.residual_graph[v][u]

        for drone_id in range(1, nb_drones + 1):
            t = 0
            curr_zone = start_name
            while curr_zone != end_name:
                out_node = f"{curr_zone}_t{t}_out"
                next_node = ""
                if out_node in flow_graph:
                    for nxt, f in flow_graph[out_node].items():
                        if f > 0:
                            next_node = nxt
                            break
                if not next_node:
                    break

                flow_graph[out_node][next_node] -= 1
                clean = next_node.replace("_in", "").replace("_out", "")
                next_zone, t_str = clean.rsplit("_t", 1)
                next_t = int(t_str)

                sim_turn = t + 1
                if sim_turn not in self.schedule:
                    self.schedule[sim_turn] = {}

                if next_zone != curr_zone:
                    cost = next_t - t
                    if cost == 1:
                        self.schedule[sim_turn][drone_id] = next_zone
                    elif cost == 2:
                        self.schedule[sim_turn][drone_id] = (
                            f"{curr_zone}-{next_zone}"
                        )
                        next_turn = sim_turn + 1
                        if next_turn not in self.schedule:
                            self.schedule[next_turn] = {}
                        self.schedule[next_turn][drone_id] = next_zone

                t = next_t
                curr_zone = next_zone

        return self.schedule

    def compute_moves(self, simulator: Any) -> dict[int, str]:
        """Fetches the precomputed movement set for the specific active turn.

        Args:
            simulator: The simulator instance providing the active turn index.

        Returns:
            A sub-dictionary outlining operations for the target turn.
        """
        if not self.schedule:
            self.solve()
        return self.schedule.get(simulator.current_turn, {})
