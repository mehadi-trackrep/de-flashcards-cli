"""
Firebase Firestore integration for fetching community flashcards.
Requires: pip install firebase-admin
And a service account JSON key or GOOGLE_APPLICATION_CREDENTIALS env var.

Firestore collection structure:
  flashcards/
    {doc_id}/
      topic: "sql"
      question: "What is..."
      answer: "It is..."

Optional: set FIRESTORE_PROJECT_ID environment variable.
"""

import os


def _get_db():
    """Initialize and return Firestore client."""
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        project_id = os.environ.get("FIRESTORE_PROJECT_ID")
        cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

        if not firebase_admin._apps:
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, {"projectId": project_id})
            elif project_id:
                # Use Application Default Credentials
                firebase_admin.initialize_app(options={"projectId": project_id})
            else:
                return None

        return firestore.client()
    except Exception:
        return None


def fetch_cards_from_firestore(topic: str | None = None) -> list[dict]:
    """
    Fetch flashcards from Firestore.
    Optionally filter by topic. Returns list of card dicts.
    """
    db = _get_db()
    if not db:
        return []

    try:
        ref = db.collection("flashcards")
        if topic:
            ref = ref.where("topic", "==", topic.lower())

        docs = ref.stream()
        cards = []
        for doc in docs:
            data = doc.to_dict()
            if "question" in data and "answer" in data and "topic" in data:
                cards.append({
                    "topic": data["topic"],
                    "question": data["question"],
                    "answer": data["answer"],
                    "source": "firestore",
                })
        return cards
    except Exception:
        return []


def push_card_to_firestore(card: dict) -> bool:
    """
    Upload a single flashcard dict to Firestore.
    Returns True on success, False on failure.
    """
    db = _get_db()
    if not db:
        return False

    try:
        db.collection("flashcards").add({
            "topic": card.get("topic", "general"),
            "question": card["question"],
            "answer": card["answer"],
        })
        return True
    except Exception:
        return False
