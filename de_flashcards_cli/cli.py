import random
import argparse
import sys

from . import config as cfg
from .flashcards import FLASHCARDS, TOPICS


# ─── Terminal styling (no dependencies) ───────────────────────────────────────

RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
CYAN    = "\033[36m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
MAGENTA = "\033[35m"
RED     = "\033[31m"
BLUE    = "\033[34m"

TOPIC_COLORS = {
    "sql":       CYAN,
    "python":    GREEN,
    "pipeline":  YELLOW,
    "warehouse": MAGENTA,
    "streaming": BLUE,
    "cloud":     "\033[96m",
}

def topic_color(topic: str) -> str:
    return TOPIC_COLORS.get(topic.lower(), CYAN)

def badge(label: str, color: str) -> str:
    return f"{BOLD}{color} {label.upper()} {RESET}"

def rule(char="─", width=62) -> str:
    return char * width


# ─── Banner ───────────────────────────────────────────────────────────────────

def print_banner():
    print(f"""
{BOLD}{CYAN}
  ██████╗ ███████╗    ███████╗██╗      █████╗ ███████╗██╗  ██╗
  ██╔══██╗██╔════╝    ██╔════╝██║     ██╔══██╗██╔════╝██║  ██║
  ██║  ██║█████╗      █████╗  ██║     ███████║███████╗███████║
  ██║  ██║██╔══╝      ██╔══╝  ██║     ██╔══██║╚════██║██╔══██║
  ██████╔╝███████╗    ██║     ███████╗██║  ██║███████║██║  ██║
  ╚═════╝ ╚══════╝    ╚═╝     ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
{RESET}{BOLD}{CYAN}                                                  — MMH{RESET}
{DIM}  Data Engineering Flashcards — sharpen your skills, one card at a time.
{RESET}""")


# ─── Card display ─────────────────────────────────────────────────────────────

def prompt_after_answer() -> bool:
    """
    After revealing an answer, ask the user what to do next.
    ENTER always continues to next card. Only q or Ctrl+C quits.
    """
    hint = f"{DIM}ENTER = next card  •  q = quit{RESET}"

    try:
        resp = input(f"\n  {hint}  ").strip().lower()
    except KeyboardInterrupt:
        return False
    except EOFError:
        return True  # non-interactive — keep going

    if resp in ("q", "quit", "exit"):
        return False
    return True


def print_card(card: dict, index: int = 1) -> bool:
    """
    Display a single flashcard.
    Returns False if the user chose to quit, True to continue.
    """
    tc = topic_color(card["topic"])
    ai_tag = f"  {DIM}✨ AI-generated{RESET}" if card.get("ai_generated") else ""
    fs_tag = f"  {DIM}☁️  Firestore{RESET}"   if card.get("source") == "firestore" else ""
    tag_line = ai_tag or fs_tag

    print(f"\n{rule()}")
    print(f"  {badge(card['topic'], tc)}  {DIM}#{index}{RESET}  {tag_line}")
    print(rule())
    print(f"\n  {BOLD}Q:{RESET} {card['question']}\n")
    print(rule("·"))

    # ── Wait for ENTER to reveal answer ──
    try:
        input(f"  {DIM}Press ENTER to reveal answer...{RESET}  ")
    except (KeyboardInterrupt, EOFError):
        print("\n\n  👋 Goodbye!\n")
        sys.exit(0)

    print(f"\n  {BOLD}{GREEN}A:{RESET} {card['answer']}\n")
    print(rule())

    # ── Ask what to do next ──
    return prompt_after_answer()


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
            print(f"  {DIM}☁️  Loaded {len(fs_cards)} card(s) from Firestore.{RESET}")
            pool.extend(fs_cards)
        else:
            print(f"  {YELLOW}⚠️  Firestore returned no cards. Check your config.{RESET}")

    if use_ai:
        ai_topic = topic or "data engineering"
        print(f"  {DIM}✨ Generating {ai_count} AI card(s) for '{ai_topic}'...{RESET}")
        from .ai_generator import generate_ai_cards
        ai_cards = generate_ai_cards(ai_topic, ai_count)
        if ai_cards:
            pool.extend(ai_cards)
            print(f"  {GREEN}✓  {len(ai_cards)} AI card(s) generated.{RESET}\n")
        else:
            print(f"  {RED}✗  AI generation failed. Is ANTHROPIC_API_KEY set?{RESET}")
            print(f"     Run: {BOLD}de-flashcards-cli config{RESET}\n")

    return pool


# ─── Config wizard ─────────────────────────────────────────────────────────────

def run_config_wizard():
    print(f"\n{BOLD}⚙️  de-flashcards-cli Configuration{RESET}")
    print(rule())
    print("Configure API keys and integrations. Press ENTER to skip any field.\n")

    current_key = cfg.get("anthropic_api_key", "")
    masked = (current_key[:8] + "...") if current_key else "not set"
    print(f"  {CYAN}Anthropic API Key{RESET} (current: {masked})")
    print(f"  {DIM}Get yours at: https://console.anthropic.com{RESET}")
    val = input("  New key: ").strip()
    if val:
        cfg.set_value("anthropic_api_key", val)
        print(f"  {GREEN}✓ Saved.{RESET}")

    print()

    current_proj = cfg.get("firestore_project_id", "")
    print(f"  {CYAN}Firestore Project ID{RESET} (current: {current_proj or 'not set'})")
    print(f"  {DIM}Found in your Firebase console under Project Settings.{RESET}")
    val = input("  Project ID: ").strip()
    if val:
        cfg.set_value("firestore_project_id", val)
        print(f"  {GREEN}✓ Saved.{RESET}")

    print()

    current_cred = cfg.get("google_credentials", "")
    print(f"  {CYAN}Google Service Account JSON path{RESET} (current: {current_cred or 'not set'})")
    print(f"  {DIM}Path to your downloaded Firebase service account key file.{RESET}")
    val = input("  Path: ").strip()
    if val:
        cfg.set_value("google_credentials", val)
        print(f"  {GREEN}✓ Saved.{RESET}")

    print(f"\n{rule()}")
    print(f"  {GREEN}{BOLD}Config saved to ~/.de-flashcards-cli/config.json{RESET}")
    print(f"  Run {BOLD}de-flashcards-cli --help{RESET} to get started.\n")


# ─── Main CLI ──────────────────────────────────────────────────────────────────

def main():
    cfg.apply_to_env()

    parser = argparse.ArgumentParser(
        prog="de-flashcards-cli",
        description="📚 Data Engineering Flashcards — static, AI-generated, or from Firestore.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=f"""Examples:
  de-flashcards-cli                        # 1 random static card
  de-flashcards-cli -n 5                   # 5 random static cards
  de-flashcards-cli -t sql                 # random SQL card
  de-flashcards-cli -t sql --all           # all SQL cards
  de-flashcards-cli --ai                   # 1 AI-generated card (any topic)
  de-flashcards-cli -t pipeline --ai -n 3  # 3 AI cards on pipelines
  de-flashcards-cli --firestore            # pull cards from Firestore
  de-flashcards-cli --list-topics          # show available topics
  de-flashcards-cli config                 # set API keys & project IDs
        """
    )

    parser.add_argument("command",      nargs="?",  help="'config' to set API keys")
    parser.add_argument("--topic", "-t", type=str,  help=f"Filter by topic: {', '.join(TOPICS)}")
    parser.add_argument("--all",   "-a", action="store_true", help="Show all cards")
    parser.add_argument("--count", "-n", type=int, default=1, help="Number of cards (default: 1)")
    parser.add_argument("--ai",          action="store_true", help="Generate card(s) with Claude AI")
    parser.add_argument("--ai-count",    type=int, default=1, help="How many AI cards to generate (default: 1)")
    parser.add_argument("--firestore",   action="store_true", help="Include cards from Firestore")
    parser.add_argument("--list-topics", "-l", action="store_true", help="List available topics")
    parser.add_argument("--no-banner",   action="store_true", help="Skip the ASCII banner")

    args = parser.parse_args()

    if args.command == "config":
        run_config_wizard()
        return

    if not args.no_banner:
        print_banner()

    if args.list_topics:
        print(f"{BOLD}Available topics:{RESET}\n")
        for t in TOPICS:
            count = sum(1 for c in FLASHCARDS if c["topic"] == t)
            color = topic_color(t)
            print(f"  {badge(t, color)}  {DIM}{count} static cards{RESET}")
        print(f"\n  {DIM}Use --ai to generate cards on any topic (e.g., --topic dbt --ai){RESET}\n")
        return

    ai_count = args.ai_count if args.ai else 0
    pool = load_pool(
        topic=args.topic,
        use_ai=args.ai,
        ai_count=ai_count,
        use_firestore=args.firestore,
    )

    if not pool:
        print(f"\n  {RED}No cards found.{RESET}")
        if args.topic:
            print(f"  Topic '{args.topic}' not recognised in static cards.")
            print(f"  Try: {BOLD}de-flashcards-cli --list-topics{RESET}\n")
        sys.exit(1)

    print(f"  {DIM}Press ENTER to flip a card. Type 'q' anytime to quit.{RESET}\n")

    # ── Infinite loop — keeps going until user types q or Ctrl+C ──────────────
    seen   = []   # track shown cards to avoid immediate repeats
    card_n = 0    # running counter for display

    while True:
        # Reshuffle when the whole pool has been seen
        if not seen:
            seen = pool[:]
            random.shuffle(seen)

        card   = seen.pop()
        card_n += 1

        keep_going = print_card(card, index=card_n)
        if not keep_going:
            print(f"\n  👋 {GREEN}Goodbye! Keep learning. 🚀{RESET}\n")
            sys.exit(0)


if __name__ == "__main__":
    main()
