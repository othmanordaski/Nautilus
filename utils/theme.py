"""
深 淵   A B Y S S
Nautilus — premium terminal design system.

A color architecture built in layers, like the ocean itself:
  Surface    →  where light still reaches (highlights, focus)
  Twilight   →  dimming, mysterious (secondary elements)
  Midnight   →  the deep blue hour (primary UI chrome)
  Abyss      →  total depth (backgrounds, voids)

Accents are living creatures — bioluminescent organisms
that punctuate the darkness with electric purpose.
"""
from rich import box

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DEPTH SYSTEM — four strata of luminance
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Surface (表層 hyōsō) — brightest, for primary content
SURFACE = "#e6edf3"         # Moonlit water surface

# Twilight (薄明 hakumei) — secondary, supporting text
TWILIGHT = "#8b949e"        # Where light fades to blue

# Midnight (深夜 shinya) — chrome, borders, quiet structure
MIDNIGHT = "#484f58"        # The deep blue hour

# Abyss (深淵 shin'en) — voids, backgrounds, absence
ABYSS = "#21262d"           # Where no light reaches

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BIOLUMINESCENCE — living accent colors
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Primary — Electric Jellyfish  (クラゲ kurage)
ELECTRIC = "#58a6ff"        # Primary interactive glow
ELECTRIC_DIM = "#388bfd"    # Deeper state of the same glow

# Secondary — Moonlit Plankton  (プランクトン purankuton)
PLANKTON = "#79c0ff"        # Softer cyan for secondary accent

# Life — Sea Glass  (シーグラス shīgurasu)
SEAGLASS = "#3fb950"        # Success — vivid green life
SEAGLASS_DIM = "#238636"    # Darker success for borders

# Danger — Fire Coral  (ファイアコーラル faia kōraru)
FIRECORAL = "#f85149"       # Error — hot, unmistakable
FIRECORAL_DIM = "#da3633"   # Darker danger for borders

# Caution — Amber Resin  (琥珀 kohaku)
AMBER = "#d29922"           # Warning — trapped light
AMBER_DIM = "#9e6a03"       # Darker amber for borders

# Nacre — Mother of Pearl  (真珠母 shinjubo)
NACRE = "#f0f6fc"           # Pure highlight, maximum contrast

# Lavender — Deep Sea Anemone  (イソギンチャク isoginchaku)
ANEMONE = "#bc8cff"         # Special accent — purple glow

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SEMANTIC MAPPING — purpose-driven aliases
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TEXT = SURFACE               # Primary readable text
TEXT_DIM = TWILIGHT           # Secondary / supporting text
ACCENT = ELECTRIC             # Interactive, clickable, active
ACCENT_DIM = ELECTRIC_DIM    # Interactive pressed/visited
MUTED = MIDNIGHT              # Borders, rules, quiet chrome
SUCCESS = SEAGLASS            # Confirmed, saved, done
ERROR = FIRECORAL             # Failed, broken, stop
WARN = AMBER                  # Attention needed, caution
HIGHLIGHT = NACRE             # Maximum emphasis
SPECIAL = ANEMONE             # Unique / distinct category

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BOX STYLES — 殻 kara (shell architecture)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BANNER_BOX = box.DOUBLE           # Grand entrance — double walls
CARD_BOX = box.ROUNDED            # Organic curves — shell chambers
LIST_BOX = box.ROUNDED            # Consistent rounded for lists
PANEL_BOX = box.ROUNDED           # Uniform organic feel
STREAM_BOX = box.HEAVY            # Emphasis — thick shell lip

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GLYPHS — 深海記号 shinkai kigō
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Navigation
ARROW = "›"                 # Chevron — forward
ARROW_BACK = "‹"            # Chevron — back
POINTER = "▸"               # Selection triangle

# List items
BULLET = "◆"                # Primary — filled diamond
BULLET_HOLLOW = "◇"         # Secondary — hollow diamond
BULLET_DOT = "●"            # Status indicator — filled
BULLET_RING = "○"           # Inactive status — hollow

# Separators
SEP = "·"                   # Inline gentle separator
SEP_BAR = "│"               # Column divider
SEP_DASH = "─"              # Horizontal thin rule

# Decorative
SHELL = "⬡"                 # Nautilus cross-section
WAVE = "〜"                 # Ocean motif
DIAMOND = "◈"               # Faceted precious

# Layout
PREFIX = "  "               # 2-space indent
PREFIX_DEEP = "    "        # 4-space nested

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SPACING — Ma (間) negative space
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PADDING_TIGHT = (0, 1)      # Inline elements
PADDING_COMPACT = (0, 2)    # List items
PADDING_DEFAULT = (1, 3)    # Cards
PADDING_GENEROUS = (1, 4)   # Panels — open water

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LEGACY COMPAT — old names → new system
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INK = TEXT
MIST = TEXT_DIM
SHADOW = MUTED
VOID = ABYSS
SEPARATOR = SEP
PANEL_BORDER = MUTED
TITLE = f"[{TEXT}]"
SUBTITLE = f"[{TEXT_DIM}]"
