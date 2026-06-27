#!/usr/bin/env python3
"""Module for parsing map files for the drone simulation."""

from typing import Optional
from connection import Connection
from map_data import MapData
from zone import Zone, ZoneType


class MapParser:
    """Parser to read and validate drone simulation map files."""

    def __init__(self, file_path: str) -> None:
        """Initializes the parser with a file path.

        Args:
            file_path: The path to the map text file.
        """
        self.file_path = file_path
        self.nb_drones: int = 0
        self.start_hub: Optional[Zone] = None
        self.end_hub: Optional[Zone] = None
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.seen_connections: set[tuple[str, str]] = set()

    def parse(self) -> MapData:
        """Parses the map file and returns a complete MapData object."""
        with open(self.file_path, "r") as file:
            for line_num, line in enumerate(file, 1):
                stripped = line.strip()

                if not stripped or stripped.startswith("#"):
                    continue

                main_content, metadata = self._extract_metadata(stripped)

                if ":" not in main_content:
                    raise ValueError(
                        f"Line {line_num}: Invalid format, missing ':'."
                    )
                prefix, data = main_content.split(":", 1)
                prefix = prefix.strip()
                data = data.strip()

                if self.nb_drones == 0:
                    if prefix != "nb_drones":
                        raise ValueError(
                            f"Line {line_num}: The first defined property "
                            f"must be 'nb_drones'."
                        )
                    self._parse_nb_drones(data, line_num)
                    continue

                if prefix in ("hub", "start_hub", "end_hub"):
                    self._parse_zone(prefix, data, metadata, line_num)
                elif prefix == "connection":
                    self._parse_connection(data, metadata, line_num)
                else:
                    raise ValueError(
                        f"Line {line_num}: Unknown property prefix '{prefix}'."
                    )

        if not self.start_hub or not self.end_hub:
            raise ValueError("Map is missing a unique start_hub or end_hub.")

        return MapData(
            nb_drones=self.nb_drones,
            start_hub=self.start_hub,
            end_hub=self.end_hub,
            zones=self.zones,
            connections=self.connections,
        )

    def _parse_nb_drones(self, data: str, line_num: int) -> None:
        """Parses and validates the number of drones."""
        try:
            count = int(data)
            if count <= 0:
                raise ValueError()
            self.nb_drones = count
        except ValueError:
            raise ValueError(
                f"Line {line_num}: 'nb_drones' must be a positive integer."
            )

    def _parse_zone(
            self, prefix: str,
            data: str,
            metadata: dict[str, str],
            line_num: int
    ) -> None:
        """Parses and validates a zone (hub, start_hub, or end_hub)."""
        parts = data.split()
        if len(parts) != 3:
            raise ValueError(
                f"Line {line_num}: Zone definition must have name, x, and y."
            )
        name, raw_x, raw_y = parts

        if "-" in name:
            raise ValueError(
                f"Line {line_num}: Zone name '{name}' cannot contain dashes."
            )
        if name in self.zones:
            raise ValueError(
                f"Line {line_num}: Zone name '{name}' is already defined."
            )

        try:
            x = int(raw_x)
            y = int(raw_y)
        except ValueError:
            raise ValueError(
                f"Line {line_num}: Coordinates must be integers."
            )

        zone_type = ZoneType.NORMAL
        if "zone" in metadata:
            try:
                zone_type = ZoneType(metadata["zone"])
            except ValueError:
                raise ValueError(
                    f"Line {line_num}: Invalid zone type '{metadata['zone']}'."
                )

        max_drones = 1
        if "max_drones" in metadata:
            try:
                max_drones = int(metadata["max_drones"])
                if max_drones <= 0:
                    raise ValueError()
            except ValueError:
                raise ValueError(
                    f"Line {line_num}: 'max_drones' "
                    f"must be a positive integer."
                )

        colour = metadata.get("colour", metadata.get("color"))
        zone = Zone(
            name=name,
            x=x,
            y=y,
            zone_type=zone_type,
            max_drones=max_drones,
            colour=colour,
        )

        if prefix == "start_hub":
            if self.start_hub is not None:
                raise ValueError(f"Line {line_num}: Multiple "
                                 f"start_hubs defined.")
            self.start_hub = zone
        elif prefix == "end_hub":
            if self.end_hub is not None:
                raise ValueError(f"Line {line_num}: Multiple "
                                 f"end_hubs defined.")
            self.end_hub = zone

        self.zones[name] = zone

    def _parse_connection(
        self, data: str, metadata: dict[str, str], line_num: int
    ) -> None:
        """Parses and validates a bidirectional connection between zones."""
        if "-" not in data:
            raise ValueError(
                f"Line {line_num}: Connection missing dash separator."
            )

        parts = data.split("-")
        if len(parts) != 2:
            raise ValueError(
                f"Line {line_num}: Invalid connection format '{data}'."
            )

        zone1, zone2 = parts[0].strip(), parts[1].strip()

        if zone1 not in self.zones or zone2 not in self.zones:
            raise ValueError(
                f"Line {line_num}: Connection refers to undefined zones "
                f"('{zone1}' or '{zone2}')."
            )

        sorted_pair = tuple(sorted([zone1, zone2]))
        connection_pair = (str(sorted_pair[0]), str(sorted_pair[1]))
        if connection_pair in self.seen_connections:
            raise ValueError(
                f"Line {line_num}: Duplicate connection between "
                f"'{zone1}' and '{zone2}' detected."
            )

        max_link_capacity = 1
        if "max_link_capacity" in metadata:
            try:
                max_link_capacity = int(metadata["max_link_capacity"])
                if max_link_capacity <= 0:
                    raise ValueError()
            except ValueError:
                raise ValueError(
                    f"Line {line_num}: 'max_link_capacity' must be "
                    f"a positive integer."
                )

        self.connections.append(
            Connection(
                zone1=zone1,
                zone2=zone2,
                max_link_capacity=max_link_capacity,
            )
        )
        self.seen_connections.add(connection_pair)

    def _extract_metadata(self, line: str) -> tuple[str, dict[str, str]]:
        """Extracts and parses metadata enclosed in brackets from a line."""

        start_idx = line.find("[")
        end_idx = line.find("]")

        if start_idx == -1 and end_idx == -1:
            return line.strip(), {}

        if start_idx == -1 or end_idx == -1 or start_idx > end_idx:
            raise ValueError("Malformed metadata brackets encountered")

        metadata_content = line[start_idx + 1: end_idx].strip()
        main_content = (line[:start_idx] + line[end_idx + 1:]).strip()

        metadata_dict: dict[str, str] = {}
        if metadata_content:
            items = metadata_content.split()
            for item in items:
                if "=" not in item:
                    raise ValueError(f"Invalid metadata format: '{item}'")

                key, value = item.split("=", 1)
                metadata_dict[key.strip()] = value.strip()

        return main_content, metadata_dict
