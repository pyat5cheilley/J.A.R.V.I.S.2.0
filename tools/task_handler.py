"""Task handler for J.A.R.V.I.S. 2.0 — manages to-do items with priority and status tracking."""

import json
import os
from datetime import datetime
from typing import Optional

TASKS_FILE = os.path.join(os.path.dirname(__file__), "..", "DATA", "tasks.json")


def load_tasks() -> list[dict]:
    """Load tasks from the JSON file. Returns an empty list if file doesn't exist."""
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_tasks(tasks: list[dict]) -> bool:
    """Persist tasks list to disk. Returns True on success."""
    try:
        os.makedirs(os.path.dirname(TASKS_FILE), exist_ok=True)
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"[task_handler] Failed to save tasks: {e}")
        return False


def add_task(
    title: str,
    description: str = "",
    priority: str = "medium",
    due_date: Optional[str] = None,
) -> dict:
    """Add a new task and return it.

    Args:
        title:       Short title for the task.
        description: Optional longer description.
        priority:    One of 'low', 'medium', 'high'.
        due_date:    Optional ISO-format date string (YYYY-MM-DD).
    """
    tasks = load_tasks()
    task_id = (max((t["id"] for t in tasks), default=0)) + 1
    task = {
        "id": task_id,
        "title": title,
        "description": description,
        "priority": priority.lower() if priority.lower() in ("low", "medium", "high") else "medium",
        "due_date": due_date,
        "status": "pending",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "completed_at": None,
    }
    tasks.append(task)
    save_tasks(tasks)
    return task


def complete_task(task_id: int) -> Optional[dict]:
    """Mark a task as completed. Returns the updated task or None if not found."""
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = "completed"
            task["completed_at"] = datetime.now().isoformat(timespec="seconds")
            save_tasks(tasks)
            return task
    return None


def delete_task(task_id: int) -> bool:
    """Remove a task by ID. Returns True if deleted, False if not found."""
    tasks = load_tasks()
    new_tasks = [t for t in tasks if t["id"] != task_id]
    if len(new_tasks) == len(tasks):
        return False
    save_tasks(new_tasks)
    return True


def get_pending_tasks(priority_filter: Optional[str] = None) -> list[dict]:
    """Return all pending tasks, optionally filtered by priority."""
    tasks = load_tasks()
    pending = [t for t in tasks if t["status"] == "pending"]
    if priority_filter:
        pending = [t for t in pending if t["priority"] == priority_filter.lower()]
    # Sort: high → medium → low, then by creation time
    priority_order = {"high": 0, "medium": 1, "low": 2}
    pending.sort(key=lambda t: (priority_order.get(t["priority"], 1), t["created_at"]))
    return pending


def format_tasks_for_display(tasks: list[dict]) -> str:
    """Format a list of tasks into a readable string for JARVIS responses."""
    if not tasks:
        return "No tasks found."
    lines = []
    for t in tasks:
        due = f" | Due: {t['due_date']}" if t.get("due_date") else ""
        status_icon = "✅" if t["status"] == "completed" else "⏳"
        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(t["priority"], "⚪")
        lines.append(
            f"{status_icon} [{t['id']}] {priority_icon} {t['title']}{due}"
        )
        if t.get("description"):
            lines.append(f"     {t['description']}")
    return "\n".join(lines)
