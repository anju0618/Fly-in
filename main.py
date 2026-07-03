#!/usr/bin/env python3
"""
Main entry point for the drone routing simulation.
"""

import sys
from map_parser import MapParser
from simulator import Simulator
from pathfinder import Pathfinder


def main() -> None:
    """Initializes and runs the drone simulation based on input map."""
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <map_file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        parser = MapParser(file_path)
        map_data = parser.parse()

        simulator = Simulator(map_data)
        pathfinder = Pathfinder(map_data)

        simulator.run(pathfinder)

        """
        if pathfinder.schedule:
            from visualizer import Visualizer
            total_turns = max(pathfinder.schedule.keys())

            print("\n[Bonus] Launching Graphical "
                  "Fleet Telemetry Visualizer...")
            visualizer = Visualizer(map_data, pathfinder.schedule, total_turns)
            visualizer.start()
        """
        if "--capacity-info" in sys.argv and pathfinder.schedule:
            print("\n=== Capacity Usage Info ===")
            drone_current_zone = {
                d_id: map_data.start_hub.name
                for d_id in range(1, map_data.nb_drones + 1)
            }
            total_turns = max(pathfinder.schedule.keys())
            for turn in range(1, total_turns + 1):
                print(f"\n[Turn {turn} Summary]")
                zone_counts = {name: 0 for name in map_data.zones}
                conn_counts = {}
                for u in map_data.graph:
                    for v, conn in map_data.graph[u]:
                        conn_counts[f"{u}-{v}"] = 0
                turn_moves = pathfinder.schedule.get(turn, {})
                for d_id in range(1, map_data.nb_drones + 1):
                    prev_zone = drone_current_zone[d_id]
                    if d_id in turn_moves:
                        move = turn_moves[d_id]
                        if "-" in move:
                            conn_counts[move] += 1
                            drone_current_zone[d_id] = move.split("-")[1]
                        else:
                            if move != prev_zone:
                                c_name = f"{prev_zone}-{move}"
                                if c_name in conn_counts:
                                    conn_counts[c_name] += 1
                            zone_counts[move] += 1
                            drone_current_zone[d_id] = move
                    else:
                        zone_counts[prev_zone] += 1
                for z_name, zone in map_data.zones.items():
                    if z_name in (
                            map_data.start_hub.name, map_data.end_hub.name
                            ):
                        continue
                    current = zone_counts[z_name]
                    max_cap = zone.max_drones
                    print(f"Zone {z_name}: {current}/{max_cap} drones")
                for u in map_data.graph:
                    for v, conn in map_data.graph[u]:
                        c_name = f"{u}-{v}"
                        current = conn_counts[c_name]
                        max_cap = conn.max_link_capacity
                        print(f"Connection {c_name}: "
                              f"{current}/{max_cap} capacity used")
            print("===========================")

    except Exception as e:
        print(f"Error during simulation: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
