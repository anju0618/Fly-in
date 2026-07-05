#!/usr/bin/env python3
"""Graphical visualizer module for the drone simulation using Tkinter.

This module renders the network topology and handles step-by-step 2D fleet
telemetry updates using optimized caching to ensure ultra-fast rendering.
"""

import math
import tkinter as tk
from typing import Any
from color_palette import ColorPalette


class Visualizer:
    """Manages the Tkinter GUI lifecycle and snappy O(1) animation updates."""

    def __init__(
        self,
        map_data: Any,
        schedule: dict[int, dict[int, str]],
        total_turns: int
    ) -> None:
        """Initializes the visualizer window and caches the structural layout.

        Args:
            map_data: The parsed configuration of the map network.
            schedule: Precomputed turn-by-turn routing movements.
            total_turns: The ultimate maximum turn horizon reached.
        """
        self.map_data = map_data
        self.schedule = schedule
        self.total_turns = total_turns
        self.current_turn = 0

        self.node_radius = 22
        self.padding = 60
        self.range_x = 1.0
        self.range_y = 1.0
        self.min_x = 0.0
        self.min_y = 0.0

        self.drone_history: dict[int, dict[int, tuple[str, float, float]]] = {}
        self._precompute_all_positions()
        self.root = tk.Tk()
        self.root.title("Fly_in - 2D Fleet Telemetry Visualizer")
        self.root.geometry("1000x750")
        self.root.configure(bg="#1e1e2e")

        self.canvas = tk.Canvas(self.root, bg="#1e1e2e", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        self.control_frame = tk.Frame(self.root, bg="#252538", height=50)
        self.control_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.btn_prev = tk.Button(
            self.control_frame, text="◀ Prev Turn", command=self.prev_turn,
            bg="#f38ba8", fg="black", font=("Helvetica", 10, "bold"), padx=10
        )
        self.btn_prev.pack(side=tk.LEFT, padx=20, pady=10)

        self.btn_next = tk.Button(
            self.control_frame, text="Next Turn ▶", command=self.next_turn,
            bg="#89b4fa", fg="black", font=("Helvetica", 10, "bold"), padx=10
        )
        self.btn_next.pack(side=tk.LEFT, padx=10, pady=10)

        self.lbl_status = tk.Label(
            self.control_frame,
            text=f"Turn: 0 / {self.total_turns} (Initialization)",
            bg="#252538", fg="#cdd6f4", font=("Helvetica", 12, "bold")
        )
        self.lbl_status.pack(side=tk.RIGHT, padx=20, pady=10)

        self._calculate_bounds()
        self.root.update_idletasks()
        self._draw_static_map()

    def _calculate_bounds(self) -> None:
        """Determines scaling factors based on maximum map coordinates."""
        xs = [z.x for z in self.map_data.zones.values()]
        ys = [z.y for z in self.map_data.zones.values()]
        min_x, max_x = min(xs) if xs else 0, max(xs) if xs else 10
        min_y, max_y = min(ys) if ys else 0, max(ys) if ys else 10
        self.range_x = float(max_x - min_x if max_x != min_x else 1)
        self.range_y = float(max_y - min_y if max_y != min_y else 1)
        self.min_x, self.min_y = float(min_x), float(min_y)

    def _get_zone_pixel_coords(self, zone_name: str) -> tuple[float, float]:
        """Translates raw zone coordinates into canvas pixel space."""
        zone = self.map_data.zones[zone_name]
        w = max(self.canvas.winfo_width(), 1000)
        h = max(self.canvas.winfo_height(), 700)

        scale_x = (w - 2 * self.padding) / self.range_x
        scale_y = (h - 2 * self.padding) / self.range_y

        pixel_x = self.padding + (zone.x - self.min_x) * scale_x
        if self.range_y == 1.0:
            pixel_y = h / 2.0
        else:
            pixel_y = self.padding + (zone.y - self.min_y) * scale_y

        return pixel_x, pixel_y

    def _precompute_all_positions(self) -> None:
        """Pre-calculates grid locations for all turns to achieve O(1)
        rendering loops."""
        start_name = self.map_data.start_hub.name

        self.drone_history[0] = {}
        for d_id in range(1, self.map_data.nb_drones + 1):
            self.drone_history[0][d_id] = (start_name, 0.0, 0.0)

        current_locs = {
            d_id: start_name
            for d_id in range(1, self.map_data.nb_drones + 1)
        }

        for t in range(1, self.total_turns + 1):
            self.drone_history[t] = {}
            turn_moves = self.schedule.get(t, {})

            for d_id in range(1, self.map_data.nb_drones + 1):
                if d_id in turn_moves:
                    target = turn_moves[d_id]
                    if "-" in target:
                        u, v = target.split("-", 1)
                        self.drone_history[t][d_id] = (target, 0.0, 0.0)
                        current_locs[d_id] = v
                    else:
                        self.drone_history[t][d_id] = (target, 0.0, 0.0)
                        current_locs[d_id] = target
                else:
                    prev_loc = self.drone_history[t - 1][d_id][0]
                    if "-" in prev_loc:
                        self.drone_history[t][d_id] = (
                            current_locs[d_id], 0.0, 0.0
                        )
                    else:
                        self.drone_history[t][d_id] = (prev_loc, 0.0, 0.0)

    def _draw_static_map(self) -> None:
        """Draws static infrastructure (hubs and connection lines)
        exactly ONCE."""

        for u_name, edges in self.map_data.graph.items():
            u_x, u_y = self._get_zone_pixel_coords(u_name)
            for v_name, _ in edges:
                v_x, v_y = self._get_zone_pixel_coords(v_name)
                self.canvas.create_line(
                    u_x, u_y, v_x, v_y,
                    fill=ColorPalette.LINE_COLOR,
                    width=2
                )

        for name, zone in self.map_data.zones.items():
            cx, cy = self._get_zone_pixel_coords(name)
            r = self.node_radius
            meta_color = zone.colour or ""
            color_hex = ColorPalette.get_hex(meta_color, ColorPalette.DEFAULT)

            if name == self.map_data.start_hub.name:
                color_hex = ColorPalette.GREEN

            elif name == self.map_data.end_hub.name:
                color_hex = ColorPalette.ORANGE

            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=color_hex, outline=ColorPalette.TEXT_LIGHT, width=2
            )

            cap_str = (
                f"\n(max:{zone.max_drones})"
                if zone.max_drones < 100 else ""
            )

            dark_colors = (
                ColorPalette.DEFAULT,
                ColorPalette.BLACK,
                ColorPalette.DARKRED,
                ColorPalette.DARKBLUE,
                ColorPalette.DARKGREEN
            )
            is_dark = color_hex in dark_colors

            text_color = (
                ColorPalette.TEXT_LIGHT
                if is_dark else ColorPalette.TEXT_DARK
            )

            self.canvas.create_text(
                cx, cy, text=f"{name}{cap_str}",
                fill=text_color, font=("Helvetica", 8, "bold")
            )

    def update_dynamic_entities(self) -> None:
        """Clears and repaints only the volatile dynamic drone markers
        using tags."""
        self.canvas.delete("dynamic_drone")

        cluster_counts: dict[str, list[int]] = {}
        active_turn_data = self.drone_history[self.current_turn]

        for d_id, (loc_str, _, _) in active_turn_data.items():
            cluster_counts.setdefault(loc_str, []).append(d_id)

        for loc_str, drones in cluster_counts.items():
            if "-" in loc_str:
                u, v = loc_str.split("-", 1)
                ux, uy = self._get_zone_pixel_coords(u)
                vx, vy = self._get_zone_pixel_coords(v)
                zx, zy = (ux + vx) / 2.0, (uy + vy) / 2.0
            else:
                zx, zy = self._get_zone_pixel_coords(loc_str)

            num_drones = len(drones)
            for idx, d_id in enumerate(drones):
                offset_r = 30 if num_drones > 1 else 0
                if num_drones > 0:
                    angle = idx * (2 * math.pi / num_drones)
                else:
                    angle = 0.0

                dx = zx + offset_r * math.cos(angle)
                dy = zy + offset_r * math.sin(angle)

                dr = 10
                self.canvas.create_oval(
                    dx - dr, dy - dr, dx + dr, dy + dr,
                    fill="#b4befe",
                    outline="#ffffff",
                    width=1.5,
                    tags="dynamic_drone"
                )
                self.canvas.create_text(
                    dx, dy, text=f"D{d_id}",
                    fill="#11111b",
                    font=("Helvetica", 8, "bold"),
                    tags="dynamic_drone"
                )

    def next_turn(self) -> None:
        """Advances the 2D frame animation by one step."""
        if self.current_turn < self.total_turns:
            self.current_turn += 1
            new_text = f"Turn: {self.current_turn} / {self.total_turns}"
            self.lbl_status.config(text=new_text)
            self.update_dynamic_entities()

    def prev_turn(self) -> None:
        """Reverts the 2D frame animation to the previous step."""
        if self.current_turn > 0:
            self.current_turn -= 1
            new_text = f"Turn: {self.current_turn} / {self.total_turns}"
            self.lbl_status.config(text=new_text)
            self.update_dynamic_entities()

    def start(self) -> None:
        """Launches the core blocking Tkinter desktop mainloop execution."""
        self.update_dynamic_entities()
        self.root.mainloop()
