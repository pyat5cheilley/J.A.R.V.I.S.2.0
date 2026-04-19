"""Reminder handler for J.A.R.V.I.S. 2.0

Manages scheduling and retrieval of reminders using a local JSON store.
Integrates with the calendar handler for event-based reminders.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional

REMINDERS_FILE = "DATA/reminders.json"


def load_reminders() -> list[dict]:
    """Load reminders from the local JSON store."""
    if not os.path.exists(REMINDERS_FILE):
        return []
    with open(REMINDERS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_reminders(reminders: list[dict]) -> None:
    """Persist reminders to the local JSON store."""
    os.makedirs(os.path.dirname(REMINDERS_FILE), exist_ok=True)
    with open(REMINDERS_FILE, "w") as f:
        json.dump(reminders, f, indent=2, default=str)


def add_reminder(title: str, remind_at: datetime, notes: str = "") -> dict:
    """Add a new reminder.

    Args:
        title: Short description of the reminder.
        remind_at: When to trigger the reminder.
        notes: Optional additional context.

    Returns:
        The newly created reminder dict.
    """
    reminders = load_reminders()
    reminder = {
        "id": int(datetime.utcnow().timestamp() * 1000),
        "title": title,
        "remind_at": remind_at.isoformat(),
        "notes": notes,
        "done": False,
        "created_at": datetime.utcnow().isoformat(),
    }
    reminders.append(reminder)
    save_reminders(reminders)
    return reminder


def get_due_reminders(within_minutes: int = 10) -> list[dict]:
    """Return reminders due within the next `within_minutes` minutes."""
    reminders = load_reminders()
    now = datetime.utcnow()
    window = now + timedelta(minutes=within_minutes)
    due = []
    for r in reminders:
        if r.get("done"):
            continue
        try:
            remind_at = datetime.fromisoformat(r["remind_at"])
        except (KeyError, ValueError):
            continue
        if now <= remind_at <= window:
            due.append(r)
    return due


def mark_done(reminder_id: int) -> bool:
    """Mark a reminder as completed by its ID.

    Returns True if the reminder was found and updated, False otherwise.
    """
    reminders = load_reminders()
    for r in reminders:
        if r.get("id") == reminder_id:
            r["done"] = True
            r["completed_at"] = datetime.utcnow().isoformat()
            save_reminders(reminders)
            return True
    return False


def delete_reminder(reminder_id: int) -> bool:
    """Delete a reminder by its ID."""
    reminders = load_reminders()
    updated = [r for r in reminders if r.get("id") != reminder_id]
    if len(updated) == len(reminders):
        return False
    save_reminders(updated)
    return True


def summarize_reminders_for_jarvis(within_hours: int = 24) -> str:
    """Return a human-readable summary of upcoming reminders for the AI prompt."""
    reminders = load_reminders()
    now = datetime.utcnow()
    cutoff = now + timedelta(hours=within_hours)
    upcoming = []
    for r in reminders:
        if r.get("done"):
            continue
        try:
            remind_at = datetime.fromisoformat(r["remind_at"])
        except (KeyError, ValueError):
            continue
        if now <= remind_at <= cutoff:
            upcoming.append(r)

    if not upcoming:
        return f"No reminders in the next {within_hours} hour(s)."

    lines = [f"Upcoming reminders (next {within_hours}h):"]
    for r in sorted(upcoming, key=lambda x: x["remind_at"]):
        ts = datetime.fromisoformat(r["remind_at"]).strftime("%Y-%m-%d %H:%M")
        note = f" — {r['notes']}" if r.get("notes") else ""
        lines.append(f"  • [{ts}] {r['title']}{note}")
    return "\n".join(lines)
