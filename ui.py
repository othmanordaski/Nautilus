"""
深海 shinkai · the deep
Nautilus deep-ocean UI.

Design principles:
- Ma (間): Negative space gives form to the abyss
- Shinkai (深海): Depth defines hierarchy
- Hakkō (発光): Bioluminescence draws the eye
- Kara (殻): Shell structure organizes information
"""
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text
import questionary
from questionary import Style
from utils.theme import (
    TEXT, TEXT_DIM, ACCENT, ACCENT_DIM, MUTED, 
    SUCCESS, ERROR, WARN, HIGHLIGHT,
    BANNER_BOX, CARD_BOX, LIST_BOX, PANEL_BOX,
    BULLET, SEPARATOR, ARROW, PREFIX,
    PADDING_COMPACT, PADDING_DEFAULT, PADDING_GENEROUS,
    INK, MIST, SHADOW
)

console = Console()

# Questionary style — bioluminescent deep-ocean accents
# Hex colors for prompt_toolkit compatibility
_selection_style = Style([
    ('qmark', 'fg:#58a6ff'),              # Question mark — bioluminescent cyan
    ('question', 'fg:#c9d1d9'),           # Question text — nacre pearl
    ('pointer', 'fg:#58a6ff bold'),       # Selection pointer — bright glow
    ('highlighted', 'fg:#58a6ff bold'),   # Highlighted item — active glow
    ('selected', 'fg:#3fb9a2'),           # Confirmed selection — sea glass
    ('answer', 'fg:#79c0ff bold'),        # Final answer — soft cyan
    ('text', 'fg:#c9d1d9'),               # Normal text — nacre
    ('disabled', 'fg:#6e7681'),           # Disabled items — undertow grey
])

# Context state for breadcrumb navigation
_context = {"breadcrumb": []}


def set_context(title: str):
    """Set breadcrumb context for current view"""
    if title not in _context["breadcrumb"]:
        _context["breadcrumb"].append(title)


def clear_context():
    """Clear breadcrumb navigation"""
    _context["breadcrumb"].clear()


def banner(show_version: bool = True):
    """
    Opening statement — the nautilus surfaces.
    Bioluminescent glow emerging from the deep.
    """
    console.print()
    console.print()
    
    # Ambient glow line
    glow_line = Text()
    glow_line.append("    ─── ", style=SHADOW)
    glow_line.append("⬡", style=ACCENT)
    glow_line.append(" ───", style=SHADOW)
    console.print(glow_line)
    console.print()
    
    # Main title — bright bioluminescent
    title_text = Text()
    title_text.append("        ", style=TEXT)
    title_text.append("N A U T I L U S", style=f"bold {ACCENT}")
    console.print(title_text)
    
    # Tagline — 深海 (deep sea)
    subtitle = Text()
    subtitle.append("          ", style=TEXT)
    subtitle.append("深 海", style=MIST)
    if show_version:
        subtitle.append("  ", style=TEXT)
        subtitle.append(f"{SEPARATOR}  ", style=SHADOW)
        subtitle.append("v1.0", style=SHADOW)
    console.print(subtitle)
    
    console.print()
    console.print(Rule(style=SHADOW, characters="━"))
    console.print()


def breadcrumb():
    """
    Display current navigation path
    Shows: Home → Search → Show Name → Season 1
    """
    if not _context["breadcrumb"]:
        return
    
    crumb = Text()
    crumb.append("  ", style=TEXT)
    for i, item in enumerate(_context["breadcrumb"]):
        if i > 0:
            crumb.append(f"  {ARROW}  ", style=SHADOW)
        crumb.append(item, style=MIST)
    
    console.print(crumb)
    console.print()


def _line(index: int, title: str, badge: str, *, max_title: int = 60) -> Text:
    """
    Single entry line with generous spacing
    Format:  ◦ 1    Title text here    · badge
    """
    t = Text()
    t.append(f"{PREFIX}{BULLET} ", style=SHADOW)
    
    # Index with fixed width for alignment
    idx_str = f"{index}".rjust(2)
    t.append(idx_str, style=f"bold {ACCENT}")
    t.append("    ", style=TEXT)
    
    # Title with truncation
    title_short = (title[: max_title] + "…") if len(title) > max_title else title
    t.append(title_short, style=TEXT)
    
    # Badge with separator
    if badge:
        t.append(f"    {SEPARATOR} ", style=SHADOW)
        t.append(badge, style=MIST)
    
    return t


def _line_simple(index: int, label: str, *, max_label: int = 55) -> Text:
    """
    Simplified line format for episodes/seasons
    Format:  ◦ 1    Label text
    """
    t = Text()
    t.append(f"{PREFIX}{BULLET} ", style=SHADOW)
    
    idx_str = f"{index}".rjust(2)
    t.append(idx_str, style=f"bold {ACCENT}")
    t.append("    ", style=TEXT)
    
    label_short = (label[: max_label] + "…") if len(label) > max_label else label
    t.append(label_short, style=TEXT)
    
    return t


def compact_list_results(results, *, title_attr: str = "title", type_attr: str = "type") -> None:
    """
    Results list - clean, spacious, minimal border
    One panel containing all entries with breathing room
    """
    if not results:
        return
        
    lines = []
    for idx, item in enumerate(results, start=1):
        title = getattr(item, title_attr, str(item))
        kind = getattr(item, type_attr, "?")
        badge = "TV" if kind == "tv" else "Movie"
        lines.append(_line(idx, title, badge))
    
    # Join with empty line for spacing
    block = Text("\n").join(lines)
    
    console.print()
    console.print(
        Panel(
            block,
            border_style=MUTED,
            box=LIST_BOX,
            padding=PADDING_COMPACT,
        )
    )
    console.print()


def compact_list_simple(items, label_key: str = "label") -> None:
    """
    Simple list for seasons/episodes
    Maintains visual consistency with results
    """
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
    console.print(
        Panel(
            block,
            border_style=MUTED,
            box=LIST_BOX,
            padding=PADDING_COMPACT,
        )
    )
    console.print()


def compact_list_history(history: list) -> None:
    """
    History list with progress information
    Shows: title · type · progress/episode
    """
    if not history:
        return
        
    lines = []
    for idx, h in enumerate(history, start=1):
        title = h.get("title", "?")
        typ = h.get("media_type", "movie")
        prog = h.get("position", "00:00:00")
        
        # For TV shows, show season/episode instead of timestamp
        if typ == "tv":
            st = h.get("season_title") or ""
            et = h.get("episode_title") or ""
            if st and et:
                prog = f"{st} {SEPARATOR} {et}"
            elif st or et:
                prog = st or et
        
        t = Text()
        t.append(f"{PREFIX}{BULLET} ", style=SHADOW)
        
        idx_str = f"{idx}".rjust(2)
        t.append(idx_str, style=f"bold {ACCENT}")
        t.append("    ", style=TEXT)
        
        # Title (truncate if needed)
        title_short = (title[:48] + "…") if len(title) > 48 else title
        t.append(title_short, style=TEXT)
        t.append(f"    {SEPARATOR} ", style=SHADOW)
        
        # Type badge
        t.append(typ.upper(), style=MIST)
        
        # Progress/episode info on same line with extra spacing
        if prog and prog != "00:00:00":
            t.append(f"    {SEPARATOR} ", style=SHADOW)
            t.append(prog, style=TEXT_DIM)
        
        lines.append(t)
    
    block = Text("\n").join(lines)
    
    console.print()
    console.print(
        Panel(
            block,
            border_style=MUTED,
            box=LIST_BOX,
            padding=PADDING_COMPACT,
        )
    )
    console.print()


def card_row(index: int, title: str, badge: str, *, width: int = 50) -> Panel:
    """Legacy card support - converted to minimal style"""
    return Panel(
        _line(index, title, badge), 
        box=PANEL_BOX, 
        border_style=MUTED, 
        padding=PADDING_COMPACT
    )


def card_row_simple(index: int, label: str, *, width: int = 45) -> Panel:
    """Legacy simple card support"""
    return Panel(
        _line_simple(index, label), 
        box=PANEL_BOX, 
        border_style=MUTED, 
        padding=PADDING_COMPACT
    )


def card_row_history(index: int, title: str, typ: str, progress: str, *, width: int = 40) -> Panel:
    """Legacy history card - maintained for compatibility"""
    t = Text()
    t.append(f"{PREFIX}{BULLET} ", style=SHADOW)
    
    idx_str = f"{index}".rjust(2)
    t.append(idx_str, style=f"bold {ACCENT}")
    t.append("    ", style=TEXT)
    
    title_short = (title[: width - 10] + "…") if len(title) > width - 10 else title
    t.append(title_short, style=TEXT)
    t.append(f"    {SEPARATOR} ", style=SHADOW)
    t.append(typ.upper(), style=MIST)
    
    if progress:
        t.append("\n      ", style=TEXT)
        t.append(progress, style=TEXT_DIM)
    
    return Panel(t, box=PANEL_BOX, border_style=MUTED, padding=PADDING_COMPACT)


def section_title(title: str, subtitle: str = "", show_breadcrumb: bool = False):
    """
    Section divider - like a breath between movements
    Subtle, spacious, informative
    """
    console.print()
    
    # Optional breadcrumb navigation
    if show_breadcrumb and _context["breadcrumb"]:
        breadcrumb()
    
    # Title with arrow prefix
    title_text = Text()
    title_text.append(f"{PREFIX}{ARROW} ", style=ACCENT)
    title_text.append(title, style=f"bold {TEXT}")
    
    if subtitle:
        title_text.append(f"  {SEPARATOR}  ", style=SHADOW)
        title_text.append(subtitle, style=MIST)
    
    console.print(title_text)
    console.print(Rule(style=SHADOW, characters="━"))


def show_cards(items: list, title_key: str, badge_key: str = None, badge_fmt=None):
    """
    Legacy compatibility: Render items as individual cards
    Note: Prefer compact_list_* functions for modern UI
    """
    for i, item in enumerate(items, start=1):
        if isinstance(item, dict):
            title = item.get(title_key, "?")
            badge = badge_fmt(item) if badge_fmt else (item.get(badge_key, "") if badge_key else "")
        else:
            title = getattr(item, title_key, str(item))
            badge = badge_fmt(item) if badge_fmt else ""
        console.print(card_row(i, title, badge))


def show_simple_cards(items: list, label_key: str):
    """
    Legacy compatibility: Simple cards for lists
    Note: Prefer compact_list_simple for modern UI
    """
    for i, item in enumerate(items, start=1):
        if isinstance(item, dict):
            label = item.get(label_key, item.get("label", "?"))
        else:
            label = getattr(item, label_key, str(item))
        console.print(card_row_simple(i, label))


def show_history_cards(history: list):
    """
    Render history using modern compact list style
    """
    compact_list_history(history)


def stream_panel(url: str, tmp_path: str):
    """
    Stream URL display - clear, accessible, calm
    Provides copy instructions without urgency
    """
    console.print()
    console.print()
    
    content = Text()
    content.append("◈ Stream URL\n\n", style=f"bold {ACCENT}")
    content.append(f"{url}\n\n", style=HIGHLIGHT)
    content.append(f"Saved to: ", style=MIST)
    content.append(f"{tmp_path}\n\n", style=TEXT_DIM)
    content.append("VLC: Media › Open Network Stream (Ctrl+N)", style=MIST)
    
    console.print(
        Panel(
            content,
            border_style=ACCENT,
            box=PANEL_BOX,
            padding=PADDING_DEFAULT,
        )
    )
    console.print()
    console.print()


async def prompt_select(prompt_label: str, choices: list) -> str:
    """
    Arrow key selection - intuitive navigation
    Uses ↑/↓ arrows to select, Enter to confirm
    """
    # Convert choices to integers for display if they're numeric strings
    try:
        numeric_choices = [int(c) for c in choices]
        is_numeric = True
    except (ValueError, TypeError):
        numeric_choices = choices
        is_numeric = False
    
    # Ask with arrow key selection (async version)
    selection = await questionary.select(
        f"{ARROW} {prompt_label}",
        choices=[str(c) for c in numeric_choices],
        style=_selection_style,
        use_shortcuts=False,
        use_indicator=True,
        pointer="→"
    ).ask_async()
    
    # Return the selected value (convert back to int if it was numeric)
    if selection is None:  # User pressed Ctrl+C
        raise KeyboardInterrupt
    
    return int(selection) if is_numeric else selection


async def prompt_select_items(prompt_label: str, items: list, format_func, show_help: bool = True, allow_back: bool = False) -> tuple:
    """
    Arrow key selection for items (results, seasons, episodes)
    Returns (index, selected_item) or (None, None) if user selects Go Back
    format_func: function to format item for display
    allow_back: whether to show "← Go Back" option
    """
    # Add Go Back option at the beginning if requested
    if allow_back:
        go_back_marker = "___GO_BACK___"
        display_items = [go_back_marker] + items
    else:
        display_items = items
    
    # Format items for display - questionary needs plain strings
    display_choices = []
    for i, item in enumerate(display_items):
        if allow_back and i == 0:
            # Format Go Back option as plain string
            display_choices.append("  ← Go Back")
        else:
            actual_index = i if not allow_back else i
            actual_item = item
            display_choices.append(format_func(actual_index, actual_item))
    
    # Show keyboard help hint
    if show_help:
        help_text = Text()
        help_text.append("  ", style=TEXT)
        help_text.append("↑↓ navigate", style=MIST)
        help_text.append(f"  {SEPARATOR}  ", style=SHADOW)
        help_text.append("↵ select", style=MIST)
        help_text.append(f"  {SEPARATOR}  ", style=SHADOW)
        help_text.append("^C cancel", style=MIST)
        console.print(help_text)
        console.print()
    
    # Ask with arrow key selection - no extra spacing
    selection = await questionary.select(
        f"{ARROW} {prompt_label}",
        choices=display_choices,
        style=_selection_style,
        use_shortcuts=False,
        use_indicator=True,
        pointer="→"
    ).ask_async()
    
    if selection is None:  # User pressed Ctrl+C
        raise KeyboardInterrupt
    
    # Find which item was selected
    selected_index = display_choices.index(selection)
    
    # Check if Go Back was selected
    if allow_back and selected_index == 0:
        return None, None
    
    # Adjust index for Go Back offset
    actual_index = selected_index if not allow_back else selected_index - 1
    return actual_index, items[actual_index]


async def prompt_text(prompt_label: str) -> str:
    """
    Text input prompt - welcoming, clear
    """
    result = await questionary.text(
        f"{ARROW} {prompt_label}",
        style=_selection_style
    ).ask_async()
    
    if result is None:  # User pressed Ctrl+C
        raise KeyboardInterrupt
    
    return result


def status_msg(msg: str):
    """
    Status message - unobtrusive, informative
    Returns formatted string for use in status contexts
    """
    return f"[{MIST}]{msg}[/]"


def ok_msg(msg: str):
    """Success message - gentle affirmation"""
    console.print()
    t = Text()
    t.append(f"{PREFIX}{BULLET} ", style=SUCCESS)
    t.append(msg, style=TEXT)
    console.print(t)


def err_msg(msg: str):
    """Error message - clear but not alarming"""
    console.print()
    t = Text()
    t.append(f"{PREFIX}{BULLET} ", style=ERROR)
    t.append(msg, style=TEXT)
    console.print(t)


def warn_msg(msg: str):
    """Warning message - informative, not aggressive"""
    console.print()
    t = Text()
    t.append(f"{PREFIX}{BULLET} ", style=WARN)
    t.append(msg, style=TEXT)
    console.print(t)


def footer_hint(hint: str = "Press Ctrl+C to exit"):
    """
    Subtle footer with helpful information
    Appears at bottom of screen, unobtrusive
    """
    console.print()
    console.print()
    hint_text = Text()
    hint_text.append("  ", style=TEXT)
    hint_text.append(hint, style=SHADOW)
    console.print(hint_text)

