"""
深海 shinkai · the deep
Nautilus deep-ocean theme.

Palette drawn from the creature itself:
- Nacre (真珠層): Iridescent mother-of-pearl interior
- Abyssal zone (深淵): Lightless ocean depths
- Bioluminescence (生物発光): Cold living light
- Coral reef (珊瑚礁): Warm organic structure
"""
from rich import box

# ━━━ Core Palette — Abyssal Depth ━━━
# Layered greys inspired by ocean strata at depth
INK = "#c9d1d9"              # 真珠 Nacre — pearlescent primary text
MIST = "#8b949e"             # 潮 Tide — secondary text, seafoam grey
SHADOW = "#6e7681"           # 陰 Undertow — subtle UI chrome
VOID = "#30363d"             # 淵 Abyss — deep structural accents

# ━━━ Accent Palette — Bioluminescence ━━━
# The cold glow of deep-sea creatures
CYAN = "#58a6ff"             # 発光 Bioluminescent blue — primary accent
CYAN_DIM = "#79c0ff"         # 淡光 Soft glow — hover / secondary accent
TEAL = "#3fb9a2"             # 翡翠 Sea glass — success, life
CORAL = "#f85149"            # 珊瑚 Deep coral — error, danger
AMBER = "#e3b341"            # 琥珀 Amber trapped in resin — warning
PEARL = "#f0f6fc"            # 光 Pure nacre — highlights, focus

# ━━━ Semantic Mapping ━━━
TEXT = INK                   # Primary text — nacre white
TEXT_DIM = MIST              # Secondary text — tide grey
ACCENT = CYAN                # Interactive elements — bioluminescent
ACCENT_DIM = CYAN_DIM        # Softer accent variant
MUTED = SHADOW               # Borders, dividers — undertow
SUCCESS = TEAL               # Success states — sea glass green
ERROR = CORAL                # Error states — deep coral
WARN = AMBER                 # Warning states — amber resin
HIGHLIGHT = PEARL            # Selection, focus — nacre glow

# ━━━ Box Styles — 殻 kara (shell) ━━━
# Structured like the chambers of a nautilus shell
BANNER_BOX = box.HEAVY_HEAD       # Bold header — shell lip
CARD_BOX = box.ROUNDED            # Rounded — organic shell curves
LIST_BOX = box.SIMPLE_HEAD        # Clean separation — shell septa
PANEL_BOX = box.ROUNDED           # Consistent organic feel

# ━━━ Symbols — 深海記号 shinkai kigō ━━━
# Geometric + organic glyphs for the deep
BULLET = "◈"                # Diamond — faceted shell chamber
SEPARATOR = "│"             # Thin bar — shell septum divider
ARROW = "›"                 # Chevron — current direction
PREFIX = "  "               # Two spaces — breathing room

# ━━━ Typography Spacing ━━━
# Ma (間) still respected — negative space gives form
PADDING_COMPACT = (0, 2)    # Tight — inside a shell chamber
PADDING_DEFAULT = (1, 3)    # Balanced — swimming room
PADDING_GENEROUS = (2, 4)   # Spacious — open water

# ━━━ Legacy Support ━━━
PANEL_BORDER = MUTED
TITLE = f"[{TEXT}]"
SUBTITLE = f"[{TEXT_DIM}]"
