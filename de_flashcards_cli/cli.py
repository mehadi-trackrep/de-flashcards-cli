import random
import argparse
import sys
import shutil

from . import config as cfg
from .flashcards import FLASHCARDS, TOPICS


# ─── Terminal capabilities ─────────────────────────────────────────────────────

def _term_width() -> int:
    return min(shutil.get_terminal_size((80, 24)).columns, 100)

# ANSI codes
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
ITALIC  = "\033[3m"

# Foreground colors
BLACK   = "\033[30m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
WHITE   = "\033[37m"
BWHITE  = "\033[97m"

# Bright foreground
BRED    = "\033[91m"
BGREEN  = "\033[92m"
BYELLOW = "\033[93m"
BBLUE   = "\033[94m"
BMAGENTA= "\033[95m"
BCYAN   = "\033[96m"

# Background colors
BG_BLACK   = "\033[40m"
BG_RED     = "\033[41m"
BG_GREEN   = "\033[42m"
BG_YELLOW  = "\033[43m"
BG_BLUE    = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN    = "\033[46m"
BG_WHITE   = "\033[47m"
BG_BBLACK  = "\033[100m"   # bright black (dark gray)
BG_BRED    = "\033[101m"
BG_BGREEN  = "\033[102m"
BG_BYELLOW = "\033[103m"
BG_BBLUE   = "\033[104m"
BG_BMAGENTA= "\033[105m"
BG_BCYAN   = "\033[106m"
BG_BWHITE  = "\033[107m"

# Per-topic theme: (bg_color, fg_color, accent_color, icon)
TOPIC_THEMES = {
    "sql":       (BG_BLUE,    BWHITE,  BCYAN,    "󰆼 "),
    "python":    (BG_GREEN,   BLACK,   BGREEN,   " "),
    "pipeline":  (BG_YELLOW,  BLACK,   BYELLOW,  "󰙨 "),
    "warehouse": (BG_MAGENTA, BWHITE,  BMAGENTA, "󰋡 "),
    "streaming": (BG_CYAN,    BLACK,   BCYAN,    " "),
    "cloud":     (BG_BBLUE,   BWHITE,  BBLUE,    "󰅟 "),
}

def get_theme(topic: str) -> tuple:
    return TOPIC_THEMES.get(topic.lower(), (BG_BBLACK, BWHITE, BCYAN, "▸ "))

def topic_accent(topic: str) -> str:
    return get_theme(topic)[2]


# ─── Drawing primitives ────────────────────────────────────────────────────────

def _pad(text: str, width: int, align: str = "left") -> str:
    """Pad text to width, ignoring ANSI escape codes in length calc."""
    import re
    visible = re.sub(r'\033\[[0-9;]*m', '', text)
    pad = max(0, width - len(visible))
    if align == "center":
        lp = pad // 2
        return " " * lp + text + " " * (pad - lp)
    elif align == "right":
        return " " * pad + text
    return text + " " * pad

def rule(char: str = "─", width: int = None) -> str:
    w = width or _term_width()
    return f"{DIM}{char * w}{RESET}"

def double_rule(width: int = None) -> str:
    w = width or _term_width()
    return f"{DIM}{'═' * w}{RESET}"

def blank_line():
    print()

def card_top(width: int, color: str) -> str:
    return f"{color}╭{'─' * (width - 2)}╮{RESET}"

def card_mid(width: int, color: str) -> str:
    return f"{color}├{'─' * (width - 2)}┤{RESET}"

def card_bot(width: int, color: str) -> str:
    return f"{color}╰{'─' * (width - 2)}╯{RESET}"

def card_row(content: str, width: int, color: str) -> str:
    inner = width - 4   # 2 for borders + 2 padding
    padded = _pad(content, inner)
    return f"{color}│{RESET} {padded} {color}│{RESET}"


# ─── Banner ────────────────────────────────────────────────────────────────────

def print_banner():
    w = _term_width()
    print()
    print(f"{BOLD}{BCYAN}{'█' * w}{RESET}")
    print()

    # ASCII art lines (centered)
    art = [
        "██████╗ ███████╗    ███████╗██╗      █████╗ ███████╗██╗  ██╗",
        "██╔══██╗██╔════╝    ██╔════╝██║     ██╔══██╗██╔════╝██║  ██║",
        "██║  ██║█████╗      █████╗  ██║     ███████║███████╗███████║",
        "██║  ██║██╔══╝      ██╔══╝  ██║     ██╔══██║╚════██║██╔══██║",
        "██████╔╝███████╗    ██║     ███████╗██║  ██║███████║██║  ██║",
        "╚═════╝ ╚══════╝    ╚═╝     ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝",
    ]
    for line in art:
        pad = max(0, (w - len(line)) // 2)
        print(f"{BOLD}{BCYAN}{' ' * pad}{line}{RESET}")

    # MMH tag — right-aligned
    tag = "— MMH"
    print(f"{BOLD}{DIM}{CYAN}{tag.rjust(w)}{RESET}")
    print()
    subtitle = "Data Engineering Flashcards  ·  sharpen your skills, one card at a time"
    print(f"{DIM}{subtitle.center(w)}{RESET}")
    print()
    print(f"{BOLD}{BCYAN}{'█' * w}{RESET}")
    print()


# ─── Flashcard display ─────────────────────────────────────────────────────────

def wrap_text(text: str, width: int) -> list[str]:
    """Word-wrap text to fit within width."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        if current and len(current) + 1 + len(word) > width:
            lines.append(current)
            current = word
        else:
            current = (current + " " + word).strip()
    if current:
        lines.append(current)
    return lines or [""]


def print_card(card: dict, index: int = 1) -> bool:
    w        = _term_width()
    bg, fg, accent, icon = get_theme(card["topic"])
    topic    = card["topic"].upper()
    ai_note  = f"{DIM}  ✦ AI{RESET}" if card.get("ai_generated") else ""
    fs_note  = f"{DIM}  ☁ cloud{RESET}" if card.get("source") == "firestore" else ""
    src_note = ai_note or fs_note

    inner_w = w - 4  # inside card borders

    # ── Header bar ──────────────────────────────────────────────────────────────
    print()
    print(card_top(w, accent))

    # Topic badge row
    badge     = f"{bg}{fg}{BOLD} {icon}{topic} {RESET}"
    counter   = f"{DIM}#{index}{RESET}"
    badge_row = badge + "  " + counter + src_note
    print(card_row(badge_row, w, accent))

    print(card_mid(w, accent))

    # ── Question ─────────────────────────────────────────────────────────────
    blank = card_row("", w, accent)
    print(blank)

    q_label = f"{BOLD}{BYELLOW}  Q  {RESET}"
    print(card_row(q_label, w, accent))
    print(blank)

    q_lines = wrap_text(card["question"], inner_w - 6)
    for line in q_lines:
        print(card_row(f"  {BYELLOW}▌{RESET}  {BOLD}{BWHITE}{line}{RESET}", w, accent))

    print(blank)
    print(card_bot(w, accent))

    # ── Reveal prompt ────────────────────────────────────────────────────────
    print()
    try:
        input(f"  {DIM}↵  Press ENTER to reveal answer{RESET}  ")
    except (KeyboardInterrupt, EOFError):
        print(f"\n\n  {BMAGENTA}👋  Goodbye! Keep learning.{RESET}\n")
        sys.exit(0)

    # ── Answer ───────────────────────────────────────────────────────────────
    print()
    print(card_top(w, BGREEN))

    a_label = f"{BOLD}{BGREEN}  A  {RESET}"
    print(card_row(a_label, w, BGREEN))
    print(card_row("", w, BGREEN))

    a_lines = wrap_text(card["answer"], inner_w - 6)
    for line in a_lines:
        print(card_row(f"  {BGREEN}▌{RESET}  {RESET}{line}{RESET}", w, BGREEN))

    print(card_row("", w, BGREEN))
    print(card_bot(w, BGREEN))

    # ── Next prompt ──────────────────────────────────────────────────────────
    print()
    hint = (
        f"  {DIM}↵ next card{RESET}"
        f"  {DIM}·{RESET}"
        f"  {BRED}q quit{RESET}"
    )
    try:
        resp = input(hint + "  ").strip().lower()
    except KeyboardInterrupt:
        print(f"\n\n  {BMAGENTA}👋  Goodbye! Keep learning.{RESET}\n")
        sys.exit(0)
    except EOFError:
        return True

    if resp in ("q", "quit", "exit"):
        return False
    return True


# ─── Source loading ────────────────────────────────────────────────────────────

def load_pool(topic: str | None, use_ai: bool, ai_count: int, use_firestore: bool) -> list[dict]:
    pool = []

    static = FLASHCARDS
    if topic:
        static = [c for c in static if c["topic"] == topic.lower()]
    pool.extend(static)

    if use_firestore:
        from .firestore_client import fetch_cards_from_firestore
        fs_cards = fetch_cards_from_firestore(topic)
        if fs_cards:
            print(f"  {DIM}☁  Loaded {len(fs_cards)} card(s) from Firestore.{RESET}")
            pool.extend(fs_cards)
        else:
            print(f"  {BYELLOW}⚠  Firestore returned no cards. Check your config.{RESET}")

    if use_ai:
        ai_topic = topic or "data engineering"
        print(f"  {DIM}✦  Generating {ai_count} AI card(s) for '{ai_topic}'...{RESET}")
        from .ai_generator import generate_ai_cards
        ai_cards = generate_ai_cards(ai_topic, ai_count)
        if ai_cards:
            pool.extend(ai_cards)
            print(f"  {BGREEN}✓  {len(ai_cards)} AI card(s) ready.{RESET}\n")
        else:
            print(f"  {BRED}✗  AI generation failed. Is ANTHROPIC_API_KEY set?{RESET}")
            print(f"     Run: {BOLD}de-flashcards-cli config{RESET}\n")

    return pool


# ─── Config wizard ─────────────────────────────────────────────────────────────

def run_config_wizard():
    w = _term_width()
    print()
    print(double_rule(w))
    print(f"  {BOLD}{BCYAN}⚙  de-flashcards-cli  ·  Configuration{RESET}")
    print(double_rule(w))
    print(f"  {DIM}Press ENTER to skip any field.{RESET}\n")

    current_key = cfg.get("anthropic_api_key", "")
    masked = (current_key[:8] + "...") if current_key else "not set"
    print(f"  {BOLD}{BCYAN}Anthropic API Key{RESET}  {DIM}(current: {masked}){RESET}")
    print(f"  {DIM}→ console.anthropic.com{RESET}")
    val = input("  New key: ").strip()
    if val:
        cfg.set_value("anthropic_api_key", val)
        print(f"  {BGREEN}✓ Saved.{RESET}")

    print()
    current_proj = cfg.get("firestore_project_id", "")
    print(f"  {BOLD}{BCYAN}Firestore Project ID{RESET}  {DIM}(current: {current_proj or 'not set'}){RESET}")
    print(f"  {DIM}→ Firebase Console → Project Settings{RESET}")
    val = input("  Project ID: ").strip()
    if val:
        cfg.set_value("firestore_project_id", val)
        print(f"  {BGREEN}✓ Saved.{RESET}")

    print()
    current_cred = cfg.get("google_credentials", "")
    print(f"  {BOLD}{BCYAN}Service Account JSON path{RESET}  {DIM}(current: {current_cred or 'not set'}){RESET}")
    print(f"  {DIM}→ Firebase → Service Accounts → Generate key{RESET}")
    val = input("  Path: ").strip()
    if val:
        cfg.set_value("google_credentials", val)
        print(f"  {BGREEN}✓ Saved.{RESET}")

    print()
    print(double_rule(w))
    print(f"  {BGREEN}{BOLD}Saved to ~/.de-flashcards-cli/config.json{RESET}")
    print(f"  Run {BOLD}de-flashcards-cli --help{RESET} to get started.\n")


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    cfg.apply_to_env()

    parser = argparse.ArgumentParser(
        prog="de-flashcards-cli",
        description="Data Engineering Flashcards — static, AI-generated, or from Firestore.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""Examples:
  de-flashcards-cli                        # random cards, infinite loop
  de-flashcards-cli -n 3                   # show 3 random cards then stop
  de-flashcards-cli -t sql                 # SQL cards, infinite loop
  de-flashcards-cli -t sql -n 5            # 5 random SQL cards then stop
  de-flashcards-cli --topic pipeline --all # all pipeline cards then stop
  de-flashcards-cli --list-topics          # show all topics
  de-flashcards-cli --ai                   # 1 AI-generated card
  de-flashcards-cli --topic spark --ai --ai-count 3  # 3 AI spark cards
  de-flashcards-cli --firestore            # pull from Firestore
  de-flashcards-cli config                 # set API keys
        """
    )

    parser.add_argument("command",        nargs="?",  help="'config' to set API keys")
    parser.add_argument("--topic", "-t",  type=str,   help=f"Filter by topic: {', '.join(TOPICS)}")
    parser.add_argument("--count", "-n",  type=int,   default=None, help="Show N random cards then stop (default: infinite loop)")
    parser.add_argument("--all",   "-a",  action="store_true", help="Show all cards for the topic then stop")
    parser.add_argument("--ai",           action="store_true", help="Generate card(s) with Claude AI")
    parser.add_argument("--ai-count",     type=int, default=1, help="How many AI cards to generate (default: 1)")
    parser.add_argument("--firestore",    action="store_true", help="Include cards from Firestore")
    parser.add_argument("--list-topics",  "-l", action="store_true", help="List available topics")
    parser.add_argument("--no-banner",    action="store_true", help="Skip the ASCII banner")

    args = parser.parse_args()

    if args.command == "config":
        run_config_wizard()
        return

    if not args.no_banner:
        print_banner()

    if args.list_topics:
        w = _term_width()
        print(f"\n  {BOLD}Available topics{RESET}\n")
        for t in TOPICS:
            count  = sum(1 for c in FLASHCARDS if c["topic"] == t)
            bg, fg, accent, icon = get_theme(t)
            badge  = f"{bg}{fg}{BOLD} {icon}{t.upper()} {RESET}"
            dots   = f"{DIM}{'·' * max(2, 18 - len(t))}{RESET}"
            print(f"  {badge}  {dots}  {DIM}{count} cards{RESET}")
        print(f"\n  {DIM}Tip: use --ai to generate cards on any topic, e.g. --topic dbt --ai{RESET}\n")
        return

    ai_count = args.ai_count if args.ai else 0
    pool = load_pool(
        topic=args.topic,
        use_ai=args.ai,
        ai_count=ai_count,
        use_firestore=args.firestore,
    )

    if not pool:
        print(f"\n  {BRED}No cards found.{RESET}")
        if args.topic:
            print(f"  Topic '{args.topic}' not found.")
            print(f"  Try: {BOLD}de-flashcards-cli --list-topics{RESET}\n")
        sys.exit(1)

    hint_topic = f" [{args.topic}]" if args.topic else ""

    # ── Decide mode: finite vs infinite ──────────────────────────────────────
    if args.all:
        # Show every card in pool once, then done
        cards  = pool[:]
        random.shuffle(cards)
        finite = True
        mode_hint = f"Showing all {len(cards)} card(s){hint_topic}. Type q to quit early."
    elif args.count is not None:
        # Show exactly N random cards, then done
        cards  = random.sample(pool, min(args.count, len(pool)))
        finite = True
        mode_hint = f"Showing {len(cards)} card(s){hint_topic}. Type q to quit early."
    else:
        # Default: infinite shuffle loop
        cards  = None
        finite = False
        mode_hint = f"Loaded {len(pool)} card(s){hint_topic}. Looping forever — q to quit."

    print(f"  {DIM}{mode_hint}{RESET}\n")

    if finite:
        # ── Finite mode: play through the list once ──────────────────────────
        for i, card in enumerate(cards, 1):
            keep_going = print_card(card, index=i)
            if not keep_going:
                print(f"\n  {BMAGENTA}{BOLD}👋  Goodbye! Keep learning. 🚀{RESET}\n")
                sys.exit(0)
        print(f"\n  {BGREEN}{BOLD}✓  All done! Well studied. 🚀{RESET}\n")
    else:
        # ── Infinite mode: shuffle loop ──────────────────────────────────────
        seen   = []
        card_n = 0

        while True:
            if not seen:
                seen = pool[:]
                random.shuffle(seen)
                if card_n > 0:
                    print(f"\n  {DIM}── deck reshuffled ──{RESET}\n")

            card   = seen.pop()
            card_n += 1

            keep_going = print_card(card, index=card_n)
            if not keep_going:
                print(f"\n  {BMAGENTA}{BOLD}👋  Goodbye! Keep learning. 🚀{RESET}\n")
                sys.exit(0)


if __name__ == "__main__":
    main()
