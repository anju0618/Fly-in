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
        total_turns = (max(pathfinder.schedule.keys())
                       if pathfinder.schedule else 0)

        if "--3D" in sys.argv:
            from visualizer_3D import Visualizer as Visualizer3D
            vis3d = Visualizer3D(map_data, pathfinder.schedule, total_turns)
            vis3d.start()
        elif "--2D" in sys.argv:
            from visualizer_2D import Visualizer as Visualizer2D
            vis2d = Visualizer2D(map_data, pathfinder.schedule, total_turns)
            vis2d.start()

    except Exception as e:
        print(f"Error during simulation: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
