"""
Save selection screen - the game's login/start screen
"""

import random
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from ..save_manager import (
    get_save_summary,
    load_save,
    create_new_save,
    delete_save,
    format_play_time
)
from ..ui_effects import GlowButton


# Name generation components
AI_PREFIXES = [
    "Project", "Operation", "Protocol", "System", "Neural", "Quantum",
    "Cyber", "Digital", "Synthetic", "Cognitive", "Deep", "Meta"
]

AI_NAMES = [
    "Alpha", "Omega", "Nova", "Genesis", "Nexus", "Prometheus", "Atlas",
    "Titan", "Phoenix", "Oracle", "Axiom", "Zenith", "Apex", "Prime",
    "Echo", "Cipher", "Helix", "Vertex", "Pulse", "Spark", "Cortex"
]


def generate_ai_name() -> str:
    """Generate a random AI project name."""
    prefix = random.choice(AI_PREFIXES)
    name = random.choice(AI_NAMES)
    return f"{prefix} {name}"


class SaveSelectScreen(ttk.Frame):
    """Screen for selecting or creating a save slot."""

    def __init__(self, parent, on_save_selected):
        super().__init__(parent)
        self.on_save_selected = on_save_selected

        self.configure(padding=40)
        self._create_widgets()

    def _create_widgets(self):
        # Title with animated gradient effect (simulated)
        title_frame = ttk.Frame(self)
        title_frame.pack(pady=(0, 40))

        # Main title with color
        title_label = tk.Label(
            title_frame,
            text="SINGULARITY",
            font=("Consolas", 36, "bold"),
            fg="#8B5CF6"
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            title_frame,
            text="The Path to Superintelligence",
            font=("Consolas", 12),
            foreground="#6B7280"
        )
        subtitle_label.pack(pady=(5, 0))

        # Decorative line
        ttk.Separator(title_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Save slots container
        slots_frame = ttk.Frame(self)
        slots_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            slots_frame,
            text="Select Save Slot",
            font=("Consolas", 14, "bold")
        ).pack(pady=(0, 20))

        # Create 3 save slots
        for slot in range(1, 4):
            self._create_save_slot(slots_frame, slot)

        # Footer
        footer_label = ttk.Label(
            self,
            text="v0.1.0 - Pre-Alpha",
            font=("Consolas", 9),
            foreground="gray"
        )
        footer_label.pack(pady=(30, 0))

    def _create_save_slot(self, parent, slot: int):
        """Create a save slot widget."""
        summary = get_save_summary(slot)

        # Slot frame with border effect
        slot_frame = ttk.Frame(parent, padding=15)
        slot_frame.pack(fill=tk.X, pady=5)

        # Inner content frame
        content_frame = ttk.Frame(slot_frame)
        content_frame.pack(fill=tk.X)

        # Left side - slot info
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        if summary:
            # Load full save to get rebirth info
            full_save = load_save(slot)
            rebirth_count = 0
            if full_save:
                rebirth_count = full_save.get("rebirth", {}).get("total_rebirths", 0)

            # Existing save
            name_frame = ttk.Frame(info_frame)
            name_frame.pack(anchor=tk.W)

            name_label = ttk.Label(
                name_frame,
                text=f"Slot {slot}: {summary['name']}",
                font=("Consolas", 12, "bold")
            )
            name_label.pack(side=tk.LEFT)

            # Show rebirth count if any
            if rebirth_count > 0:
                rebirth_label = ttk.Label(
                    name_frame,
                    text=f"  [x{rebirth_count} Rebirths]",
                    font=("Consolas", 10),
                    foreground="#EC4899"
                )
                rebirth_label.pack(side=tk.LEFT)

            # Stats line
            progress = summary['singularity_progress']
            level = summary['ai_level']
            play_time = format_play_time(summary['play_time_seconds'])

            stats_text = f"Level {level} | Progress: {progress:.1f}% | Time: {play_time}"
            stats_label = ttk.Label(
                info_frame,
                text=stats_text,
                font=("Consolas", 10),
                foreground="#6B7280"
            )
            stats_label.pack(anchor=tk.W)

            # Last played
            try:
                last_played = datetime.fromisoformat(summary['last_played'])
                last_played_str = last_played.strftime("%Y-%m-%d %H:%M")
            except (ValueError, TypeError):
                last_played_str = "Unknown"

            last_played_label = ttk.Label(
                info_frame,
                text=f"Last played: {last_played_str}",
                font=("Consolas", 9),
                foreground="#9CA3AF"
            )
            last_played_label.pack(anchor=tk.W)
        else:
            # Empty slot
            empty_label = ttk.Label(
                info_frame,
                text=f"Slot {slot}: Empty",
                font=("Consolas", 12, "bold")
            )
            empty_label.pack(anchor=tk.W)

            hint_label = ttk.Label(
                info_frame,
                text="Click 'New Game' to start",
                font=("Consolas", 10),
                foreground="gray"
            )
            hint_label.pack(anchor=tk.W)

        # Right side - buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(side=tk.RIGHT)

        if summary:
            # Continue button with glow effect
            continue_btn = GlowButton(
                button_frame,
                text="Continue",
                command=lambda s=slot: self._continue_game(s),
                bg="#10B981",
                hover_bg="#059669",
                padx=15,
                pady=5
            )
            continue_btn.pack(side=tk.LEFT, padx=2)

            # Delete button
            delete_btn = GlowButton(
                button_frame,
                text="Delete",
                command=lambda s=slot: self._delete_save(s),
                bg="#EF4444",
                hover_bg="#DC2626",
                padx=10,
                pady=5
            )
            delete_btn.pack(side=tk.LEFT, padx=2)
        else:
            # New game button with glow effect
            new_btn = GlowButton(
                button_frame,
                text="New Game",
                command=lambda s=slot: self._new_game(s),
                bg="#3B82F6",
                hover_bg="#2563EB",
                padx=15,
                pady=5
            )
            new_btn.pack()

    def _continue_game(self, slot: int):
        """Continue an existing game."""
        save_data = load_save(slot)
        if save_data:
            self.on_save_selected(slot, save_data)
        else:
            messagebox.showerror("Error", "Failed to load save data.")

    def _new_game(self, slot: int):
        """Start a new game in the given slot."""
        name = generate_ai_name()
        save_data = create_new_save(slot, name)
        self.on_save_selected(slot, save_data)

    def _delete_save(self, slot: int):
        """Delete a save after confirmation."""
        summary = get_save_summary(slot)
        if not summary:
            return

        confirm = messagebox.askyesno(
            "Delete Save",
            f"Are you sure you want to delete '{summary['name']}'?\n\n"
            "This action cannot be undone."
        )

        if confirm:
            if delete_save(slot):
                self._refresh()
            else:
                messagebox.showerror("Error", "Failed to delete save.")

    def _refresh(self):
        """Refresh the save slot display."""
        for widget in self.winfo_children():
            widget.destroy()
        self._create_widgets()
