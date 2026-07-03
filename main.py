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

        simulator.run(pathfinder, show_capacity="--capacity-info" in sys.argv)

        if pathfinder.schedule:
            from visualizer import Visualizer
            total_turns = max(pathfinder.schedule.keys())

            print("\n[Bonus] Launching Graphical "
                  "Fleet Telemetry Visualizer...")
            visualizer = Visualizer(map_data, pathfinder.schedule, total_turns)
            visualizer.start()

    except Exception as e:
        print(f"Error during simulation: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
