#!/usr/bin/env python3
from enum import Enum


class ColorPalette(str, Enum):
    """Enumeration of color names mapped to hex codes for UI consistency."""

    # 基本カラー
    DEFAULT = "#45475a"
    TEXT_LIGHT = "#cdd6f4"
    TEXT_DARK = "#11111b"
    LINE_COLOR = "#313244"

    # 標準カラー
    GREEN = "#a6e3a1"
    RED = "#f38ba8"
    BLUE = "#89b4fa"
    YELLOW = "#f9e2af"
    GRAY = "#7f849c"
    GREY = "#7f849c"
    CYAN = "#89dceb"
    MAGENTA = "#f5c2e7"
    ORANGE = "#fab387"
    PURPLE = "#cba6f7"
    WHITE = "#ffffff"
    BLACK = "#11111b"

    # 暗め
    DARKRED = "#900c3f"
    DARKBLUE = "#1e3a8a"
    DARKGREEN = "#14532d"
    DARKYELLOW = "#854d0e"
    DARKGRAY = "#374151"
    DARKGREY = "#374151"
    DARKPURPLE = "#581c87"

    # 明るめ
    LIGHTRED = "#fca5a5"
    LIGHTBLUE = "#93c5fd"
    LIGHTGREEN = "#86efac"
    LIGHTYELLOW = "#fef08a"
    LIGHTGRAY = "#e5e7eb"
    LIGHTGREY = "#e5e7eb"

    # その他
    PINK = "#f5bde6"
    BROWN = "#b57614"
    GOLD = "#f1c40f"
    SILVER = "#bdc3c7"
    NAVY = "#000080"
    TEAL = "#008080"
    OLIVE = "#808000"
    LIME = "#00ff00"

    @classmethod
    def get_hex(cls, color_name: str, default_hex: str = "#45475a") -> str:
        """Looks up a color name dynamically and returns its hex code.

        If the color name is not found in the enum, it attempts to return
        the raw string if it's already a valid hex, or falls back to default.
        """
        normalized = color_name.strip().upper()
        if hasattr(cls, normalized):
            return str(cls[normalized].value)

        if color_name.startswith("#") and len(color_name) in (4, 7):
            return color_name

        return default_hex
