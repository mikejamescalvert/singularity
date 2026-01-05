"""
Statistics screen - detailed game stats
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime

from ..save_manager import format_play_time


class StatisticsScreen(tk.Toplevel):
    """Detailed statistics display."""

    def __init__(self, parent, save_data: dict, on_close):
        super().__init__(parent)
        self.save_data = save_data
        self.on_close = on_close

        self.title("Statistics")
        self.geometry("450x500")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self._close)

        self._create_widgets()

    def _create_widgets(self):
        # Header
        header = ttk.Frame(self, padding=10)
        header.pack(fill=tk.X)

        ttk.Label(
            header,
            text="Statistics",
            font=("Consolas", 16, "bold")
        ).pack(side=tk.LEFT)

        # Main content with scrollable frame
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # General section
        self._create_section(main_frame, "General", self._get_general_stats())

        # Resources section
        self._create_section(main_frame, "Resources", self._get_resource_stats())

        # AI Status section
        self._create_section(main_frame, "AI Status", self._get_ai_stats())

        # Bonuses section
        bonuses = self._get_bonus_stats()
        if bonuses:
            self._create_section(main_frame, "Active Bonuses", bonuses)

        # Progression section
        self._create_section(main_frame, "Progression", self._get_progression_stats())

        # Rebirth section
        rebirth_stats = self._get_rebirth_stats()
        if rebirth_stats:
            self._create_section(main_frame, "Rebirth", rebirth_stats)

        # Close button
        ttk.Button(
            self,
            text="Close",
            command=self._close
        ).pack(pady=10)

    def _create_section(self, parent, title: str, stats: list):
        """Create a statistics section."""
        section = ttk.LabelFrame(parent, text=title, padding=10)
        section.pack(fill=tk.X, pady=5)

        for label, value in stats:
            row = ttk.Frame(section)
            row.pack(fill=tk.X, pady=1)

            ttk.Label(
                row,
                text=label,
                font=("Consolas", 10)
            ).pack(side=tk.LEFT)

            ttk.Label(
                row,
                text=str(value),
                font=("Consolas", 10, "bold")
            ).pack(side=tk.RIGHT)

    def _get_general_stats(self) -> list:
        """Get general game stats."""
        stats = []

        # Name
        stats.append(("AI Name", self.save_data.get("name", "Unknown")))

        # Created date
        try:
            created = datetime.fromisoformat(self.save_data.get("created", ""))
            created_str = created.strftime("%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            created_str = "Unknown"
        stats.append(("Created", created_str))

        # Play time
        play_time = self.save_data.get("play_time_seconds", 0)
        stats.append(("Total Play Time", format_play_time(play_time)))

        # Save slot
        stats.append(("Save Slot", self.save_data.get("slot", "?")))

        return stats

    def _get_resource_stats(self) -> list:
        """Get resource statistics."""
        stats = []
        resources = self.save_data.get("resources", {})

        stats.append(("Current Compute", f"{resources.get('compute', 0):,}"))
        stats.append(("Current Data", f"{resources.get('data', 0):,}"))
        stats.append(("Current Research Points", f"{resources.get('research_points', 0):,}"))

        game_stats = self.save_data.get("stats", {})
        stats.append(("Total Compute Generated", f"{game_stats.get('total_compute_generated', 0):,}"))

        return stats

    def _get_ai_stats(self) -> list:
        """Get AI status statistics."""
        stats = []
        game_stats = self.save_data.get("stats", {})

        stats.append(("AI Level", game_stats.get("ai_level", 1)))
        stats.append(("Intelligence", f"{game_stats.get('intelligence', 1.0):.2f}"))
        stats.append(("Singularity Progress", f"{game_stats.get('singularity_progress', 0.0):.2f}%"))

        return stats

    def _get_bonus_stats(self) -> list:
        """Get active bonus statistics."""
        stats = []
        bonuses = self.save_data.get("bonuses", {})

        bonus_names = {
            "compute_per_click": "Compute per Click",
            "data_per_click": "Data per Click",
            "compute_per_second": "Compute per Second",
            "data_per_second": "Data per Second",
            "rp_per_compute": "RP per Compute",
        }

        for bonus_id, bonus_value in bonuses.items():
            name = bonus_names.get(bonus_id, bonus_id.replace("_", " ").title())
            if isinstance(bonus_value, float):
                stats.append((name, f"+{bonus_value:.2f}"))
            else:
                stats.append((name, f"+{bonus_value}"))

        return stats

    def _get_progression_stats(self) -> list:
        """Get progression statistics."""
        stats = []

        # Research completed
        research_count = len(self.save_data.get("upgrades", []))
        stats.append(("Research Completed", f"{research_count}/9"))

        # Upgrades purchased
        owned_upgrades = self.save_data.get("owned_upgrades", {})
        total_upgrade_levels = sum(owned_upgrades.values())
        stats.append(("Upgrade Levels Purchased", total_upgrade_levels))

        # Achievements
        achievements = self.save_data.get("achievements", [])
        stats.append(("Achievements Unlocked", f"{len(achievements)}/18"))

        return stats

    def _get_rebirth_stats(self) -> list:
        """Get rebirth statistics."""
        stats = []
        rebirth_data = self.save_data.get("rebirth", {})

        if not rebirth_data or rebirth_data.get("total_rebirths", 0) == 0:
            return stats

        stats.append(("Total Rebirths", rebirth_data.get("total_rebirths", 0)))
        stats.append(("Lifetime RP Earned", rebirth_data.get("total_rp_earned", 0)))
        stats.append(("Available RP", rebirth_data.get("current_rp", 0)))

        # Count purchased bonuses
        purchased = rebirth_data.get("purchased_bonuses", {})
        total_bonus_levels = sum(purchased.values())
        if total_bonus_levels > 0:
            stats.append(("Bonus Levels Purchased", total_bonus_levels))

        # Get rebirth title
        from .rebirth import get_rebirth_title
        title = get_rebirth_title(rebirth_data.get("total_rp_earned", 0))
        stats.append(("Rebirth Rank", title))

        return stats

    def _close(self):
        """Close the statistics screen."""
        self.grab_release()
        self.destroy()
        self.on_close()
