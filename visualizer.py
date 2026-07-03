#!/usr/bin/env python3
"""Graphical visualizer module for the drone simulation using Tkinter.

This module renders the network topology, zone features, and provides
interactive controls to step through or autoplay the drone fleet routing.
"""

import math
import tkinter as tk
from typing import Any, Dict, List, Tuple


class Visualizer:
    """Manages the Tkinter GUI lifecycle and animation of the simulation."""

    def __init__(
        self,
        map_data: Any,
        schedule: Dict[int, Dict[int, str]],
        total_turns: int
    ) -> None:
        """Initializes the visualizer window and structural layout elements.

        Args:
            map_data: The parsed configuration of the map network.
            schedule: Precomputed turn-by-turn routing movements.
            total_turns: The ultimate maximum turn horizon reached.
        """
        self.map_data = map_data
        self.schedule = schedule
        self.total_turns = total_turns
        self.current_turn = 0
        self.range_x = 1.0
        self.range_y = 1.0
        self.min_x = 0.0
        self.min_y = 0.0

        self.drone_positions: Dict[int, str] = {}
        for i in range(1, map_data.nb_drones + 1):
            self.drone_positions[i] = map_data.start_hub.name

        self.root = tk.Tk()
        self.root.title("Fly_in - Fleet Telemetry Visualizer")
        self.root.geometry("1000x750")

        self.canvas = tk.Canvas(self.root, bg="#1e1e2e", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        self.control_frame = tk.Frame(self.root, bg="#252538", height=50)
        self.control_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.btn_next = tk.Button(
            self.control_frame,
            text="Next Turn",
            command=self.next_turn,
            bg="#89b4fa",
            fg="black",
        )
        self.btn_next.pack(side=tk.LEFT, padx=20, pady=10)

        self.btn_prev = tk.Button(
            self.control_frame,
            text="Prev Turn",
            command=self.prev_turn,
            bg="#f38ba8",
            fg="black",
        )
        self.btn_prev.pack(side=tk.LEFT, padx=10, pady=10)

        self.lbl_status = tk.Label(
            self.control_frame,
            text=f"Turn: 0 / {self.total_turns} (Initialization)",
            bg="#252538",
            fg="#cdd6f4",
            font=("Helvetica", 12, "bold"),
        )
        self.lbl_status.pack(side=tk.RIGHT, padx=20, pady=10)

        self.is_playing = False
        self.node_radius = 22
        self.padding = 60
        self._calculate_bounds()

    def _calculate_bounds(self) -> None:
        """Determines scaling factors based on maximum map coordinates."""
        xs = [z.x for z in self.map_data.zones.values()]
        ys = [z.y for z in self.map_data.zones.values()]

        min_x = min(xs) if xs else 0
        max_x = max(xs) if xs else 10
        min_y = min(ys) if ys else 0
        max_y = max(ys) if ys else 10

        self.range_x = float(max_x - min_x if max_x != min_x else 1)
        self.range_y = float(max_y - min_y if max_y != min_y else 1)
        self.min_x = float(min_x)
        self.min_y = float(min_y)

    def _get_coords(self, zone_name: str) -> Tuple[float, float]:
        """Translates raw zone coordinates into canvas pixel space.

        Args:
            zone_name: The identifier name of the targeted infrastructure.

        Returns:
            A coordinate float tuple representing center pixel locations.
        """
        if "-" in zone_name:
            u_name, v_name = zone_name.split("-", 1)
            u_x, u_y = self._get_coords(u_name)
            v_x, v_y = self._get_coords(v_name)
            return (u_x + v_x) / 2, (u_y + v_y) / 2

        zone = self.map_data.zones[zone_name]
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        if w <= 1:
            w = 1000
        if h <= 1:
            h = 700

        scale_x = (w - 2 * self.padding) / self.range_x
        scale_y = (h - 2 * self.padding) / self.range_y

        pixel_x = self.padding + (zone.x - self.min_x) * scale_x
        if self.range_y == 1.0:
            pixel_y = h / 2
        else:
            pixel_y = self.padding + (zone.y - self.min_y) * scale_y

        return pixel_x, pixel_y

    def refresh_view(self) -> None:
        """Clears and re-draws the current network state and drone fleet."""
        self.canvas.delete("all")

        for u_name, edges in self.map_data.graph.items():
            u_x, u_y = self._get_coords(u_name)
            for v_name, _ in edges:
                v_x, v_y = self._get_coords(v_name)
                self.canvas.create_line(
                    u_x, u_y, v_x, v_y, fill="#585b70", width=2
                )

        for name, zone in self.map_data.zones.items():
            cx, cy = self._get_coords(name)
            r = self.node_radius

            color_hex = "#45475a"
            meta_color = getattr(zone, "color", "").lower()
            if meta_color == "green":
                color_hex = "#a6e3a1"
            elif meta_color == "red":
                color_hex = "#f38ba8"
            elif meta_color == "blue":
                color_hex = "#89b4fa"
            elif meta_color == "yellow":
                color_hex = "#f9e2af"
            elif meta_color == "gray":
                color_hex = "#7f849c"

            if name == self.map_data.start_hub.name:
                color_hex = "#a6e3a1"
            elif name == self.map_data.end_hub.name:
                color_hex = "#f9e2af"

            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=color_hex, outline="#cdd6f4", width=2
            )

            cap_str = ""
            if zone.max_drones < 100:
                cap_str = f"\n(max:{zone.max_drones})"

            is_dark = color_hex != "#45475a"
            text_color = "#11111b" if is_dark else "#cdd6f4"
            self.canvas.create_text(
                cx, cy - 35,
                text=f"{name}{cap_str}",
                fill=text_color,
                font=("Helvetica", 9, "bold"),
            )

        zone_clusters: Dict[str, List[int]] = {}
        for d_id, z_name in self.drone_positions.items():
            zone_clusters.setdefault(z_name, []).append(d_id)

        for z_name, drones in zone_clusters.items():
            zx, zy = self._get_coords(z_name)
            num_drones = len(drones)

            for idx, d_id in enumerate(drones):
                offset_r = 32 if num_drones > 1 else 0
                angle = 0.0
                if num_drones > 0:
                    angle = idx * (2 * math.pi / num_drones)
                dx = zx + offset_r * math.cos(angle)
                dy = zy + offset_r * math.sin(angle)

                dr = 10
                self.canvas.create_oval(
                    dx - dr, dy - dr, dx + dr, dy + dr,
                    fill="#fab387", outline="#ffffff", width=1.5
                )
                self.canvas.create_text(
                    dx, dy,
                    text=f"D{d_id}",
                    fill="#11111b",
                    font=("Helvetica", 8, "bold"),
                )

    def next_turn(self) -> None:
        """Advances the simulation state by one incremental step."""
        if self.current_turn >= self.total_turns:
            self.is_playing = False
            return

        self.current_turn += 1
        turn_moves = self.schedule.get(self.current_turn, {})

        for d_id, target_zone in turn_moves.items():
            self.drone_positions[d_id] = target_zone

        self.lbl_status.config(
            text=f"Turn: {self.current_turn} / {self.total_turns}"
        )
        self.refresh_view()

    def prev_turn(self) -> None:
        """Reverts the simulation state to the previous turn."""
        if self.current_turn <= 0:
            return
        self.current_turn -= 1
        for i in range(1, self.map_data.nb_drones + 1):
            self.drone_positions[i] = self.map_data.start_hub.name

        # 2. current_turn までスケジュールを適用して進める
        for t in range(1, self.current_turn + 1):
            turn_moves = self.schedule.get(t, {})
            for d_id, target_zone in turn_moves.items():
                self.drone_positions[d_id] = target_zone

        # 表示を更新
        self.lbl_status.config(
            text=f"Turn: {self.current_turn} / {self.total_turns}"
        )
        self.refresh_view()

    def start(self) -> None:
        """Starts the main blocking visual GUI thread window loop."""
        self.root.after(200, self.refresh_view)
        self.root.mainloop()
