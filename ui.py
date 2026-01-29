"""
Hyprland-style UI: card-based, bold accents, no tables.
Gorgeous terminal experience.
"""
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text
from rich import box

console = Console()

# Hyprland palette: cyan glow, magenta accent, dark base
ACCENT = "bright_cyan"
ACCENT_DIM = "cyan"
SECONDARY = "bright_magenta"
TEXT = "white"
TEXT_DIM = "dim white"
MUTED = "bright_black"
SUCCESS = "green"
ERROR = "red"
WARN = "yellow"

# Hyprland/Arch: minimal borders, compact landscape
CARD_BOX = box.ROUNDED
BANNER_BOX = box.DOUBLE
LIST_BOX = box.MINIMAL  # Thin border for compact lists


def banner():
    """Hero banner - Hyprland style."""
    console.print()
    console.print(
        Panel.fit(
            "[bold bright_cyan]▸ NAUTILUS[/]\n[dim bright_black]media engine[/]",
            border_style=ACCENT,
            box=BANNER_BOX,
            padding=(0, 3),
        )
    )
    console.print(Rule(style=ACCENT_DIM, characters="─"))
    console.print()


def _line(index: int, title: str, badge: str, *, max_title: int = 55) -> Text:
    """One compact line:  1  │  Title  ·  TV"""
    t = Text()
    t.append(f"  {index}  ", style=f"bold {ACCENT}")
    t.append("│ ", style=MUTED)
    title_short = (title[: max_title] + "…") if len(title) > max_title else title
    t.append(title_short, style=TEXT)
    t.append("  ", style=TEXT)
    t.append(f"· {badge}", style=f"dim {MUTED}")
    return t


def _line_simple(index: int, label: str, *, max_label: int = 50) -> Text:
    """One compact line:  1  │  Label"""
    t = Text()
    t.append(f"  {index}  ", style=f"bold {ACCENT}")
    t.append("│ ", style=MUTED)
    label_short = (label[: max_label] + "…") if len(label) > max_label else label
    t.append(label_short, style=TEXT)
    return t


def compact_list_results(results, *, title_attr: str = "title", type_attr: str = "type") -> None:
    """Arch/Hyprland landscape: one thin panel, one line per result. No huge cards."""
    lines = []
    for idx, item in enumerate(results, start=1):
        title = getattr(item, title_attr, str(item))
        kind = getattr(item, type_attr, "?")
        badge = "TV" if kind == "tv" else "Movie"
        lines.append(_line(idx, title, badge))
    block = Text("\n").join(lines)
    console.print(
        Panel(
            block,
            title="[dim]results[/]",
            title_align="left",
            border_style=ACCENT_DIM,
            box=LIST_BOX,
            padding=(0, 1),
        )
    )


def compact_list_simple(items, label_key: str = "label") -> None:
    """Compact list: one panel, one line per item (seasons/episodes)."""
    lines = []
    for idx, item in enumerate(items, start=1):
        label = item.get(label_key, item.get("label", str(item))) if isinstance(item, dict) else getattr(item, label_key, str(item))
        lines.append(_line_simple(idx, label))
    block = Text("\n").join(lines)
    console.print(
        Panel(
            block,
            border_style=ACCENT_DIM,
            box=LIST_BOX,
            padding=(0, 1),
        )
    )


def compact_list_history(history: list) -> None:
    """Compact history: one panel, one line per entry."""
    lines = []
    for idx, h in enumerate(history, start=1):
        title = h.get("title", "?")
        typ = h.get("media_type", "movie")
        prog = h.get("position", "00:00:00")
        if typ == "tv":
            st = h.get("season_title") or ""
            et = h.get("episode_title") or ""
            if st or et:
                prog = f"{st} · {et}"
        t = Text()
        t.append(f"  {idx}  ", style=f"bold {ACCENT}")
        t.append("│ ", style=MUTED)
        t.append((title[:45] + "…") if len(title) > 45 else title, style=TEXT)
        t.append("  ", style=TEXT)
        t.append(f"· {typ.upper()}", style=f"dim {MUTED}")
        t.append("  ", style=TEXT)
        t.append(prog, style=TEXT_DIM)
        lines.append(t)
    block = Text("\n").join(lines)
    console.print(
        Panel(
            block,
            title="[dim]continue[/]",
            title_align="left",
            border_style=ACCENT_DIM,
            box=LIST_BOX,
            padding=(0, 1),
        )
    )


def card_row(index: int, title: str, badge: str, *, width: int = 50) -> Panel:
    """Legacy: single card (used only if needed)."""
    return Panel(_line(index, title, badge), box=LIST_BOX, border_style=ACCENT_DIM, padding=(0, 1))


def card_row_simple(index: int, label: str, *, width: int = 45) -> Panel:
    """Legacy: simple card."""
    return Panel(_line_simple(index, label), box=LIST_BOX, border_style=ACCENT_DIM, padding=(0, 1))


def card_row_history(index: int, title: str, typ: str, progress: str, *, width: int = 40) -> Panel:
    """Legacy: history card."""
    t = Text()
    t.append(f"  {index}  ", style=f"bold {ACCENT}")
    t.append("│ ", style=MUTED)
    t.append((title[: width - 15] + "…") if len(title) > width - 15 else title, style=TEXT)
    t.append(f"  · {typ.upper()}\n    ", style=f"dim {MUTED}")
    t.append(progress, style=TEXT_DIM)
    return Panel(t, box=LIST_BOX, border_style=ACCENT_DIM, padding=(0, 1))


def section_title(title: str, subtitle: str = ""):
    """Section header – compact."""
    console.print()
    console.print(f"[bold {ACCENT}]▸[/] [bold {TEXT}]{title}[/]", end="")
    if subtitle:
        console.print(f" [dim {MUTED}]{subtitle}[/]")
    else:
        console.print()
    console.print(Rule(style=MUTED, characters="─"))


def show_cards(items: list, title_key: str, badge_key: str = None, badge_fmt=None):
    """Render list of dicts or items as cards. badge_fmt(item) -> str for badge."""
    for i, item in enumerate(items, start=1):
        if isinstance(item, dict):
            title = item.get(title_key, "?")
            badge = badge_fmt(item) if badge_fmt else (item.get(badge_key, "") if badge_key else "")
        else:
            title = getattr(item, title_key, str(item))
            badge = badge_fmt(item) if badge_fmt else ""
        console.print(card_row(i, title, badge))
        console.print()


def show_simple_cards(items: list, label_key: str):
    """Render list as simple cards (seasons, episodes)."""
    for i, item in enumerate(items, start=1):
        if isinstance(item, dict):
            label = item.get(label_key, item.get("label", "?"))
        else:
            label = getattr(item, label_key, str(item))
        console.print(card_row_simple(i, label))
        console.print()


def show_history_cards(history: list):
    """Render history as compact list (one panel)."""
    compact_list_history(history)


def stream_panel(url: str, tmp_path: str):
    """Glowing panel for stream URL."""
    console.print()
    console.print(Panel.fit(
        f"[bold {ACCENT}]▸ Stream link[/]\n\n[white]{url}[/]\n\n[dim {MUTED}]Copy: {tmp_path}[/]\n[dim {MUTED}]VLC: Media → Open Network Stream (Ctrl+N)[/]",
        border_style=ACCENT,
        box=CARD_BOX,
        padding=(1, 2),
    ))
    console.print()


def prompt_select(prompt_label: str, choices: list) -> str:
    """Styled select prompt."""
    from rich.prompt import IntPrompt
    return IntPrompt.ask(f"[bold {ACCENT}]▸[/] [dim {MUTED}]{prompt_label}[/]", choices=choices, show_choices=False)


def prompt_text(prompt_label: str) -> str:
    """Styled text prompt."""
    from rich.prompt import Prompt
    return Prompt.ask(f"[bold {ACCENT}]▸[/] [dim {MUTED}]{prompt_label}[/]")


def status_msg(msg: str):
    """Return a status context message."""
    return f"[dim {ACCENT}]◐[/] [dim {MUTED}]{msg}[/]"


def ok_msg(msg: str):
    console.print(f"[{SUCCESS}]✓[/] {msg}")


def err_msg(msg: str):
    console.print(f"[{ERROR}]✗[/] {msg}")


def warn_msg(msg: str):
    console.print(f"[{WARN}]![/] {msg}")
