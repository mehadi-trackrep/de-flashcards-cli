"""
AI-powered flashcard generation using the Anthropic API.
Requires ANTHROPIC_API_KEY environment variable to be set.
"""

import os
import json
import re


def generate_ai_card(topic: str) -> dict | None:
    """
    Generate a single flashcard using Claude AI for a given topic.
    Returns a dict with 'topic', 'question', 'answer' or None on failure.
    """
    try:
        import anthropic
    except ImportError:
        return None

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""Generate a single data engineering flashcard about the topic: "{topic}".

Return ONLY a JSON object in this exact format (no markdown, no explanation):
{{
  "question": "A clear, specific technical question about {topic} in data engineering",
  "answer": "A concise but complete answer, 1-3 sentences max"
}}

Make it practical and useful for a data engineer studying for interviews or refreshing knowledge."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = message.content[0].text.strip()

        # Strip markdown code fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        data = json.loads(raw)
        return {
            "topic": topic.lower(),
            "question": data["question"],
            "answer": data["answer"],
            "ai_generated": True,
        }

    except Exception:
        return None


def generate_ai_cards(topic: str, count: int = 3) -> list[dict]:
    """Generate multiple unique AI flashcards for a topic."""
    try:
        import anthropic
    except ImportError:
        return []

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return []

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""Generate {count} unique data engineering flashcards about the topic: "{topic}".

Return ONLY a JSON array in this exact format (no markdown, no explanation):
[
  {{
    "question": "...",
    "answer": "..."
  }}
]

Rules:
- Each question must be distinct and non-overlapping
- Answers should be 1-3 sentences, practical and precise
- Focus on real-world data engineering knowledge"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = message.content[0].text.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        cards = json.loads(raw)
        return [
            {
                "topic": topic.lower(),
                "question": c["question"],
                "answer": c["answer"],
                "ai_generated": True,
            }
            for c in cards
            if "question" in c and "answer" in c
        ]

    except Exception:
        return []
