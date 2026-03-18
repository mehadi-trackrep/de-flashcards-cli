"""
Google Sheets card loader.

Fetches flashcards from a public Google Sheet on first run,
saves them to ~/.de-flashcards-cli/cards.json, and reads
from that local cache on every subsequent run.

Sheet format (first row = header):
  topic | question | answer

To make your sheet fetchable:
  File → Share → Anyone with the link → Viewer
  Then copy the Sheet ID from the URL:
  https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit
"""

import csv
import json
import urllib.request
from io import StringIO
from pathlib import Path

CONFIG_DIR  = Path.home() / ".de-flashcards-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"   # single source of truth
CARDS_CACHE = CONFIG_DIR / "cards.json"

_CSV_URL = "https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


# ─── config.json helpers ───────────────────────────────────────────────────────

def _read_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _write_config(data: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ─── cards.json cache helpers ──────────────────────────────────────────────────

def _read_cache() -> list[dict]:
    if CARDS_CACHE.exists():
        try:
            with open(CARDS_CACHE) as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            pass
    return []


def _write_cache(cards: list[dict]):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CARDS_CACHE, "w") as f:
        json.dump(cards, f, indent=2)


# ─── Public state checks ───────────────────────────────────────────────────────

def is_configured() -> bool:
    """True if a sheet_id has been saved in config.json."""
    return bool(_read_config().get("sheet_id", "").strip())


def cache_exists() -> bool:
    """True if cards.json exists and has at least one card."""
    return len(_read_cache()) > 0


# ─── Sheet config ──────────────────────────────────────────────────────────────

def save_sheet_config(sheet_id: str, gid: str = "0"):
    """Save sheet_id + gid into config.json."""
    cfg = _read_config()
    cfg["sheet_id"] = sheet_id.strip()
    cfg["gid"]      = gid.strip() or "0"
    _write_config(cfg)


# ─── Fetch + parse ─────────────────────────────────────────────────────────────

def _fetch_csv(sheet_id: str, gid: str = "0") -> str:
    url = _CSV_URL.format(sheet_id=sheet_id, gid=gid)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "de-flashcards-cli/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8")
    except Exception as e:
        raise RuntimeError(f"Could not fetch sheet: {e}")


def _parse_csv(raw_csv: str) -> list[dict]:
    reader = csv.DictReader(StringIO(raw_csv))

    if reader.fieldnames is None:
        raise ValueError("Sheet appears to be empty.")

    # Normalise headers: strip + lowercase
    reader.fieldnames = [f.strip().lower() for f in reader.fieldnames]

    required = {"topic", "question", "answer"}
    missing  = required - set(reader.fieldnames)
    if missing:
        raise ValueError(
            f"Sheet is missing columns: {', '.join(sorted(missing))}\n"
            f"  Found:    {', '.join(reader.fieldnames)}\n"
            f"  Required: topic, question, answer"
        )

    cards = []
    for row in reader:
        topic    = row.get("topic",    "").strip().lower()
        question = row.get("question", "").strip()
        answer   = row.get("answer",   "").strip()
        if not topic or not question or not answer:
            continue
        cards.append({
            "topic":    topic,
            "question": question,
            "answer":   answer,
            "source":   "sheets",
        })
    return cards


# ─── Sync (fetch → parse → save cache) ────────────────────────────────────────

def sync_from_sheets(verbose: bool = True) -> list[dict]:
    """
    Fetch from Google Sheets, write to cards.json, return cards.
    Raises RuntimeError on any failure.
    """
    cfg      = _read_config()
    sheet_id = cfg.get("sheet_id", "").strip()
    gid      = cfg.get("gid", "0").strip() or "0"

    if not sheet_id:
        raise RuntimeError(
            "No Google Sheet configured.\n"
            "  Run: de-flashcards-cli config"
        )

    if verbose:
        print("  Fetching cards from Google Sheets...", end=" ", flush=True)

    raw   = _fetch_csv(sheet_id, gid)
    cards = _parse_csv(raw)

    if not cards:
        raise RuntimeError(
            "Sheet fetched but no valid cards found.\n"
            "  Make sure columns are named: topic, question, answer"
        )

    _write_cache(cards)

    if verbose:
        topics = sorted(set(c["topic"] for c in cards))
        print(f"✓  {len(cards)} cards fetched.")
        for t in topics:
            n = sum(1 for c in cards if c["topic"] == t)
            print(f"     {t}: {n} card(s)")
        print(f"  Saved to: {CARDS_CACHE}")

    return cards


# ─── Load (read cache only — no network) ──────────────────────────────────────

def load_cards(topic: str | None = None) -> list[dict]:
    """
    Load cards purely from local cache (cards.json).
    Does NOT fetch from the network — call sync_from_sheets() for that.
    Returns filtered list if topic given, else all cards.
    """
    cards = _read_cache()
    if topic:
        cards = [c for c in cards if c["topic"] == topic.lower()]
    return cards


def get_topics() -> list[str]:
    """Return sorted list of topics from the local cache."""
    return sorted(set(c["topic"] for c in _read_cache()))
