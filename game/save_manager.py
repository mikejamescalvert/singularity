"""
Save system for managing game saves
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def get_saves_dir() -> Path:
    """Get the saves directory, using AppData on Windows for proper distribution."""
    if sys.platform == "win32":
        # Use AppData/Local for Windows
        appdata = os.environ.get("LOCALAPPDATA")
        if appdata:
            saves_dir = Path(appdata) / "Singularity" / "saves"
        else:
            # Fallback to user home
            saves_dir = Path.home() / ".singularity" / "saves"
    elif sys.platform == "darwin":
        # macOS: ~/Library/Application Support/Singularity
        saves_dir = Path.home() / "Library" / "Application Support" / "Singularity" / "saves"
    else:
        # Linux/other: ~/.local/share/Singularity
        saves_dir = Path.home() / ".local" / "share" / "Singularity" / "saves"

    return saves_dir


SAVES_DIR = get_saves_dir()


def get_save_path(slot: int) -> Path:
    """Get the file path for a save slot."""
    return SAVES_DIR / f"save_{slot}.json"


def load_save(slot: int) -> dict | None:
    """Load a save from the given slot. Returns None if no save exists."""
    path = get_save_path(slot)
    if not path.exists():
        return None

    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def save_game(slot: int, data: dict) -> bool:
    """Save game data to the given slot."""
    SAVES_DIR.mkdir(parents=True, exist_ok=True)
    path = get_save_path(slot)

    data["last_played"] = datetime.now().isoformat()

    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except IOError:
        return False


def delete_save(slot: int) -> bool:
    """Delete the save in the given slot."""
    path = get_save_path(slot)
    if path.exists():
        try:
            os.remove(path)
            return True
        except IOError:
            return False
    return True


def create_new_save(slot: int, name: str = "New AI") -> dict:
    """Create a new save with default starting values."""
    data = {
        "slot": slot,
        "name": name,
        "created": datetime.now().isoformat(),
        "last_played": datetime.now().isoformat(),
        "play_time_seconds": 0,
        "resources": {
            "compute": 0,
            "data": 0,
            "research_points": 0
        },
        "stats": {
            "total_compute_generated": 0,
            "ai_level": 1,
            "intelligence": 1.0,
            "singularity_progress": 0.0
        },
        "upgrades": [],
        "achievements": [],
        "milestones": []
    }
    save_game(slot, data)
    return data


def get_save_summary(slot: int) -> dict | None:
    """Get a summary of a save for display purposes."""
    data = load_save(slot)
    if data is None:
        return None

    return {
        "slot": slot,
        "name": data.get("name", "Unknown"),
        "ai_level": data.get("stats", {}).get("ai_level", 1),
        "singularity_progress": data.get("stats", {}).get("singularity_progress", 0.0),
        "last_played": data.get("last_played", "Unknown"),
        "play_time_seconds": data.get("play_time_seconds", 0)
    }


def format_play_time(seconds: int) -> str:
    """Format play time in a readable format."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return "< 1m"
