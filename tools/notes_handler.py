"""Notes handler for J.A.R.V.I.S.2.0

Provides functionality to create, read, update, search, and delete
persistent notes stored as a local JSON file.
"""

import json
import os
import uuid
from datetime import datetime
from typing import Optional

NOTES_FILE = os.path.join(os.path.dirname(__file__), "..", "DATA", "notes.json")


def load_notes() -> list[dict]:
    """Load all notes from the JSON store.

    Returns:
        list[dict]: List of note objects, or empty list if file doesn't exist.
    """
    if not os.path.exists(NOTES_FILE):
        return []
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_notes(notes: list[dict]) -> None:
    """Persist notes list to the JSON store.

    Args:
        notes (list[dict]): The full list of note objects to save.
    """
    os.makedirs(os.path.dirname(NOTES_FILE), exist_ok=True)
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)


def add_note(title: str, content: str, tags: Optional[list[str]] = None) -> dict:
    """Create a new note and persist it.

    Args:
        title (str): Short title or subject for the note.
        content (str): Body text of the note.
        tags (list[str], optional): Optional list of tag strings for categorisation.

    Returns:
        dict: The newly created note object.
    """
    notes = load_notes()
    # Using full UUID (not truncated) to avoid ID collisions over time
    note = {
        "id": str(uuid.uuid4()),
        "title": title.strip(),
        "content": content.strip(),
        "tags": [t.lower().strip() for t in (tags or [])],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    notes.append(note)
    save_notes(notes)
    return note


def get_note(note_id: str) -> Optional[dict]:
    """Retrieve a single note by its ID.

    Args:
        note_id (str): The UUID of the note.

    Returns:
        dict | None: The note object, or None if not found.
    """
    return next((n for n in load_notes() if n["id"] == note_id), None)


def update_note(
    note_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> Optional[dict]:
    """Update fields on an existing note.

    Args:
        note_id (str): ID of the note to update.
        title (str, optional): New title, if changing.
        content (str, optional): New body text, if changing.
        tags (list[str], optional): Replacement tag list, if changing.

    Returns:
        dict | None: Updated note, or None if note_id not found.
    """
    notes = load_notes()
    for note in notes:
        if note["id"] == note_id:
            if title is not None:
                note["title"] = title.strip()
            if content is not None:
                note["content"] = content.strip()
            if tags is not None:
                note["tags"] = [t.lower().strip() for t in tags]
            note["updated_at"] = datetime.now().isoformat()
            save_notes(notes)
            return note
    return None
