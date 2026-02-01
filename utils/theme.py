"""
和 wa · harmony
Japanese minimalist theme for Nautilus.
Philosophy: Ma (negative space), Kanso (simplicity), Shibui (subtle beauty).

Palette inspired by:
- Sumi-e ink wash painting (墨絵)
- Washi paper texture (和紙) 
- Indigo dye tradition (藍染)
- Zen temple aesthetics (禅)
"""
from rich import box

# ━━━ Core Palette ━━━
# Ma (間) - the void, negative space
INK = "grey70"              # 墨 Primary text - soft charcoal
MIST = "grey50"             # 霧 Secondary text - morning mist  
SHADOW = "grey35"           # 影 Subtle elements - bamboo shadow
VOID = "grey23"             # 間 Background accents - deep void

# Accent colors - restrained, natural
INDIGO = "#5c6bc0"          # 藍 Indigo - traditional Japanese dye
SAKURA = "#e8b4b8"          # 桜 Pale cherry blossom (success)
VERMILLION = "#d45d49"      # 朱 Subdued red (error)
AMBER = "#d4a849"           # 琥珀 Warm amber (warning)
SNOW = "white"              # 雪 Pure white (highlights)

# ━━━ Semantic Colors ━━━
TEXT = INK                  # Primary text
TEXT_DIM = MIST            # Secondary text
ACCENT = INDIGO            # Interactive elements
ACCENT_DIM = "#7986cb"     # Lighter indigo
MUTED = SHADOW             # Borders, dividers
SUCCESS = SAKURA           # Success states
ERROR = VERMILLION         # Error states  
WARN = AMBER               # Warning states
HIGHLIGHT = SNOW           # Selection, focus

# ━━━ Box Styles - 枠 waku ━━━
# Minimal borders reflecting shoji screen aesthetics
BANNER_BOX = box.SIMPLE         # Clean lines for hero
CARD_BOX = box.SIMPLE           # Uniform simplicity
LIST_BOX = box.SIMPLE_HEAD      # Subtle header separation
PANEL_BOX = box.SIMPLE          # Consistent simplicity

# ━━━ Symbols - 記号 kigō ━━━
# Using subtle geometric shapes instead of bold glyphs
BULLET = "◦"               # Hollow circle - restraint
SEPARATOR = "·"            # Middle dot - gentle division
ARROW = "→"                # Simple arrow - direction
PREFIX = "  "              # Two spaces - breathing room

# ━━━ Typography Spacing ━━━
# Generous ma (negative space) for clarity
PADDING_COMPACT = (0, 2)   # Minimal vertical, comfortable horizontal
PADDING_DEFAULT = (1, 3)   # Balanced breathing room
PADDING_GENEROUS = (2, 4)  # Spacious, zen-like

# ━━━ Legacy Support ━━━
# Keeping old names for compatibility
PANEL_BORDER = MUTED
TITLE = f"[{TEXT}]"
SUBTITLE = f"[{TEXT_DIM}]"
