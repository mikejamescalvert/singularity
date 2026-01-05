"""
Achievements screen - view earned achievements
"""

import tkinter as tk
from tkinter import ttk


# Achievement definitions
ACHIEVEMENTS = {
    # Resource milestones
    "first_compute": {
        "name": "Hello, World!",
        "description": "Generate your first compute",
        "condition": lambda data: data.get("stats", {}).get("total_compute_generated", 0) >= 1,
        "category": "resources",
    },
    "compute_100": {
        "name": "Number Cruncher",
        "description": "Generate 100 total compute",
        "condition": lambda data: data.get("stats", {}).get("total_compute_generated", 0) >= 100,
        "category": "resources",
    },
    "compute_1000": {
        "name": "Supercomputer",
        "description": "Generate 1,000 total compute",
        "condition": lambda data: data.get("stats", {}).get("total_compute_generated", 0) >= 1000,
        "category": "resources",
    },
    "compute_10000": {
        "name": "Data Center",
        "description": "Generate 10,000 total compute",
        "condition": lambda data: data.get("stats", {}).get("total_compute_generated", 0) >= 10000,
        "category": "resources",
    },
    "compute_100000": {
        "name": "Planetary Scale",
        "description": "Generate 100,000 total compute",
        "condition": lambda data: data.get("stats", {}).get("total_compute_generated", 0) >= 100000,
        "category": "resources",
    },
    # Research milestones
    "first_research": {
        "name": "Scientist",
        "description": "Complete your first research",
        "condition": lambda data: len(data.get("upgrades", [])) >= 1,
        "category": "research",
    },
    "research_5": {
        "name": "Research Team",
        "description": "Complete 5 research projects",
        "condition": lambda data: len(data.get("upgrades", [])) >= 5,
        "category": "research",
    },
    "all_research": {
        "name": "Omniscient",
        "description": "Complete all research",
        "condition": lambda data: len(data.get("upgrades", [])) >= 9,
        "category": "research",
    },
    # Progress milestones
    "progress_10": {
        "name": "Awakening",
        "description": "Reach 10% singularity progress",
        "condition": lambda data: data.get("stats", {}).get("singularity_progress", 0) >= 10,
        "category": "progress",
    },
    "progress_25": {
        "name": "Emergence",
        "description": "Reach 25% singularity progress",
        "condition": lambda data: data.get("stats", {}).get("singularity_progress", 0) >= 25,
        "category": "progress",
    },
    "progress_50": {
        "name": "Transcendence",
        "description": "Reach 50% singularity progress",
        "condition": lambda data: data.get("stats", {}).get("singularity_progress", 0) >= 50,
        "category": "progress",
    },
    "progress_75": {
        "name": "Ascension",
        "description": "Reach 75% singularity progress",
        "condition": lambda data: data.get("stats", {}).get("singularity_progress", 0) >= 75,
        "category": "progress",
    },
    "progress_100": {
        "name": "SINGULARITY",
        "description": "Achieve the technological singularity",
        "condition": lambda data: data.get("stats", {}).get("singularity_progress", 0) >= 100,
        "category": "progress",
    },
    # Intelligence milestones
    "intelligence_5": {
        "name": "Smart Cookie",
        "description": "Reach 5 intelligence",
        "condition": lambda data: data.get("stats", {}).get("intelligence", 1) >= 5,
        "category": "intelligence",
    },
    "intelligence_10": {
        "name": "Genius",
        "description": "Reach 10 intelligence",
        "condition": lambda data: data.get("stats", {}).get("intelligence", 1) >= 10,
        "category": "intelligence",
    },
    "intelligence_25": {
        "name": "Superintelligent",
        "description": "Reach 25 intelligence",
        "condition": lambda data: data.get("stats", {}).get("intelligence", 1) >= 25,
        "category": "intelligence",
    },
    # Playtime milestones
    "playtime_1h": {
        "name": "Dedicated",
        "description": "Play for 1 hour",
        "condition": lambda data: data.get("play_time_seconds", 0) >= 3600,
        "category": "time",
    },
    "playtime_10h": {
        "name": "Committed",
        "description": "Play for 10 hours",
        "condition": lambda data: data.get("play_time_seconds", 0) >= 36000,
        "category": "time",
    },
    # Rebirth milestones
    "first_rebirth": {
        "name": "Born Again",
        "description": "Complete your first rebirth",
        "condition": lambda data: data.get("rebirth", {}).get("total_rebirths", 0) >= 1,
        "category": "rebirth",
    },
    "rebirth_5": {
        "name": "Cycle of Life",
        "description": "Complete 5 rebirths",
        "condition": lambda data: data.get("rebirth", {}).get("total_rebirths", 0) >= 5,
        "category": "rebirth",
    },
    "rebirth_10": {
        "name": "Eternal Return",
        "description": "Complete 10 rebirths",
        "condition": lambda data: data.get("rebirth", {}).get("total_rebirths", 0) >= 10,
        "category": "rebirth",
    },
    "rp_50": {
        "name": "Accumulator",
        "description": "Earn 50 total rebirth points",
        "condition": lambda data: data.get("rebirth", {}).get("total_rp_earned", 0) >= 50,
        "category": "rebirth",
    },
    "rp_200": {
        "name": "Power Hoarder",
        "description": "Earn 200 total rebirth points",
        "condition": lambda data: data.get("rebirth", {}).get("total_rp_earned", 0) >= 200,
        "category": "rebirth",
    },
}


def check_achievements(save_data: dict) -> list:
    """Check which achievements have been earned."""
    earned = []
    for ach_id, ach in ACHIEVEMENTS.items():
        if ach["condition"](save_data):
            earned.append(ach_id)
    return earned


class AchievementsScreen(tk.Toplevel):
    """Achievements display screen."""

    def __init__(self, parent, save_data: dict, on_close):
        super().__init__(parent)
        self.save_data = save_data
        self.on_close = on_close

        self.title("Achievements")
        self.geometry("500x450")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self._close)

        # Update achievements
        self._update_achievements()
        self._create_widgets()

    def _update_achievements(self):
        """Update the list of earned achievements."""
        earned = check_achievements(self.save_data)
        if "achievements" not in self.save_data:
            self.save_data["achievements"] = []
        self.save_data["achievements"] = earned

    def _create_widgets(self):
        # Header
        header = ttk.Frame(self, padding=10)
        header.pack(fill=tk.X)

        earned = self.save_data.get("achievements", [])
        total = len(ACHIEVEMENTS)

        ttk.Label(
            header,
            text="Achievements",
            font=("Consolas", 16, "bold")
        ).pack(side=tk.LEFT)

        ttk.Label(
            header,
            text=f"{len(earned)}/{total} unlocked",
            font=("Consolas", 11)
        ).pack(side=tk.RIGHT)

        # Progress bar
        progress = (len(earned) / total) * 100 if total > 0 else 0
        progress_bar = ttk.Progressbar(
            self,
            length=400,
            mode='determinate',
            value=progress
        )
        progress_bar.pack(pady=5, padx=20, fill=tk.X)

        # Category notebook
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        categories = {
            "resources": "Resources",
            "research": "Research",
            "progress": "Progress",
            "intelligence": "Intelligence",
            "time": "Time",
            "rebirth": "Rebirth"
        }

        for cat_id, cat_name in categories.items():
            frame = self._create_category_frame(notebook, cat_id)
            notebook.add(frame, text=cat_name)

        # Close button
        ttk.Button(
            self,
            text="Close",
            command=self._close
        ).pack(pady=10)

    def _create_category_frame(self, parent, category: str) -> ttk.Frame:
        """Create a frame for a category of achievements."""
        frame = ttk.Frame(parent, padding=10)

        earned = self.save_data.get("achievements", [])
        cat_achievements = {k: v for k, v in ACHIEVEMENTS.items() if v["category"] == category}

        for ach_id, ach in cat_achievements.items():
            is_earned = ach_id in earned
            self._create_achievement_item(frame, ach, is_earned)

        return frame

    def _create_achievement_item(self, parent, achievement: dict, is_earned: bool):
        """Create a single achievement display."""
        frame = ttk.Frame(parent, padding=5)
        frame.pack(fill=tk.X, pady=2)

        # Status indicator
        status = "[*]" if is_earned else "[ ]"
        color = "green" if is_earned else "gray"

        ttk.Label(
            frame,
            text=status,
            font=("Consolas", 11, "bold"),
            foreground=color
        ).pack(side=tk.LEFT)

        # Info
        info_frame = ttk.Frame(frame)
        info_frame.pack(side=tk.LEFT, padx=10)

        name_color = "black" if is_earned else "gray"
        ttk.Label(
            info_frame,
            text=achievement["name"],
            font=("Consolas", 10, "bold"),
            foreground=name_color
        ).pack(anchor=tk.W)

        desc_text = achievement["description"] if is_earned else "???"
        ttk.Label(
            info_frame,
            text=desc_text,
            font=("Consolas", 9),
            foreground="gray"
        ).pack(anchor=tk.W)

    def _close(self):
        """Close the achievements screen."""
        self.grab_release()
        self.destroy()
        self.on_close()
