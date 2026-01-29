"""
Japanese minimalist theme for Nautilus.
Sumi ink, washi paper, subtle indigo accent — clean and professional.
"""
# Rich markup-safe palette (no brackets in values; use as style names or in .print(style, text))
INK = "dim white"          # Primary text (sumi)
PAPER = "dim white"        # Muted secondary
ACCENT = "bright_black"    # Indigo/navy feel
BORDER = "dim bright_black"
SUCCESS = "dim green"
ERROR = "dim red"
WARN = "dim yellow"
HIGHLIGHT = "white"        # Numbers / selection

# Style tags for use in markup strings (escape user content)
TITLE = "[bold dim white]"
SUBTITLE = "[dim bright_black]"
LABEL = "[dim white]"
ACCENT_TAG = "[bright_black]"
SUCCESS_TAG = "[dim green]"
ERROR_TAG = "[dim red]"
WARN_TAG = "[dim yellow]"
RESET = "[/]"

# Panel
PANEL_BORDER = "bright_black"
PANEL_TITLE = "[bold dim white]"
PANEL_SUBTITLE = "[dim bright_black]"

# Table
TABLE_BORDER = "bright_black"
TABLE_TITLE = "[dim white]"
TABLE_HEADER = "[dim bright_black]"
TABLE_ROW_ID = "bright_black"
TABLE_ROW_DIM = "dim white"
