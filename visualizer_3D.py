#!/usr/bin/env python3
"""Highly optimized 3D Spatial Map Canvas Layout Engine powered by Matplotlib.

This module renders the network map as a true 3D spatial canvas (X, Y, Z).
It utilizes low-level artist property shifts (_offsets3d) to bypass heavy
re-drawing cycles, ensuring smooth turn-by-step navigation.
"""

import matplotlib.pyplot as plt
from typing import Any


class Visualizer:
    """True 3D Map Visualizer with optimized dynamic rendering paths."""

    def __init__(
        self,
        map_data: Any,
        schedule: dict[int, dict[int, str]],
        total_turns: int
    ) -> None:
        """Initializes the 3D map dimensions and precomputes timelines."""
        self.map_data = map_data
        self.schedule = schedule
        self.total_turns = max(schedule.keys()) if schedule else total_turns
        self.current_turn = 0

        # マップ上の同一(x, y)座標のハブをZ軸（高さ）方向に自動スタック化
        self.zone_z: dict[str, float] = {}
        coord_counts: dict[tuple[int, int], int] = {}
        for name, zone in self.map_data.zones.items():
            xy = (zone.x, zone.y)
            count = coord_counts.get(xy, 0)
            self.zone_z[name] = float(count)
            coord_counts[xy] = count + 1

        # 全ターンのドローン座標を事前にキャッシュ
        self.drone_positions: dict[
            int, dict[int, tuple[float, float, float]]
        ] = {}
        self._precompute_positions()

        # 動的描画コンポーネントの参照保持用
        self.drone_scat: Any = None
        self.drone_labels: list[Any] = []
        self.fig: Any = None
        self.ax: Any = None

    def _precompute_positions(self) -> None:
        """Pre-allocates float coordinates for all drones across all turns."""
        start_zone = self.map_data.start_hub
        for t in range(self.total_turns + 1):
            self.drone_positions[t] = {}

        for d_id in range(1, self.map_data.nb_drones + 1):
            self.drone_positions[0][d_id] = (
                float(start_zone.x),
                float(start_zone.y),
                self.zone_z[start_zone.name]
            )
            curr_name = start_zone.name

            for t in range(1, self.total_turns + 1):
                movements = self.schedule.get(t, {})
                if d_id in movements:
                    z_str = movements[d_id]
                    if "-" in z_str:
                        src, dest = z_str.split("-")
                        sz = self.map_data.zones[src]
                        dz = self.map_data.zones[dest]
                        self.drone_positions[t][d_id] = (
                            (sz.x + dz.x) / 2.0,
                            (sz.y + dz.y) / 2.0,
                            (self.zone_z[src] + self.zone_z[dest]) / 2.0
                        )
                        curr_name = dest
                    else:
                        z = self.map_data.zones[z_str]
                        self.drone_positions[t][d_id] = (
                            float(z.x), float(z.y), self.zone_z[z_str]
                        )
                        curr_name = z_str
                else:
                    px, py, pz = self.drone_positions[t - 1][d_id]
                    if t > 1 and "-" in self.schedule.get(
                        t - 1,
                        {}
                        ).get(
                            d_id,
                            ""):
                        curr_z = self.map_data.zones[curr_name]
                        self.drone_positions[t][d_id] = (
                            float(curr_z.x),
                            float(curr_z.y),
                            self.zone_z[curr_name]
                        )
                    else:
                        self.drone_positions[t][d_id] = (px, py, pz)

    def _draw_static_map(self) -> None:
        """
        Draws static components (grid, guidelines, lines, hubs) exactly ONCE.
        """
        self.ax.set_facecolor("#1e1e2e")
        unique_coords = set((z.x, z.y) for z in self.map_data.zones.values())
        for cx, cy in unique_coords:
            max_z = max(
                self.zone_z[n] for n, z in self.map_data.zones.items()
                if z.x == cx and z.y == cy)
            if max_z > 0:
                self.ax.plot(
                    [cx, cx],
                    [cy, cy],
                    [0.0, max_z],
                    c="#89b4fa",
                    linestyle="--",
                    alpha=0.4
                    )

        for conn in self.map_data.connections:
            if (conn.zone1 in self.map_data.zones and
                    conn.zone2 in self.map_data.zones):
                z1 = self.map_data.zones[conn.zone1]
                z2 = self.map_data.zones[conn.zone2]

                self.ax.plot(
                    [z1.x, z2.x],
                    [z1.y, z2.y],
                    [self.zone_z[conn.zone1], self.zone_z[conn.zone2]],
                    c="#45475a",
                    alpha=0.6
                    )

        for name, zone in self.map_data.zones.items():
            color = zone.colour or (
                "green" if name == self.map_data.start_hub.name
                else "red" if name == self.map_data.end_hub.name
                else "gray"
                )
            try:
                self.ax.scatter(
                        [zone.x],
                        [zone.y],
                        [self.zone_z[name]],
                        c=color,
                        s=150,
                        edgecolors='white',
                        alpha=0.8
                        )
            except ValueError:
                self.ax.scatter(
                    [zone.x],
                    [zone.y],
                    [self.zone_z[name]],
                    c="gray",
                    s=150,
                    edgecolors='white',
                    alpha=0.8
                    )
            self.ax.text(
                zone.x,
                zone.y,
                self.zone_z[name] + 0.05,
                name,
                fontsize=8,
                color="#cdd6f4",
                ha='center'
                )

    def _update_drones(self) -> None:
        """
        Updates only dynamic elements using high-speed property mutations.
        """

        self.ax.set_title(
                    f"3D Map Telemetry Window — Turn {self.current_turn} "
                    f"/ {self.total_turns}",
                    color="#cdd6f4",
                    weight="bold"
                    )
        xs, ys, zs = [], [], []
        active_positions = self.drone_positions[self.current_turn]
        for d_id, (dx, dy, dz) in active_positions.items():
            xs.append(dx)
            ys.append(dy)
            zs.append(dz)

        # 🌟 劇的軽量化の肝：scatter全体の再描画をせず、内部の3D座標配列だけを差し替える
        self.drone_scat._offsets3d = (xs, ys, zs)

        # 古いドローン文字ラベルだけをピンポイントで消去して再配置
        for lbl in self.drone_labels:
            lbl.remove()
        self.drone_labels.clear()

        for d_id, (dx, dy, dz) in active_positions.items():
            lbl = self.ax.text(
                        dx,
                        dy,
                        dz + 0.03,
                        f"D{d_id}",
                        fontsize=9,
                        color="#f9e2af",
                        weight='bold',
                        ha='center'
                        )
            self.drone_labels.append(lbl)

    def start(self) -> None:
        """Launches the window layout and sets up interactive widget loops."""
        self.fig = plt.figure(figsize=(10, 8))
        self.fig.patch.set_facecolor("#1e1e2e")
        self.ax = self.fig.add_subplot(111, projection='3d')
        self._draw_static_map()

        self.drone_scat = self.ax.scatter(
                            [],
                            [],
                            [],
                            c="#fab387",
                            s=120,
                            marker='^',
                            edgecolors='black',
                            zorder=5)

        # 3. 操作ボタンの配置
        from matplotlib.widgets import Button
        ax_prev = self.fig.add_axes([0.3, 0.03, 0.15, 0.05])
        ax_next = self.fig.add_axes([0.55, 0.03, 0.15, 0.05])

        btn_prev = Button(
                    ax_prev,
                    '◀ Prev',
                    color='#252538',
                    hovercolor='#45475a'
                    )
        btn_next = Button(
                    ax_next,
                    'Next ▶',
                    color='#252538',
                    hovercolor='#45475a'
                    )
        btn_prev.label.set_color('#cdd6f4')
        btn_next.label.set_color('#cdd6f4')

        def update_next(event: Any) -> None:
            if self.current_turn < self.total_turns:
                self.current_turn += 1
                self._update_drones()
                self.fig.canvas.draw_idle()  # 必要最低限の差分バックバッファ更新

        def update_prev(event: Any) -> None:
            if self.current_turn > 0:
                self.current_turn -= 1
                self._update_drones()
                self.fig.canvas.draw_idle()

        btn_next.on_clicked(update_next)
        btn_prev.on_clicked(update_prev)
        self._update_drones()
        plt.show()
