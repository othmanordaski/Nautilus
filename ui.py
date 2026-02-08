"""
深 淵   A B Y S S
Nautilus — premium terminal experience.

Every screen is a chamber in the shell.
Every interaction is a creature in the deep.
"""
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text
from rich.table import Table
from rich.columns import Columns
from rich.align import Align
import questionary
from questionary import Style
from utils.theme import (
    # Depth strata
    SURFACE, TWILIGHT, MIDNIGHT, ABYSS,
    # Bioluminescent accents
    ELECTRIC, ELECTRIC_DIM, PLANKTON, SEAGLASS, SEAGLASS_DIM,
    FIRECORAL, FIRECORAL_DIM, AMBER, AMBER_DIM, NACRE, ANEMONE,
    # Semantic
    TEXT, TEXT_DIM, ACCENT, ACCENT_DIM, MUTED, SUCCESS, ERROR, WARN, HIGHLIGHT, SPECIAL,
    # Box styles
    BANNER_BOX, CARD_BOX, LIST_BOX, PANEL_BOX, STREAM_BOX,
    # Glyphs
    ARROW, ARROW_BACK, POINTER, BULLET, BULLET_HOLLOW, BULLET_DOT, BULLET_RING,
    SEP, SEP_BAR, SEP_DASH, SHELL, WAVE, DIAMOND,
    PREFIX, PREFIX_DEEP,
    # Spacing
    PADDING_TIGHT, PADDING_COMPACT, PADDING_DEFAULT, PADDING_GENEROUS,
    # Legacy compat
    INK, MIST, SHADOW, SEPARATOR,
)

console = Console()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  QUESTIONARY STYLE — bioluminescent selection
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_selection_style = Style([
    ('qmark', 'fg:#58a6ff bold'),          # Question mark — electric glow
    ('question', 'fg:#e6edf3'),            # Question — surface bright
    ('pointer', 'fg:#58a6ff bold'),        # Arrow pointer — electric
    ('highlighted', 'fg:#79c0ff bold'),    # Hovered item — plankton glow
    ('selected', 'fg:#3fb950 bold'),       # Confirmed — sea glass green
    ('answer', 'fg:#3fb950 bold'),         # Final answer — vivid life
    ('text', 'fg:#8b949e'),               # Normal text — twilight
    ('disabled', 'fg:#484f58'),           # Disabled — midnight
    ('instruction', 'fg:#484f58 italic'),  # Help text — midnight
])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  NAVIGATION CONTEXT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_context = {"breadcrumb": []}


def set_context(title: str):
    """Push a breadcrumb level."""
    if title not in _context["breadcrumb"]:
        _context["breadcrumb"].append(title)


def clear_context():
    """Reset breadcrumb trail."""
    _context["breadcrumb"].clear()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BANNER — the nautilus surfaces
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def banner(show_version: bool = True):
    """
    The opening — a nautilus shell emerging from darkness.
    Layered depth: decorative line → title → subtitle → rule.
    """
    console.print()
    
    # ── Decorative shell motif ──
    motif = Text()
    motif.append("          ", style=TEXT)
    motif.append("─── ", style=MIDNIGHT)
    motif.append(SHELL, style=f"bold {ACCENT}")
    motif.append(" ───", style=MIDNIGHT)
    console.print(motif)
    console.print()
    
    # ── Title — electric bioluminescent ──
    title = Text()
    title.append("      ", style=TEXT)
    title.append("N ", style=f"bold {ACCENT}")
    title.append("A ", style=f"bold {PLANKTON}")
    title.append("U ", style=f"bold {ACCENT}")
    title.append("T ", style=f"bold {PLANKTON}")
    title.append("I ", style=f"bold {ACCENT}")
    title.append("L ", style=f"bold {PLANKTON}")
    title.append("U ", style=f"bold {ACCENT}")
    title.append("S", style=f"bold {PLANKTON}")
    console.print(title)
    
    # ── Subtitle — twilight depth ──
    sub = Text()
    sub.append("        ", style=TEXT)
    sub.append("深 淵", style=TWILIGHT)
    if show_version:
        sub.append(f"  {SEP_BAR}  ", style=MIDNIGHT)
        sub.append("v1.0", style=MIDNIGHT)
    console.print(sub)
    
    console.print()
    console.print(Rule(style=MIDNIGHT, characters="━"))
    console.print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BREADCRUMB — navigation trail
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def breadcrumb():
    """Render: Home › Search › Show Name › Season 1"""
    if not _context["breadcrumb"]:
        return
    
    trail = Text()
    trail.append(f"{PREFIX}", style=TEXT)
    for i, item in enumerate(_context["breadcrumb"]):
        if i > 0:
            trail.append(f" {ARROW} ", style=MIDNIGHT)
        if i == len(_context["breadcrumb"]) - 1:
            trail.append(item, style=f"bold {TEXT}")  # Current = bright
        else:
            trail.append(item, style=TWILIGHT)        # Past = dimmed
    
    console.print(trail)
    console.print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LIST ITEM RENDERERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _badge(label: str, color: str) -> Text:
    """Render a small colored badge: [TV] or [Movie]"""
    t = Text()
    t.append(label, style=f"bold {color}")
    return t


def _line(index: int, title: str, badge: str = "", *, max_title: int = 58) -> Text:
    """
    Rich list entry with visual hierarchy:
      ◆  1   Title text here                         · TV
    """
    t = Text()
    t.append(f"{PREFIX}", style=TEXT)
    t.append(f"{BULLET} ", style=ACCENT)
    
    # Index — electric glow, right-aligned
    idx_str = f"{index}".rjust(2)
    t.append(idx_str, style=f"bold {ACCENT}")
    t.append("   ", style=TEXT)
    
    # Title — surface bright, truncated
    title_short = (title[:max_title] + "…") if len(title) > max_title else title
    t.append(title_short, style=TEXT)
    
    # Badge — twilight, with separator
    if badge:
        t.append(f"  {SEP}  ", style=MIDNIGHT)
        if badge.upper() == "TV":
            t.append(badge, style=f"bold {ANEMONE}")
        elif badge.upper() == "MOVIE":
            t.append(badge, style=f"bold {PLANKTON}")
        else:
            t.append(badge, style=TWILIGHT)
    
    return t


def _line_simple(index: int, label: str, *, max_label: int = 55) -> Text:
    """Simplified entry for seasons/episodes."""
    t = Text()
    t.append(f"{PREFIX}", style=TEXT)
    t.append(f"{BULLET_HOLLOW} ", style=ACCENT_DIM)
    
    idx_str = f"{index}".rjust(2)
    t.append(idx_str, style=f"bold {ACCENT}")
    t.append("   ", style=TEXT)
    
    label_short = (label[:max_label] + "…") if len(label) > max_label else label
    t.append(label_short, style=TEXT)
    
    return t


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  COMPACT LISTS — paneled collections
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def compact_list_results(results, *, title_attr: str = "title", type_attr: str = "type") -> None:
    """Search results in a rounded panel — differentiated badges."""
    if not results:
        return
    
    lines = []
    for idx, item in enumerate(results, start=1):
        title = getattr(item, title_attr, str(item))
        kind = getattr(item, type_attr, "?")
        badge = "TV" if kind == "tv" else "Movie"
        lines.append(_line(idx, title, badge))
    
    block = Text("\n").join(lines)
    
    console.print()
    console.print(Panel(
        block,
        border_style=MUTED,
        box=LIST_BOX,
        padding=PADDING_COMPACT,
        subtitle=Text(f" {len(results)} results ", style=MIDNIGHT),
        subtitle_align="right",
    ))
    console.print()


def compact_list_simple(items, label_key: str = "label") -> None:
    """Seasons/episodes — hollow diamonds, clean."""
    if not items:
        return
    
    lines = []
    for idx, item in enumerate(items, start=1):
        if isinstance(item, dict):
            label = item.get(label_key, item.get("label", str(item)))
        else:
            label = getattr(item, label_key, str(item))
        lines.append(_line_simple(idx, label))
    
    block = Text("\n").join(lines)
    
    console.print()
    console.print(Panel(
        block,
        border_style=MUTED,
        box=LIST_BOX,
        padding=PADDING_COMPACT,
    ))
    console.print()


def compact_list_history(history: list) -> None:
    """Watch history — rich metadata per entry."""
    if not history:
        return
    
    lines = []
    for idx, h in enumerate(history, start=1):
        title = h.get("title", "?")
        typ = h.get("media_type", "movie")
        prog = h.get("position", "00:00:00")
        
        if typ == "tv":
            st = h.get("season_title") or ""
            et = h.get("episode_title") or ""
            if st and et:
                prog = f"{st} {SEP} {et}"
            elif st or et:
                prog = st or et
        
        t = Text()
        t.append(f"{PREFIX}", style=TEXT)
        t.append(f"{BULLET} ", style=ACCENT)
        
        idx_str = f"{idx}".rjust(2)
        t.append(idx_str, style=f"bold {ACCENT}")
        t.append("   ", style=TEXT)
        
        # Title
        title_short = (title[:44] + "…") if len(title) > 44 else title
        t.append(title_short, style=TEXT)
        
        # Type badge
        t.append(f"  {SEP}  ", style=MIDNIGHT)
        if typ == "tv":
            t.append("TV", style=f"bold {ANEMONE}")
        else:
            t.append("MOVIE", style=f"bold {PLANKTON}")
        
        # Progress — only if meaningful
        if prog and prog != "00:00:00":
            t.append(f"  {SEP}  ", style=MIDNIGHT)
            t.append(prog, style=TWILIGHT)
        
        lines.append(t)
    
    block = Text("\n").join(lines)
    
    console.print()
    console.print(Panel(
        block,
        border_style=MUTED,
        box=LIST_BOX,
        padding=PADDING_COMPACT,
        title=Text(f" {DIAMOND} History ", style=f"bold {ACCENT}"),
        title_align="left",
    ))
    console.print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LEGACY CARDS — thin wrappers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def card_row(index: int, title: str, badge: str, *, width: int = 50) -> Panel:
    return Panel(_line(index, title, badge), box=CARD_BOX, border_style=MUTED, padding=PADDING_TIGHT)


def card_row_simple(index: int, label: str, *, width: int = 45) -> Panel:
    return Panel(_line_simple(index, label), box=CARD_BOX, border_style=MUTED, padding=PADDING_TIGHT)


def card_row_history(index: int, title: str, typ: str, progress: str, *, width: int = 40) -> Panel:
    t = Text()
    t.append(f"{PREFIX}{BULLET} ", style=ACCENT)
    idx_str = f"{index}".rjust(2)
    t.append(idx_str, style=f"bold {ACCENT}")
    t.append("   ", style=TEXT)
    title_short = (title[:width - 10] + "…") if len(title) > width - 10 else title
    t.append(title_short, style=TEXT)
    t.append(f"  {SEP}  ", style=MIDNIGHT)
    t.append(typ.upper(), style=f"bold {ANEMONE}" if typ == "tv" else f"bold {PLANKTON}")
    if progress:
        t.append("\n      ", style=TEXT)
        t.append(progress, style=TWILIGHT)
    return Panel(t, box=CARD_BOX, border_style=MUTED, padding=PADDING_TIGHT)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SECTION TITLE — visual divider with hierarchy
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def section_title(title: str, subtitle: str = "", show_breadcrumb: bool = False):
    """
    Section header — accent arrow, bold title, dim subtitle.
    Optional breadcrumb navigation above.
    """
    console.print()
    
    if show_breadcrumb and _context["breadcrumb"]:
        breadcrumb()
    
    header = Text()
    header.append(f"{PREFIX}{POINTER} ", style=f"bold {ACCENT}")
    header.append(title, style=f"bold {TEXT}")
    
    if subtitle:
        header.append(f"  {SEP_BAR}  ", style=MIDNIGHT)
        header.append(subtitle, style=TWILIGHT)
    
    console.print(header)
    console.print(Rule(style=MIDNIGHT, characters="─"))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LEGACY CARD RENDERERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def show_cards(items: list, title_key: str, badge_key: str = None, badge_fmt=None):
    for i, item in enumerate(items, start=1):
        if isinstance(item, dict):
            title = item.get(title_key, "?")
            badge = badge_fmt(item) if badge_fmt else (item.get(badge_key, "") if badge_key else "")
        else:
            title = getattr(item, title_key, str(item))
            badge = badge_fmt(item) if badge_fmt else ""
        console.print(card_row(i, title, badge))


def show_simple_cards(items: list, label_key: str):
    for i, item in enumerate(items, start=1):
        if isinstance(item, dict):
            label = item.get(label_key, item.get("label", "?"))
        else:
            label = getattr(item, label_key, str(item))
        console.print(card_row_simple(i, label))


def show_history_cards(history: list):
    compact_list_history(history)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STREAM PANEL — the prize
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def stream_panel(url: str, tmp_path: str):
    """
    Stream URL display — the extracted treasure.
    Heavy bordered panel with accent title, URL in highlight.
    """
    console.print()
    
    content = Text()
    content.append(f"{DIAMOND} Stream URL\n", style=f"bold {ACCENT}")
    content.append(f"{SEP_DASH * 40}\n\n", style=MIDNIGHT)
    content.append(url, style=f"bold {HIGHLIGHT}")
    content.append("\n\n", style=TEXT)
    content.append(f"Saved to  {SEP}  ", style=TWILIGHT)
    content.append(tmp_path, style=TEXT_DIM)
    content.append("\n\n", style=TEXT)
    content.append(f"VLC  {ARROW}  Media  {ARROW}  Open Network Stream  ", style=TWILIGHT)
    content.append("Ctrl+N", style=f"bold {TEXT}")
    
    console.print(Panel(
        content,
        border_style=ACCENT,
        box=STREAM_BOX,
        padding=PADDING_GENEROUS,
        title=Text(f" {SHELL} Stream Ready ", style=f"bold {ACCENT}"),
        title_align="left",
    ))
    console.print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  INTERACTIVE PROMPTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def prompt_select(prompt_label: str, choices: list) -> str:
    """Arrow key selection for simple choices."""
    try:
        numeric_choices = [int(c) for c in choices]
        is_numeric = True
    except (ValueError, TypeError):
        numeric_choices = choices
        is_numeric = False
    
    selection = await questionary.select(
        f"{POINTER} {prompt_label}",
        choices=[str(c) for c in numeric_choices],
        style=_selection_style,
        use_shortcuts=False,
        use_indicator=True,
        pointer=f" {POINTER}",
        instruction="",
    ).ask_async()
    
    if selection is None:
        raise KeyboardInterrupt
    
    return int(selection) if is_numeric else selection


async def prompt_select_items(prompt_label: str, items: list, format_func, show_help: bool = True, allow_back: bool = False) -> tuple:
    """
    Arrow key selection for rich item lists.
    Returns (index, item) or (None, None) for Go Back.
    """
    if allow_back:
        go_back_marker = "___GO_BACK___"
        display_items = [go_back_marker] + items
    else:
        display_items = items
    
    display_choices = []
    for i, item in enumerate(display_items):
        if allow_back and i == 0:
            display_choices.append(f"  {ARROW_BACK} Go Back")
        else:
            display_choices.append(format_func(i if not allow_back else i, item))
    
    # Help hints — subtle, informative
    if show_help:
        hint = Text()
        hint.append(f"{PREFIX}", style=TEXT)
        hint.append("↑↓", style=f"bold {ACCENT}")
        hint.append(" navigate", style=TWILIGHT)
        hint.append(f"   {SEP}   ", style=MIDNIGHT)
        hint.append("↵", style=f"bold {ACCENT}")
        hint.append(" select", style=TWILIGHT)
        hint.append(f"   {SEP}   ", style=MIDNIGHT)
        hint.append("^C", style=f"bold {FIRECORAL}")
        hint.append(" cancel", style=TWILIGHT)
        console.print(hint)
        console.print()
    
    selection = await questionary.select(
        f"{POINTER} {prompt_label}",
        choices=display_choices,
        style=_selection_style,
        use_shortcuts=False,
        use_indicator=True,
        pointer=f" {POINTER}",
        instruction="",
    ).ask_async()
    
    if selection is None:
        raise KeyboardInterrupt
    
    selected_index = display_choices.index(selection)
    
    if allow_back and selected_index == 0:
        return None, None
    
    actual_index = selected_index if not allow_back else selected_index - 1
    return actual_index, items[actual_index]


async def prompt_text(prompt_label: str) -> str:
    """Text input — clean, focused."""
    result = await questionary.text(
        f"{POINTER} {prompt_label}",
        style=_selection_style,
        instruction="",
    ).ask_async()
    
    if result is None:
        raise KeyboardInterrupt
    
    return result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STATUS MESSAGES — semantic feedback
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def status_msg(msg: str):
    """Loading/progress text for status spinners."""
    return f"[{TWILIGHT}]{msg}[/]"


def ok_msg(msg: str):
    """Success — green dot, bright text."""
    console.print()
    t = Text()
    t.append(f"{PREFIX}{BULLET_DOT} ", style=f"bold {SUCCESS}")
    t.append(msg, style=TEXT)
    console.print(t)


def err_msg(msg: str):
    """Error — red dot, clear message."""
    console.print()
    t = Text()
    t.append(f"{PREFIX}{BULLET_DOT} ", style=f"bold {ERROR}")
    t.append(msg, style=TEXT)
    console.print(t)


def warn_msg(msg: str):
    """Warning — amber dot, informative."""
    console.print()
    t = Text()
    t.append(f"{PREFIX}{BULLET_DOT} ", style=f"bold {WARN}")
    t.append(msg, style=TEXT)
    console.print(t)


def info_msg(msg: str):
    """Informational — blue dot, neutral."""
    console.print()
    t = Text()
    t.append(f"{PREFIX}{BULLET_RING} ", style=ACCENT)
    t.append(msg, style=TEXT_DIM)
    console.print(t)


def footer_hint(hint: str = "Press Ctrl+C to exit"):
    """Subtle footer — barely visible, always helpful."""
    console.print()
    console.print()
    h = Text()
    h.append(f"{PREFIX}", style=TEXT)
    h.append(hint, style=MIDNIGHT)
    console.print(h)

