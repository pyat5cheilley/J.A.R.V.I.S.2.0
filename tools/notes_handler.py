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
    note = {
        "id": str(uuid.uuid4())[:8],
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
        note_id (str): The short UUID of the note.

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


def delete_note(note_id: str) -> bool:
    """Delete a note by ID.

    Args:
        note_id (str): ID of the note to remove.

    Returns:
        bool: True if the note was found and deleted, False otherwise.
    """
    notes = load_notes()
    filtered = [n for n in notes if n["id"] != note_id]
    if len(filtered) == len(notes):
        return False
    save_notes(filtered)
    return True


def search_notes(query: str) -> list[dict]:
    """Search notes by keyword across title, content, and tags.

    Args:
        query (str): Search term (case-insensitive).

    Returns:
        list[dict]: Notes whose title, content, or tags contain the query.
    """
    q = query.lower().strip()
    results = []
    for note in load_notes():
        if (
            q in note["title"].lower()
            or q in note["content"].lower()
            or any(q in tag for tag in note["tags"])
        ):
            results.append(note)
    return results


def list_notes(tag_filter: Optional[str] = None) -> list[dict]:
    """List all notes, optionally filtered by tag.

    Args:
        tag_filter (str, optional): If provided, only return notes with this tag.

    Returns:
        list[dict]: Matching notes sorted by creation date (newest first).
    """
    notes = load_notes()
    if tag_filter:
        tf = tag_filter.lower().strip()
        notes = [n for n in notes if tf in n["tags"]]
    return sorted(notes, key=lambda n: n["created_at"], reverse=True)
