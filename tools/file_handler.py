"""File handler for J.A.R.V.I.S.2.0 — read, write, summarize, and list local files."""

import os
import json
import datetime
from pathlib import Path

# Base directory for user-accessible files (relative to project root)
FILES_DIR = Path("DATA/FILES")
FILES_DIR.mkdir(parents=True, exist_ok=True)


def _resolve_path(filename: str) -> Path:
    """Resolve a filename to a safe path inside FILES_DIR."""
    # Prevent directory traversal attacks
    safe_name = Path(filename).name
    return FILES_DIR / safe_name


def list_files(extension: str = None) -> list[dict]:
    """
    List all files in the FILES_DIR.

    Args:
        extension: Optional filter, e.g. '.txt', '.md'

    Returns:
        List of dicts with name, size (bytes), and modified timestamp.
    """
    results = []
    for entry in sorted(FILES_DIR.iterdir()):
        if not entry.is_file():
            continue
        if extension and entry.suffix.lower() != extension.lower():
            continue
        stat = entry.stat()
        results.append({
            "name": entry.name,
            "size_bytes": stat.st_size,
            "modified": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        })
    return results


def read_file(filename: str) -> str:
    """
    Read the contents of a text file.

    Args:
        filename: Name of the file inside FILES_DIR.

    Returns:
        File contents as a string, or an error message.
    """
    path = _resolve_path(filename)
    if not path.exists():
        return f"Error: File '{filename}' not found."
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        return f"Error reading file: {exc}"


def write_file(filename: str, content: str, overwrite: bool = False) -> dict:
    """
    Write content to a file inside FILES_DIR.

    Args:
        filename: Target filename.
        content: Text content to write.
        overwrite: If False and file exists, return an error.

    Returns:
        Dict with 'success' bool and 'message' string.
    """
    path = _resolve_path(filename)
    if path.exists() and not overwrite:
        return {"success": False, "message": f"File '{filename}' already exists. Use overwrite=True to replace it."}
    try:
        path.write_text(content, encoding="utf-8")
        return {"success": True, "message": f"File '{filename}' saved ({len(content)} characters)."}
    except Exception as exc:
        return {"success": False, "message": f"Error writing file: {exc}"}


def append_to_file(filename: str, content: str) -> dict:
    """
    Append text to an existing file (or create it if absent).

    Args:
        filename: Target filename.
        content: Text to append.

    Returns:
        Dict with 'success' bool and 'message' string.
    """
    path = _resolve_path(filename)
    try:
        with path.open("a", encoding="utf-8") as fh:
            fh.write(content)
        return {"success": True, "message": f"Appended {len(content)} characters to '{filename}'."}
    except Exception as exc:
        return {"success": False, "message": f"Error appending to file: {exc}"}


def delete_file(filename: str) -> dict:
    """
    Delete a file from FILES_DIR.

    Args:
        filename: Name of the file to delete.

    Returns:
        Dict with 'success' bool and 'message' string.
    """
    path = _resolve_path(filename)
    if not path.exists():
        return {"success": False, "message": f"File '{filename}' not found."}
    try:
        path.unlink()
        return {"success": True, "message": f"File '{filename}' deleted."}
    except Exception as exc:
        return {"success": False, "message": f"Error deleting file: {exc}"}


def get_file_info(filename: str) -> dict:
    """
    Return metadata about a single file.

    Args:
        filename: Name of the file.

    Returns:
        Dict with file metadata or an error message.
    """
    path = _resolve_path(filename)
    if not path.exists():
        return {"error": f"File '{filename}' not found."}
    stat = path.stat()
    return {
        "name": path.name,
        "extension": path.suffix,
        "size_bytes": stat.st_size,
        "created": datetime.datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
        "modified": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "path": str(path.resolve()),
    }
